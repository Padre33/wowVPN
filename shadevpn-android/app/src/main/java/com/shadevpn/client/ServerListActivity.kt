package com.shadevpn.client

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.card.MaterialCardView

/**
 * Displays all available VPN servers as a scrollable list.
 * Servers come from saved profiles (fetched via subscription).
 * User taps a server → it becomes active → returns to main screen.
 */
class ServerListActivity : AppCompatActivity() {

    private lateinit var serverListContainer: LinearLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_list)

        serverListContainer = findViewById(R.id.serverListContainer)

        findViewById<ImageView>(R.id.btnBack).setOnClickListener { finish() }

        // Fast Connect card
        findViewById<MaterialCardView>(R.id.cardFastConnect).setOnClickListener {
            val intent = android.content.Intent(this, MainActivity::class.java)
            intent.flags = android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP or
                    android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP
            intent.putExtra("auto_connect", true)
            startActivity(intent)
            finish()
        }

        // Load and display servers
        loadServers()
    }

    private fun loadServers() {
        serverListContainer.removeAllViews()

        val profiles = SecureStorage.loadProfiles(this)
        val activeId = SecureStorage.loadActiveProfileId(this)

        if (profiles.isEmpty()) {
            val emptyText = TextView(this).apply {
                text = "Нет доступных серверов"
                setTextColor(resources.getColor(R.color.text_secondary, theme))
                textSize = 15f
                setPadding(16, 32, 16, 32)
            }
            serverListContainer.addView(emptyText)
            return
        }

        for (profile in profiles) {
            val cardView = LayoutInflater.from(this)
                .inflate(R.layout.item_server, serverListContainer, false)

            val textFlag = cardView.findViewById<TextView>(R.id.textFlag)
            val textName = cardView.findViewById<TextView>(R.id.textServerName)
            val textCountry = cardView.findViewById<TextView>(R.id.textServerCountry)
            val iconActive = cardView.findViewById<ImageView>(R.id.iconActive)
            val card = cardView as MaterialCardView

            // Resolve display name, flag, and subtitle
            val serverInfo = resolveServerInfo(profile)
            textFlag.text = serverInfo.flag
            textName.text = serverInfo.displayName
            textCountry.text = serverInfo.subtitle

            // Highlight active server
            val isActive = profile.id == activeId
            if (isActive) {
                card.strokeColor = resources.getColor(R.color.accent, theme)
                card.strokeWidth = 2
                iconActive.visibility = View.VISIBLE
            } else {
                card.strokeColor = resources.getColor(R.color.bg_tertiary, theme)
                card.strokeWidth = 1
                iconActive.visibility = View.GONE
            }

            // Click to select server
            card.setOnClickListener {
                SecureStorage.saveActiveProfileId(this, profile.id)
                // Removed annoying Toast

                // Return to main screen
                val intent = android.content.Intent(this, MainActivity::class.java)
                intent.flags = android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP or
                        android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP
                startActivity(intent)
                finish()
            }

            serverListContainer.addView(cardView)
        }
    }

    // ──────────── Server Info Resolution ────────────

    data class ServerDisplayInfo(
        val displayName: String,
        val flag: String,
        val subtitle: String
    )

    /**
     * Known server IPs → human-readable info.
     * Add your real servers here as you buy them.
     */
    private val knownServers = mapOf(
        "185.204.52.135" to ServerDisplayInfo("Нидерланды", "🇳🇱", "Amsterdam, NL"),
        // Add more servers here:
        // "123.45.67.89" to ServerDisplayInfo("Турция", "🇹🇷", "Istanbul, TR"),
        // "98.76.54.32" to ServerDisplayInfo("Германия", "🇩🇪", "Frankfurt, DE"),
    )

    private fun resolveServerInfo(profile: SecureStorage.ConnectionProfile): ServerDisplayInfo {
        // 1. If name already has emoji flag (new subscription format), use as-is
        val flagMatch = Regex("[\\uD83C][\\uDDE6-\\uDDFF]{2}|[\\uD83C][\\uDDE6-\\uDDFF][\\uD83C][\\uDDE6-\\uDDFF]").find(profile.name)
        if (flagMatch != null) {
            val cleanName = profile.name.replace(flagMatch.value, "").trim()
            return ServerDisplayInfo(
                displayName = cleanName.ifEmpty { profile.name },
                flag = flagMatch.value,
                subtitle = cleanName
            )
        }

        // 2. Trust the given profile name if it's not a raw IP
        val customIpRegex = Regex("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$")
        if (!customIpRegex.matches(profile.name) && profile.name.isNotBlank()) {
            // Just use the API provided name, fallback flag logic if no regex match
            return ServerDisplayInfo(
                displayName = profile.name,
                flag = flagMatch?.value ?: "🇪🇺",
                subtitle = profile.name.split(" ").lastOrNull() ?: "Auto"
            )
        }

        // 3. Try to extract IP from the key and look up in known servers
        val parsed = parseConnectionKey(profile.key)
        if (parsed != null) {
            val serverIp = parsed[0].substringBefore(":")
            val known = knownServers[serverIp]
            if (known != null) {
                return known
            }
            // Unknown server — use IP with globe
            return ServerDisplayInfo(
                displayName = serverIp,
                flag = "🌐",
                subtitle = "Port ${parsed[0].substringAfter(":", "443")}"
            )
        }

        // 3. If name looks like an IP, try to match it
        val ipPattern = Regex("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$")
        if (ipPattern.matches(profile.name)) {
            val known = knownServers[profile.name]
            if (known != null) return known
        }

        // 4. Fallback
        return ServerDisplayInfo(
            displayName = profile.name,
            flag = "🌐",
            subtitle = ""
        )
    }

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
            val json = org.json.JSONObject(String(jsonBytes))
            arrayOf(json.getString("s"), json.getString("k"), json.getString("p"), json.getString("i"))
        } catch (_: Exception) { null }
    }
}
