package com.shadevpn.client

import android.app.Activity
import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.os.Handler
import android.view.HapticFeedbackConstants
import android.os.Looper
import android.util.Log
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.card.MaterialCardView
import org.json.JSONObject
import kotlinx.coroutines.*

/**
 * Main VPN screen — power button, status, stats, server card.
 * Matches Figma design: S logo + gear, centered power circle, bottom server card.
 */
class MainActivity : AppCompatActivity() {

    private var isConnected = false
    private var activeKey: String = ""

    // Views
    private lateinit var btnConnect: FrameLayout
    private lateinit var powerBg: View
    private lateinit var powerIcon: ImageView
    private lateinit var statusDot: View
    private lateinit var textStatus: TextView
    private lateinit var textTimer: TextView
    private lateinit var statsRow: LinearLayout
    private lateinit var textUpload: TextView
    private lateinit var textDownload: TextView
    private lateinit var textDuration: TextView

    private val vpnPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            startVpnService()
        } else {
            Toast.makeText(this, getString(R.string.error_vpn_denied), Toast.LENGTH_SHORT).show()
        }
    }

    // Connection timer
    private val timerHandler = Handler(Looper.getMainLooper())
    private var connectionStartTime = 0L
    private val timerRunnable = object : Runnable {
        override fun run() {
            if (isConnected && connectionStartTime > 0) {
                val elapsed = (System.currentTimeMillis() - connectionStartTime) / 1000
                val h = elapsed / 3600
                val m = (elapsed % 3600) / 60
                val s = elapsed % 60
                textTimer.text = String.format("%02d:%02d:%02d", h, m, s)
                textDuration.text = String.format("%02d:%02d", h * 60 + m, s)
                timerHandler.postDelayed(this, 1000)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Bind views
        btnConnect = findViewById(R.id.btnConnect)
        powerBg = findViewById(R.id.powerBg)
        powerIcon = findViewById(R.id.powerIcon)
        statusDot = findViewById(R.id.statusDot)
        textStatus = findViewById(R.id.textStatus)
        textTimer = findViewById(R.id.textTimer)
        statsRow = findViewById(R.id.statsRow)
        textUpload = findViewById(R.id.textUpload)
        textDownload = findViewById(R.id.textDownload)
        textDuration = findViewById(R.id.textDuration)

        // Load active key
        val profiles = SecureStorage.loadProfiles(this)
        val activeId = SecureStorage.loadActiveProfileId(this)
        val active = profiles.find { it.id == activeId } ?: profiles.firstOrNull()
        activeKey = active?.key ?: ""

        // If no key at all, go to onboarding
        if (activeKey.isEmpty()) {
            startActivity(Intent(this, OnboardingActivity::class.java))
            finish()
            return
        }

        // Server card — show server info
        updateServerCard(active)

        // Background subscription refresh (silent, non-blocking)
        val subUrl = SecureStorage.loadSubscriptionUrl(this)
        if (subUrl.isNotEmpty()) {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    val updatedProfiles = SubscriptionManager.refreshAndSaveProfiles(this@MainActivity)
                    if (updatedProfiles != null && updatedProfiles.isNotEmpty()) {
                        withContext(Dispatchers.Main) {
                            // Reload the active profile after refresh
                            val newActiveId = SecureStorage.loadActiveProfileId(this@MainActivity)
                            val newActive = updatedProfiles.find { it.id == newActiveId } ?: updatedProfiles.first()
                            activeKey = newActive.key
                            updateServerCard(newActive)
                            Log.d("MainActivity", "Subscription refreshed: ${updatedProfiles.size} servers")
                        }
                    }
                } catch (e: Exception) {
                    Log.e("MainActivity", "Subscription refresh failed: ${e.message}")
                }
            }
        }

        // Connect button with haptic feedback
        btnConnect.setOnClickListener {
            it.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
            if (isConnected) disconnect() else connect()
        }

        // Settings
        findViewById<ImageView>(R.id.btnSettings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        // Server card click
        findViewById<com.google.android.material.card.MaterialCardView>(R.id.cardServer).setOnClickListener {
            startActivity(android.content.Intent(this, ServerListActivity::class.java))
        }

        // Restore connection state
        if (ShadeVpnService.isRunning) {
            isConnected = true
            updateUI(true, ShadeVpnService.lastStatusText)
        }

        // Check if opened via fast connect
        if (intent?.getBooleanExtra("auto_connect", false) == true) {
            if (!isConnected) {
                // Post connection to run after UI is fully initialized
                btnConnect.post { connect() }
            }
        }
    }

    private val knownServers = mapOf(
        "185.204.52.135" to Pair("Нидерланды", "🇳🇱"),
        // Add more servers here as you buy them
    )

    private fun updateServerCard(profile: SecureStorage.ConnectionProfile?) {
        if (profile == null) return

        // Try to extract flag from name (subscription format: "Нидерланды 🇳🇱")
        val flagMatch = Regex("[\\uD83C][\\uDDE6-\\uDDFF]{2}|[\\uD83C][\\uDDE6-\\uDDFF][\\uD83C][\\uDDE6-\\uDDFF]").find(profile.name)
        if (flagMatch != null) {
            val cleanName = profile.name.replace(flagMatch.value, "").trim()
            findViewById<TextView>(R.id.textServerName).text = cleanName.ifEmpty { profile.name }
            findViewById<TextView>(R.id.textServerFlag).text = flagMatch.value
            return
        }

        // For old profiles: try to extract IP from key and look up known name
        val parsed = parseConnectionKey(profile.key)
        if (parsed != null) {
            val serverIp = parsed[0].substringBefore(":")
            val known = knownServers[serverIp]
            if (known != null) {
                findViewById<TextView>(R.id.textServerName).text = known.first
                findViewById<TextView>(R.id.textServerFlag).text = known.second
                return
            }
        }

        // Fallback
        findViewById<TextView>(R.id.textServerName).text = profile.name
        findViewById<TextView>(R.id.textServerFlag).text = "🌐"
    }

    override fun onNewIntent(intent: android.content.Intent?) {
        super.onNewIntent(intent)
        if (intent?.getBooleanExtra("auto_connect", false) == true) {
            if (!isConnected) {
                connect()
            }
        }
    }

    override fun onResume() {
        super.onResume()

        // Reload active profile (in case user switched server in ServerListActivity)
        val profiles = SecureStorage.loadProfiles(this)
        val activeId = SecureStorage.loadActiveProfileId(this)
        val active = profiles.find { it.id == activeId } ?: profiles.firstOrNull()
        if (active != null && active.key.isNotEmpty()) {
            activeKey = active.key
            updateServerCard(active)
        }

        ShadeVpnService.statusCallback = { connected, statusText ->
            runOnUiThread {
                isConnected = connected
                updateUI(connected, statusText)
            }
        }
        ShadeVpnService.trafficCallback = { uploadBytes, downloadBytes ->
            runOnUiThread {
                textUpload.text = formatBytes(uploadBytes)
                textDownload.text = formatBytes(downloadBytes)
            }
        }
        if (ShadeVpnService.isRunning) {
            isConnected = true
            updateUI(true, ShadeVpnService.lastStatusText)
        }
    }

    override fun onPause() {
        super.onPause()
        if (isFinishing) {
            ShadeVpnService.statusCallback = null
            ShadeVpnService.trafficCallback = null
        }
    }

    // ──────────── Connection ────────────

    private fun parseConnectionKey(key: String): Array<String>? {
        val raw = key.trim()
        val payload = when {
            raw.startsWith("shade://") -> raw.removePrefix("shade://")
            raw.startsWith("aivpn://") -> raw.removePrefix("aivpn://")
            else -> raw
        }
        return try {
            val jsonBytes = android.util.Base64.decode(payload,
                android.util.Base64.URL_SAFE or android.util.Base64.NO_PADDING or android.util.Base64.NO_WRAP)
            val json = JSONObject(String(jsonBytes))
            arrayOf(json.getString("s"), json.getString("k"), json.getString("p"), json.getString("i"))
        } catch (_: Exception) { null }
    }

    private fun connect() {
        if (activeKey.isEmpty()) {
            Toast.makeText(this, getString(R.string.error_fill_fields), Toast.LENGTH_SHORT).show()
            return
        }
        val parsed = parseConnectionKey(activeKey)
        if (parsed == null) {
            Toast.makeText(this, getString(R.string.error_invalid_connection_key), Toast.LENGTH_SHORT).show()
            return
        }
        val intent = VpnService.prepare(this)
        if (intent != null) {
            vpnPermissionLauncher.launch(intent)
        } else {
            startVpnService()
        }
    }

    private fun disconnect() {
        val intent = Intent(this, ShadeVpnService::class.java).apply {
            action = ShadeVpnService.ACTION_DISCONNECT
        }
        startService(intent)
    }

    private fun startVpnService() {
        val parsed = parseConnectionKey(activeKey) ?: return
        val (server, serverKey, psk, vpnIp) = parsed
        val intent = Intent(this, ShadeVpnService::class.java).apply {
            action = ShadeVpnService.ACTION_CONNECT
            putExtra("server", server)
            putExtra("server_key", serverKey)
            putExtra("psk", psk)
            putExtra("vpn_ip", vpnIp)
        }
        startForegroundService(intent)
        updateUI(true, getString(R.string.status_connecting))
    }

    // ──────────── UI State ────────────

    private fun updateUI(connected: Boolean, statusText: String) {
        isConnected = connected

        // Power button appearance
        if (connected) {
            powerBg.setBackgroundResource(R.drawable.bg_power_on)
            powerIcon.setColorFilter(getColor(R.color.bg_primary))
            statusDot.setBackgroundResource(R.drawable.dot_green)
        } else {
            powerBg.setBackgroundResource(R.drawable.bg_power_off)
            powerIcon.setColorFilter(getColor(R.color.accent))
            statusDot.setBackgroundResource(R.drawable.dot_grey)
        }

        textStatus.text = statusText

        // Show/hide stats and timer
        val statsVisibility = if (connected) View.VISIBLE else View.GONE
        textTimer.visibility = statsVisibility
        statsRow.visibility = statsVisibility

        // Timer management
        if (connected && connectionStartTime == 0L) {
            connectionStartTime = System.currentTimeMillis()
            timerHandler.post(timerRunnable)
        } else if (!connected) {
            connectionStartTime = 0L
            timerHandler.removeCallbacks(timerRunnable)
            textTimer.text = "00:00:00"
            textUpload.text = "0 B"
            textDownload.text = "0 B"
            textDuration.text = "00:00"
        }
    }

    private fun formatBytes(bytes: Long): String {
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> String.format("%.1f KB", bytes / 1024.0)
            bytes < 1024 * 1024 * 1024 -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
            else -> String.format("%.2f GB", bytes / (1024.0 * 1024.0 * 1024.0))
        }
    }

    override fun onDestroy() {
        timerHandler.removeCallbacks(timerRunnable)
        super.onDestroy()
    }
}
