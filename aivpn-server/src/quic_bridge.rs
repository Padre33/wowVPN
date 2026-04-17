//! QUIC Bridge — QUIC front-end for ShadeVPN's UDP Gateway
//!
//! Accepts incoming QUIC connections on UDP port 443, unwraps QUIC streams,
//! decodes length-framed AIVPN packets, and forwards them as UDP
//! datagrams to the local Gateway.

use std::net::SocketAddr;
use std::sync::Arc;
use std::io;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::UdpSocket;
use tracing::{info, warn, error, debug};

use quinn::{Endpoint, ServerConfig, Connection};

use crate::tls_bridge::load_tls_config;
use aivpn_common::transport::{frame_packet, FrameDecoder};

/// QUIC Bridge configuration
#[derive(Clone)]
pub struct QuicBridgeConfig {
    pub quic_listen_addr: String,
    pub gateway_udp_addr: String,
    pub tls_cert_path: String,
    pub tls_key_path: String,
}

pub struct QuicBridge {
    config: QuicBridgeConfig,
    endpoint: Endpoint,
}

impl QuicBridge {
    pub fn new(config: QuicBridgeConfig) -> io::Result<Self> {
        let tls_config = load_tls_config(&config.tls_cert_path, &config.tls_key_path)?;
        let quic_server_config = quinn::crypto::rustls::QuicServerConfig::try_from(tls_config)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))?;
        let server_config = ServerConfig::with_crypto(Arc::new(quic_server_config));
        
        let addr: SocketAddr = config.quic_listen_addr.parse().map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))?;
        let endpoint = Endpoint::server(server_config, addr)?;
        
        Ok(Self { config, endpoint })
    }

    pub async fn run(&self) -> io::Result<()> {
        info!(
            "🚀 QUIC Bridge listening on {} → forwarding to UDP {}",
            self.config.quic_listen_addr, self.config.gateway_udp_addr
        );

        while let Some(conn_req) = self.endpoint.accept().await {
            let gateway_addr = self.config.gateway_udp_addr.clone();
            tokio::spawn(async move {
                match conn_req.await {
                    Ok(conn) => {
                        info!("QUIC connection from {}", conn.remote_address());
                        if let Err(e) = handle_quic_client(conn, &gateway_addr).await {
                            debug!("QUIC client {} disconnected: {}", gateway_addr, e);
                        }
                    }
                    Err(e) => warn!("QUIC handshake failed: {}", e),
                }
            });
        }
        Ok(())
    }
}

async fn handle_quic_client(conn: Connection, gateway_addr: &str) -> io::Result<()> {
    let peer_addr = conn.remote_address();
    
    let (mut quic_send, mut quic_recv) = match conn.accept_bi().await {
        Ok(s) => s,
        Err(e) => return Err(io::Error::new(io::ErrorKind::ConnectionAborted, e.to_string())),
    };

    let udp_socket = UdpSocket::bind("0.0.0.0:0").await?;
    udp_socket.connect(gateway_addr).await?;
    let udp_socket = Arc::new(udp_socket);

    let udp_send_sock = udp_socket.clone();
    let quic_to_udp = tokio::spawn(async move {
        let mut decoder = FrameDecoder::new();
        let mut buf = vec![0u8; 8192];
        loop {
            let n = match quic_recv.read(&mut buf).await {
                Ok(Some(n)) => n,
                Ok(None) => break,
                Err(e) => { debug!("QUIC read error: {}", e); break; }
            };
            decoder.push(&buf[..n]);
            loop {
                match decoder.next_packet() {
                    Ok(Some(packet)) => {
                        if udp_send_sock.send(&packet).await.is_err() { return; }
                    }
                    Ok(None) => break,
                    Err(_) => return,
                }
            }
        }
    });

    let udp_recv_sock = udp_socket.clone();
    let udp_to_quic = tokio::spawn(async move {
        let mut buf = vec![0u8; 4096];
        loop {
            let n = match udp_recv_sock.recv(&mut buf).await {
                Ok(n) => n,
                Err(_) => break,
            };
            let framed = frame_packet(&buf[..n]);
            if quic_send.write_all(&framed).await.is_err() { break; }
        }
    });

    tokio::select! {
        _ = quic_to_udp => {},
        _ = udp_to_quic => {},
    }
    
    info!("QUIC client {} disconnected", peer_addr);
    Ok(())
}
