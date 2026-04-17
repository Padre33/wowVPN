package com.shadevpn.client

import android.net.VpnService
import com.aivpn.client.AivpnJni

/**
 * ShadeVPN JNI wrapper.
 * Delegates all native calls to [AivpnJni] which lives in the original
 * com.aivpn.client package to match the prebuilt Rust .so JNI symbols.
 */
object ShadeVpnJni {

    init {
        System.loadLibrary("aivpn_core")
    }

    fun runTunnel(
        vpnService: VpnService,
        tunFd: Int,
        tcpFd: Int,
        serverHost: String,
        serverPort: Int,
        serverKey: ByteArray,
        psk: ByteArray?,
        transport: String = "udp",
    ): String = AivpnJni.runTunnel(vpnService, tunFd, tcpFd, serverHost, serverPort, serverKey, psk, transport)

    fun stopTunnel() = AivpnJni.stopTunnel()

    fun getUploadBytes(): Long = AivpnJni.getUploadBytes()

    fun getDownloadBytes(): Long = AivpnJni.getDownloadBytes()
}
