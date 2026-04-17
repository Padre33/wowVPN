//! NAT Forwarder Module
//! 
//! Handles:
//! - TUN device creation
//! - Packet forwarding to internet
//! - NAT masquerading

use std::io;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::io::AsyncWriteExt;
use tracing::{info, warn, debug};

use aivpn_common::error::{Error, Result};

const TUN_MTU: u16 = 1420;

/// NAT Forwarder for routing traffic to internet
/// Uses split reader/writer to avoid mutex starvation
pub struct NatForwarder {
    tun_name: String,
    tun_addr: String,
    tun_netmask: String,
    writer: Option<Arc<Mutex<tun::DeviceWriter>>>,
    writer_taken: Option<Mutex<Option<tun::DeviceWriter>>>,
    reader: Option<Mutex<Option<tun::DeviceReader>>>,
}

impl NatForwarder {
    pub fn new(tun_name: &str, tun_addr: &str, tun_netmask: &str) -> Result<Self> {
        Ok(Self {
            tun_name: tun_name.to_string(),
            tun_addr: tun_addr.to_string(),
            tun_netmask: tun_netmask.to_string(),
            writer: None,
            writer_taken: None,
            reader: None,
        })
    }
    
    /// Create TUN device for NAT
    pub fn create(&mut self) -> Result<()> {
        let mut config = tun::Configuration::default();
        
        config
            .tun_name(&self.tun_name)
            .address(&self.tun_addr)
            .netmask(&self.tun_netmask)
            .mtu(TUN_MTU)
            .up();
        
        #[cfg(target_os = "linux")]
        config.platform_config(|config| {
            config.ensure_root_privileges(true);
        });
        
        let dev = tun::create_as_async(&config)
            .map_err(|e| Error::Io(io::Error::new(io::ErrorKind::Other, e.to_string())))?;
        
        let (writer, reader) = dev.split()
            .map_err(|e| Error::Io(io::Error::new(io::ErrorKind::Other, e.to_string())))?;
        self.writer = None; // Writer accessed via take_writer() for channel-based I/O
        self.writer_taken = Some(Mutex::new(Some(writer)));
        self.reader = Some(Mutex::new(Some(reader)));
        
        info!(
            "Created NAT TUN device: {} ({}/{})",
            self.tun_name,
            self.tun_addr,
            self.tun_netmask
        );
        
        // Enable IP forwarding (Linux)
        #[cfg(target_os = "linux")]
        {
            self.enable_ip_forwarding()?;
            self.setup_iptables()?;
        }
        
        Ok(())
    }
    
    /// Enable IP forwarding on Linux
    #[cfg(target_os = "linux")]
    fn enable_ip_forwarding(&self) -> Result<()> {
        use std::fs::{read_to_string, write};
        
        // Check if already enabled (e.g. inside Docker with host sysctl)
        if let Ok(val) = read_to_string("/proc/sys/net/ipv4/ip_forward") {
            if val.trim() == "1" {
                info!("IPv4 forwarding already enabled");
                return Ok(());
            }
        }
        
        // Try to enable IPv4 forwarding
        write("/proc/sys/net/ipv4/ip_forward", "1")
            .map_err(|e| Error::Io(io::Error::new(
                io::ErrorKind::PermissionDenied,
                format!("Failed to enable IP forwarding: {}", e),
            )))?;
        
        info!("Enabled IPv4 forwarding");
        Ok(())
    }
    
    /// Add an iptables rule only if it doesn't already exist (idempotent).
    /// Replaces -A with -C to check first, then adds only if missing.
    #[cfg(target_os = "linux")]
    fn iptables_add_once(args: &[&str]) {
        use std::process::Command;
        // Build check args: replace first "-A" with "-C"
        let check_args: Vec<&str> = {
            let mut replaced = false;
            args.iter().map(|&s| {
                if s == "-A" && !replaced { replaced = true; "-C" } else { s }
            }).collect()
        };
        let already_exists = Command::new("iptables")
            .args(&check_args)
            .output()
            .map(|o| o.status.success())
            .unwrap_or(false);
        if !already_exists {
            let _ = Command::new("iptables").args(args).output();
        }
    }

