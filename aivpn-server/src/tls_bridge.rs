//! TLS Bridge — TCP/TLS front-end for ShadeVPN's UDP Gateway
//!
//! Accepts incoming TLS connections on TCP port 443, unwraps TLS,
//! decodes length-framed AIVPN packets, and forwards them as UDP
//! datagrams to the local Gateway (0.0.0.0:443 UDP).
//!
//! Responses from the Gateway arrive as UDP datagrams and are
//! framed back into the TLS stream for the client.
//!
//! Architecture:
//! ```text
//! Internet                  Server (same process)
//! ────────                  ──────────────────────
//! Client ──[TLS/TCP:443]──► TlsBridge ──[UDP loopback]──► Gateway
//!        ◄─[TLS/TCP:443]── TlsBridge ◄─[UDP loopback]── Gateway
//! ```
//!
//! DPI sees: normal HTTPS traffic to port 443/TCP
//! Gateway sees: normal AIVPN UDP packets from 127.0.0.1

use std::net::SocketAddr;
use std::path::Path;
use std::sync::Arc;
use std::io;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, UdpSocket};
use tracing::{info, warn, error, debug};

use tokio_rustls::TlsAcceptor;
use tokio_rustls::rustls::ServerConfig;
use tokio_rustls::rustls::pki_types::{CertificateDer, PrivateKeyDer};

use aivpn_common::transport::{frame_packet, FrameDecoder};

/// TLS Bridge configuration
#[derive(Clone)]
pub struct TlsBridgeConfig {
    /// Address to listen on for TLS/TCP connections (default: 0.0.0.0:443)
    pub tls_listen_addr: String,
    /// Address of the UDP gateway to forward packets to (default: 127.0.0.1:443)
    pub gateway_udp_addr: String,
    /// Path to TLS certificate file (PEM format)
    pub tls_cert_path: String,
    /// Path to TLS private key file (PEM format)
    pub tls_key_path: String,
}

impl Default for TlsBridgeConfig {
    fn default() -> Self {
        Self {
            tls_listen_addr: "0.0.0.0:443".to_string(),
            gateway_udp_addr: "127.0.0.1:443".to_string(),
            tls_cert_path: String::new(),
            tls_key_path: String::new(),
        }
    }
}

/// TLS Bridge server
pub struct TlsBridge {
    config: TlsBridgeConfig,
    acceptor: TlsAcceptor,
}

impl TlsBridge {
    /// Create a new TLS bridge from config
    pub fn new(config: TlsBridgeConfig) -> io::Result<Self> {
        let tls_config = load_tls_config(&config.tls_cert_path, &config.tls_key_path)?;
        let acceptor = TlsAcceptor::from(Arc::new(tls_config));

        Ok(Self { config, acceptor })
    }

    /// Run the TLS bridge — listens for connections and bridges them to UDP gateway
    pub async fn run(&self) -> io::Result<()> {
        let listener = TcpListener::bind(&self.config.tls_listen_addr).await?;
        info!(
            "🔒 TLS Bridge listening on {} → forwarding to UDP {}",
            self.config.tls_listen_addr, self.config.gateway_udp_addr
        );

        loop {
            match listener.accept().await {
                Ok((stream, peer_addr)) => {
                    info!("TLS connection from {}", peer_addr);
                    let _ = stream.set_nodelay(true);
                    
                    let acceptor = self.acceptor.clone();
                    let gateway_addr = self.config.gateway_udp_addr.clone();

                    tokio::spawn(async move {
                        match acceptor.accept(stream).await {
                            Ok(tls_stream) => {
                                info!("TLS handshake complete: {}", peer_addr);
                                if let Err(e) = handle_tls_client(tls_stream, peer_addr, &gateway_addr).await {
                                    debug!("TLS client {} disconnected: {}", peer_addr, e);
                                }
                            }
                            Err(e) => {
                                warn!("TLS handshake failed from {}: {}", peer_addr, e);
                            }
                        }
                    });
                }
                Err(e) => {
                    error!("TCP accept error: {}", e);
                }
            }
        }
    }
}

