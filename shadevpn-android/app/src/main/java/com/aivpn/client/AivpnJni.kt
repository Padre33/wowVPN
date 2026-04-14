@file:JvmName("AivpnJni")
package com.aivpn.client

import android.net.VpnService

/**
 * JNI bridge class in the ORIGINAL package namespace (com.aivpn.client).
 *
 * The prebuilt Rust .so (libaivpn_core.so) has JNI symbols that expect
 * Java_com_aivpn_client_AivpnJni_* method names.
 * This class lives in the original package to match those symbols exactly.
 *
 * ShadeVpnJni in com.shadevpn.client delegates all calls here.
 */
object AivpnJni {

    @JvmStatic
    external fun runTunnel(
        vpnService: VpnService,
        tunFd: Int,
        serverHost: String,
        serverPort: Int,
        serverKey: ByteArray,
        psk: ByteArray?,
    ): String

    @JvmStatic
    external fun stopTunnel()

    @JvmStatic
    external fun getUploadBytes(): Long

    @JvmStatic
    external fun getDownloadBytes(): Long
}
