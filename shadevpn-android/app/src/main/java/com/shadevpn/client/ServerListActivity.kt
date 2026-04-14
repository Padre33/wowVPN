package com.shadevpn.client

import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.card.MaterialCardView
import org.json.JSONObject

class ServerListActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_list)

        findViewById<ImageView>(R.id.btnBack).setOnClickListener { finish() }

        val activeKey = SecureStorage.loadConnectionKey(this)
        
        if (activeKey.isNotEmpty()) {
            val parsed = parseConnectionKey(activeKey)
            if (parsed != null) {
                val host = parsed[0].substringBefore(":")
                findViewById<TextView>(R.id.textServerCountry).text = host
                findViewById<TextView>(R.id.textServerCity).text = "Custom Server"
                findViewById<TextView>(R.id.textServerFlag).text = "NL"
            }
        }

        findViewById<MaterialCardView>(R.id.cardActiveServer).setOnClickListener {
            finish()
        }

        findViewById<MaterialCardView>(R.id.cardFastConnect).setOnClickListener {
            // Send user back to MainActivity and tell it to connect automatically
            val intent = android.content.Intent(this, MainActivity::class.java)
            intent.flags = android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP or android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP
            intent.putExtra("auto_connect", true)
            startActivity(intent)
            finish()
        }
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
            val json = JSONObject(String(jsonBytes))
            arrayOf(json.getString("s"), json.getString("k"), json.getString("p"), json.getString("i"))
        } catch (_: Exception) { null }
    }
}