/// Handle a single TLS client — bridge packets between TLS stream and UDP gateway
async fn handle_tls_client(
    tls_stream: tokio_rustls::server::TlsStream<tokio::net::TcpStream>,
    peer_addr: SocketAddr,
    gateway_addr: &str,
) -> io::Result<()> {
    // Create a dedicated UDP socket for this client to talk to the gateway
    // Bind to 0.0.0.0:0 to get an ephemeral port
    let udp_socket = UdpSocket::bind("0.0.0.0:0").await?;
    udp_socket.connect(gateway_addr).await?;

    let local_udp_addr = udp_socket.local_addr()?;
    debug!(
        "Bridge: TLS client {} ↔ UDP {} → gateway {}",
        peer_addr, local_udp_addr, gateway_addr
    );

    let udp_socket = Arc::new(udp_socket);
    let (mut tls_reader, mut tls_writer) = tokio::io::split(tls_stream);

    // Task 1: TLS → UDP (client sends data → forward to gateway)
    let udp_send = udp_socket.clone();
    let tls_to_udp = tokio::spawn(async move {
        let mut decoder = FrameDecoder::new();
        let mut buf = vec![0u8; 4096];

        loop {
            let n = match tls_reader.read(&mut buf).await {
                Ok(0) => {
                    debug!("TLS client closed connection");
                    break;
                }
                Ok(n) => n,
                Err(e) => {
                    debug!("TLS read error: {}", e);
                    break;
                }
            };

            decoder.push(&buf[..n]);

            // Decode all complete frames and forward as UDP
            loop {
                match decoder.next_packet() {
                    Ok(Some(packet)) => {
                        if let Err(e) = udp_send.send(&packet).await {
                            debug!("UDP send error: {}", e);
                            return;
                        }
                    }
                    Ok(None) => break, // Need more data
                    Err(e) => {
                        warn!("Frame decode error from {}: {}", peer_addr, e);
                        return;
                    }
                }
            }
        }
    });

    // Task 2: UDP → TLS (gateway sends responses → forward to client)
    let udp_recv = udp_socket.clone();
    let udp_to_tls = tokio::spawn(async move {
        let mut buf = vec![0u8; 2048];

        loop {
            let n = match udp_recv.recv(&mut buf).await {
                Ok(n) => n,
                Err(e) => {
                    debug!("UDP recv error: {}", e);
                    break;
                }
            };

            // Frame the UDP packet and send over TLS
            let framed = frame_packet(&buf[..n]);
            if let Err(e) = tls_writer.write_all(&framed).await {
                debug!("TLS write error: {}", e);
                break;
            }
            // Flush to prevent buffering delays
            if let Err(e) = tls_writer.flush().await {
                debug!("TLS flush error: {}", e);
                break;
            }
        }
    });

    // Wait for either direction to finish (client disconnect or error)
    tokio::select! {
        _ = tls_to_udp => {},
        _ = udp_to_tls => {},
    }

    info!("TLS client {} disconnected", peer_addr);
    Ok(())
}

/// Load TLS server config from certificate and key files
pub fn load_tls_config(cert_path: &str, key_path: &str) -> io::Result<ServerConfig> {
    // Read certificate chain
    let cert_file = std::fs::File::open(cert_path)
        .map_err(|e| io::Error::new(io::ErrorKind::NotFound, format!("Cannot open cert '{}': {}", cert_path, e)))?;
    let mut cert_reader = io::BufReader::new(cert_file);
    let certs: Vec<CertificateDer<'static>> = rustls_pemfile::certs(&mut cert_reader)
        .collect::<std::result::Result<Vec<_>, _>>()
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, format!("Invalid cert: {}", e)))?;

    if certs.is_empty() {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "No certificates found in cert file"));
    }

    // Read private key
    let key_file = std::fs::File::open(key_path)
        .map_err(|e| io::Error::new(io::ErrorKind::NotFound, format!("Cannot open key '{}': {}", key_path, e)))?;
    let mut key_reader = io::BufReader::new(key_file);
    let key: PrivateKeyDer<'static> = rustls_pemfile::private_key(&mut key_reader)
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, format!("Invalid key: {}", e)))?
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidData, "No private key found in key file"))?;

    // Build TLS 1.3 config (most secure, best performance)
    let config = ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(certs, key)
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, format!("TLS config error: {}", e)))?;

    Ok(config)
}