    /// Setup iptables rules for NAT (idempotent — safe to call on every restart)
    #[cfg(target_os = "linux")]
    fn setup_iptables(&self) -> Result<()> {
        // NAT masquerading — one rule per subnet, independent of TUN name
        let masq_src = format!("{}/24", self.tun_addr);
        Self::iptables_add_once(&[
            "-t", "nat", "-A", "POSTROUTING",
            "-s", &masq_src, "-j", "MASQUERADE",
        ]);
        info!("iptables MASQUERADE rule ensured");

        // Allow forwarding through this TUN
        Self::iptables_add_once(&[
            "-A", "FORWARD", "-i", &self.tun_name, "-j", "ACCEPT",
        ]);
        Self::iptables_add_once(&[
            "-A", "FORWARD", "-o", &self.tun_name,
            "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT",
        ]);

        // Clamp TCP MSS to avoid PMTU blackholes (download and upload)
        Self::iptables_add_once(&[
            "-t", "mangle", "-A", "FORWARD",
            "-o", &self.tun_name, "-p", "tcp",
            "--tcp-flags", "SYN,RST", "SYN", "-j", "TCPMSS", "--clamp-mss-to-pmtu",
        ]);
        Self::iptables_add_once(&[
            "-t", "mangle", "-A", "FORWARD",
            "-i", &self.tun_name, "-p", "tcp",
            "--tcp-flags", "SYN,RST", "SYN", "-j", "TCPMSS", "--clamp-mss-to-pmtu",
        ]);

        info!("Added iptables MASQUERADE rule");
        Ok(())
    }
    
    /// Forward packet to TUN (write)
    pub async fn forward_packet(&self, packet: &[u8]) -> Result<()> {
        let writer = self.writer.as_ref()
            .ok_or_else(|| Error::Io(io::Error::new(
                io::ErrorKind::NotConnected,
                "TUN device not created",
            )))?;
        
        let mut w = writer.lock().await;
        
        // Linux TUN with IFF_NO_PI (default) expects raw IP packets
        // No flush() — let the OS buffer writes naturally for throughput
        w.write_all(packet).await?;
        
        debug!("Forwarded {} bytes to TUN", packet.len());
        Ok(())
    }
    
    /// Take ownership of the TUN writer (for use in a dedicated writer task)
    pub async fn take_writer(&self) -> Option<tun::DeviceWriter> {
        if let Some(ref lock) = self.writer_taken {
            lock.lock().await.take()
        } else {
            None
        }
    }
    
    /// Take ownership of the TUN reader (for use in a spawned task)
    pub async fn take_reader(&self) -> Option<tun::DeviceReader> {
        if let Some(reader_lock) = &self.reader {
            reader_lock.lock().await.take()
        } else {
            None
        }
    }
    
    /// Get TUN device name
    pub fn tun_name(&self) -> &str {
        &self.tun_name
    }
}

impl Drop for NatForwarder {
    fn drop(&mut self) {
        info!("Cleaning up NAT TUN device: {}", self.tun_name);

        // Cleanup ALL iptables rules added for this TUN device.
        // This runs on graceful shutdown (SIGTERM). On SIGKILL it won't run,
        // but setup_iptables() is now idempotent so duplicates won't accumulate.
        #[cfg(target_os = "linux")]
        {
            use std::process::Command;

            // Remove NAT MASQUERADE
            let _ = Command::new("iptables")
                .args(["-t", "nat", "-D", "POSTROUTING",
                    "-s", &format!("{}/24", self.tun_addr), "-j", "MASQUERADE"])
                .output();

            // Remove FORWARD ACCEPT rules (were missing from Drop before!)
            let _ = Command::new("iptables")
                .args(["-D", "FORWARD", "-i", &self.tun_name, "-j", "ACCEPT"])
                .output();
            let _ = Command::new("iptables")
                .args(["-D", "FORWARD", "-o", &self.tun_name,
                    "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"])
                .output();

            // Remove mangle MSS clamping rules
            let _ = Command::new("iptables")
                .args(["-t", "mangle", "-D", "FORWARD",
                    "-o", &self.tun_name, "-p", "tcp",
                    "--tcp-flags", "SYN,RST", "SYN", "-j", "TCPMSS", "--clamp-mss-to-pmtu"])
                .output();
            let _ = Command::new("iptables")
                .args(["-t", "mangle", "-D", "FORWARD",
                    "-i", &self.tun_name, "-p", "tcp",
                    "--tcp-flags", "SYN,RST", "SYN", "-j", "TCPMSS", "--clamp-mss-to-pmtu"])
                .output();
        }
    }
}
