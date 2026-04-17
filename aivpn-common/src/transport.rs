//! Transport Abstraction Layer
//!
//! Provides TCP framing for AIVPN packets over stream-based transports (TLS/TCP).
//! UDP packets are self-framing (each datagram = one packet).
//! TCP is a byte stream, so we need length-prefix framing:
//!
//!   [2 bytes: packet length (big-endian u16)] [N bytes: AIVPN packet]
//!
//! This allows the receiver to reconstruct individual AIVPN packets
//! from the continuous TLS byte stream.

use crate::error::{Error, Result};

/// Maximum framed packet size (u16 max = 65535, but AIVPN packets are ≤1500)
pub const MAX_FRAMED_PACKET_SIZE: usize = 1500;

/// Frame an AIVPN packet for TCP transport: prepend 2-byte big-endian length
pub fn frame_packet(packet: &[u8]) -> Vec<u8> {
    let len = packet.len() as u16;
    let mut framed = Vec::with_capacity(2 + packet.len());
    framed.extend_from_slice(&len.to_be_bytes());
    framed.extend_from_slice(packet);
    framed
}

/// Read a complete framed packet from a buffer.
///
/// Returns `Ok(Some((packet, bytes_consumed)))` if a full frame was read,
/// `Ok(None)` if the buffer doesn't contain a complete frame yet,
/// or `Err` if the frame is invalid.
pub fn decode_frame(buf: &[u8]) -> Result<Option<(Vec<u8>, usize)>> {
    if buf.len() < 2 {
        return Ok(None); // Need at least 2 bytes for length prefix
    }

    let pkt_len = u16::from_be_bytes([buf[0], buf[1]]) as usize;

    if pkt_len == 0 {
        return Err(Error::InvalidPacket("Zero-length frame"));
    }
    if pkt_len > MAX_FRAMED_PACKET_SIZE {
        return Err(Error::InvalidPacket("Frame exceeds max packet size"));
    }

    let total = 2 + pkt_len;
    if buf.len() < total {
        return Ok(None); // Incomplete frame, need more data
    }

    let packet = buf[2..total].to_vec();
    Ok(Some((packet, total)))
}

/// Streaming frame decoder — accumulates bytes and yields complete packets.
///
/// Usage:
/// ```ignore
/// let mut decoder = FrameDecoder::new();
/// decoder.push(data_from_tls);
/// while let Some(packet) = decoder.next_packet()? {
///     process_aivpn_packet(&packet);
/// }
/// ```
pub struct FrameDecoder {
    buf: Vec<u8>,
}

impl FrameDecoder {
    pub fn new() -> Self {
        Self {
            buf: Vec::with_capacity(4096),
        }
    }

    /// Push new data from the TLS/TCP stream
    pub fn push(&mut self, data: &[u8]) {
        self.buf.extend_from_slice(data);
    }

    /// Try to decode the next complete packet from the buffer
    pub fn next_packet(&mut self) -> Result<Option<Vec<u8>>> {
        match decode_frame(&self.buf)? {
            Some((packet, consumed)) => {
                // Remove consumed bytes from buffer
                self.buf.drain(..consumed);
                Ok(Some(packet))
            }
            None => Ok(None),
        }
    }

    /// Check if the internal buffer is empty
    pub fn is_empty(&self) -> bool {
        self.buf.is_empty()
    }
}

impl Default for FrameDecoder {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_frame_roundtrip() {
        let original = vec![1, 2, 3, 4, 5];
        let framed = frame_packet(&original);
        assert_eq!(framed.len(), 7); // 2 + 5

        let (decoded, consumed) = decode_frame(&framed).unwrap().unwrap();
        assert_eq!(decoded, original);
        assert_eq!(consumed, 7);
    }

    #[test]
    fn test_incomplete_frame() {
        let framed = frame_packet(&[1, 2, 3]);
        // Only give first 3 bytes (header + 1 byte, but need 5 total)
        assert!(decode_frame(&framed[..3]).unwrap().is_none());
    }

    #[test]
    fn test_decoder_multiple_packets() {
        let mut decoder = FrameDecoder::new();

        let pkt1 = vec![10, 20, 30];
        let pkt2 = vec![40, 50, 60, 70];

        let mut data = frame_packet(&pkt1);
        data.extend_from_slice(&frame_packet(&pkt2));

        decoder.push(&data);

        assert_eq!(decoder.next_packet().unwrap().unwrap(), pkt1);
        assert_eq!(decoder.next_packet().unwrap().unwrap(), pkt2);
        assert!(decoder.next_packet().unwrap().is_none());
    }

    #[test]
    fn test_decoder_partial_push() {
        let mut decoder = FrameDecoder::new();
        let pkt = vec![1, 2, 3, 4, 5];
        let framed = frame_packet(&pkt);

        // Push in two parts
        decoder.push(&framed[..3]);
        assert!(decoder.next_packet().unwrap().is_none());

        decoder.push(&framed[3..]);
        assert_eq!(decoder.next_packet().unwrap().unwrap(), pkt);
    }
}
