package com.shadevpn.client

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import com.google.android.material.card.MaterialCardView
import com.google.android.material.switchmaterial.SwitchMaterial

/**
 * Settings screen with 4 sections: Connection, Interface, Account, Support.
 */
class SettingsActivity : AppCompatActivity() {

    private val langCodes = listOf("en", "ru", "tr", "ar", "zh")
    private val langNames = listOf("English", "Русский", "Türkçe", "العربية", "中文")
    private val langFlags = listOf("🇬🇧", "🇷🇺", "🇹🇷", "🇸🇦", "🇨🇳")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        // Back button
        findViewById<ImageView>(R.id.btnBack).setOnClickListener { finish() }

        // ── Connection ──

        val switchKill = findViewById<SwitchMaterial>(R.id.switchKillSwitch)
        switchKill.isChecked = SecureStorage.loadBoolean(this, "kill_switch")
        switchKill.setOnCheckedChangeListener { _, checked ->
            SecureStorage.saveBoolean(this, "kill_switch", checked)
            if (checked) {
                AlertDialog.Builder(this, R.style.Theme_ShadeVPN_Dialog)
                    .setTitle(getString(R.string.kill_switch))
                    .setMessage("Для 100% защиты перейдите в системные настройки Android -> VPN -> ShadeVPN и включите опцию 'Блокировать соединения без VPN'")
                    .setPositiveButton("Перейти в настройки") { _, _ ->
                        try {
                            val intent = Intent("android.net.vpn.SETTINGS")
                            startActivity(intent)
                        } catch (e: Exception) {
                            Toast.makeText(this, "Не удалось открыть настройки автоматически", Toast.LENGTH_SHORT).show()
                        }
                    }
                    .setNegativeButton(getString(R.string.btn_cancel), null)
                    .show()
            }
        }

        val switchNet = findViewById<SwitchMaterial>(R.id.switchNetShield)
        switchNet.isChecked = SecureStorage.loadBoolean(this, "netshield")
        switchNet.setOnCheckedChangeListener { _, checked ->
            SecureStorage.saveBoolean(this, "netshield", checked)
        }

        findViewById<MaterialCardView>(R.id.cardSplitTunnel).setOnClickListener {
            startActivity(Intent(this, SplitTunnelActivity::class.java))
        }

        // ── Interface ──

        val textLang = findViewById<TextView>(R.id.textCurrentLang)
        val currentLang = SecureStorage.loadLanguage(this)
        val currentIdx = langCodes.indexOf(currentLang).coerceAtLeast(0)
        textLang.text = langNames[currentIdx]

        findViewById<MaterialCardView>(R.id.cardLanguage).setOnClickListener {
            val displayNames = langNames.mapIndexed { i, name ->
                "${langFlags[i]}  $name"
            }.toTypedArray()

            AlertDialog.Builder(this, R.style.Theme_ShadeVPN_Dialog)
                .setTitle(getString(R.string.label_language))
                .setItems(displayNames) { _, which ->
                    val newLang = langCodes[which]
                    SecureStorage.saveLanguage(this, newLang)
                    textLang.text = langNames[which]
                    AppCompatDelegate.setApplicationLocales(
                        LocaleListCompat.forLanguageTags(newLang)
                    )
                }
                .show()
        }

        // ── Account ──

        // Show current key preview
        val profiles = SecureStorage.loadProfiles(this)
        val activeId = SecureStorage.loadActiveProfileId(this)
        val active = profiles.find { it.id == activeId } ?: profiles.firstOrNull()
        val keyPreview = findViewById<TextView>(R.id.textKeyPreview)
        if (active != null) {
            val shortKey = if (active.key.length > 30) active.key.take(30) + "..." else active.key
            keyPreview.text = shortKey
        }

        findViewById<MaterialCardView>(R.id.cardChangeKey).setOnClickListener {
            AlertDialog.Builder(this, R.style.Theme_ShadeVPN_Dialog)
                .setTitle(getString(R.string.change_key))
                .setMessage(getString(R.string.change_key_confirm))
                .setPositiveButton(getString(R.string.btn_ok)) { _, _ ->
                    SecureStorage.clearAll(this)
                    startActivity(Intent(this, OnboardingActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                    })
                    finish()
                }
                .setNegativeButton(getString(R.string.btn_cancel), null)
                .show()
        }



        // ── Support ──

        // Feedback
        findViewById<MaterialCardView>(R.id.cardFeedback).setOnClickListener {
            showFeedbackDialog()
        }

        // About
        findViewById<MaterialCardView>(R.id.cardAbout).setOnClickListener {
            AlertDialog.Builder(this, R.style.Theme_ShadeVPN_Dialog)
                .setTitle("ShadeVPN")
                .setMessage("Version 1.0.0\n\nYour Privacy Shield\n\n© 2026 ShadeVPN")
                .setPositiveButton("OK", null)
                .show()
        }
    }

    private fun showFeedbackDialog() {
        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 32, 48, 0)
        }
        val input = EditText(this).apply {
            hint = getString(R.string.feedback_hint)
            minLines = 4
            maxLines = 8
            setTextColor(getColor(R.color.text_primary))
            setHintTextColor(getColor(R.color.text_secondary))
        }
        layout.addView(input)

        AlertDialog.Builder(this, R.style.Theme_ShadeVPN_Dialog)
            .setTitle(getString(R.string.feedback_title))
            .setView(layout)
            .setPositiveButton(getString(R.string.feedback_send)) { _, _ ->
                val feedbackText = input.text.toString().trim()
                if (feedbackText.isNotEmpty()) {
                    // TODO: Send feedback to Telegram bot / API
                    Toast.makeText(this, getString(R.string.feedback_thanks), Toast.LENGTH_LONG).show()
                }
            }
            .setNegativeButton(getString(R.string.btn_cancel), null)
            .show()
    }
}
