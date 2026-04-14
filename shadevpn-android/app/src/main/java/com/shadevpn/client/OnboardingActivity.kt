package com.shadevpn.client

import android.app.Activity
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import com.google.android.material.button.MaterialButton
import com.google.zxing.BinaryBitmap
import com.google.zxing.DecodeHintType
import com.google.zxing.MultiFormatReader
import com.google.zxing.RGBLuminanceSource
import com.google.zxing.common.HybridBinarizer
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import org.json.JSONObject
import java.util.UUID
import kotlinx.coroutines.*

/**
 * Onboarding — first launch.
 * Supports both legacy shade:// keys (single server) and
 * subscription shade:// keys (with embedded "sub" URL for dynamic server list).
 */
class OnboardingActivity : AppCompatActivity() {

    private val langCodes = listOf("en", "ru", "tr", "ar", "zh")
    private val langNames = listOf("English", "Русский", "Türkçe", "العربية", "中文")
    private var langIndex = 0

    private lateinit var editKey: EditText

    // ZXing Scanner Intent (Standalone, no external apps)
    private val barcodeLauncher = registerForActivityResult(ScanContract()) { result ->
        if (result.contents != null) {
            editKey.setText(result.contents)
            activateKey(result.contents)
        } else {
            Toast.makeText(this, "Scan cancelled", Toast.LENGTH_SHORT).show()
        }
    }

    // Gallery picker
    private val galleryLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val imageUri = result.data?.data
            if (imageUri != null) {
                decodeQRFromImage(imageUri)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)

        editKey = findViewById(R.id.editKey)
        val btnPaste = findViewById<MaterialButton>(R.id.btnPaste)
        val btnActivate = findViewById<MaterialButton>(R.id.btnActivate)
        val btnScanQR = findViewById<MaterialButton>(R.id.btnScanQR)
        val btnLoadQR = findViewById<MaterialButton>(R.id.btnLoadQR)
        val btnGetKey = findViewById<TextView>(R.id.btnGetKey)
        val btnLang = findViewById<MaterialButton>(R.id.btnLangOnboarding)

        // Init language
        val savedLang = SecureStorage.loadLanguage(this)
        langIndex = langCodes.indexOf(savedLang).coerceAtLeast(0)
        updateLangButton(btnLang)

        // Language cycle
        btnLang.setOnClickListener {
            langIndex = (langIndex + 1) % langCodes.size
            val newLang = langCodes[langIndex]
            SecureStorage.saveLanguage(this, newLang)
            updateLangButton(btnLang)
            AppCompatDelegate.setApplicationLocales(
                LocaleListCompat.forLanguageTags(newLang)
            )
        }

        // Paste from clipboard
        btnPaste.setOnClickListener {
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = clipboard.primaryClip
            if (clip != null && clip.itemCount > 0) {
                val text = clip.getItemAt(0).text?.toString() ?: ""
                editKey.setText(text)
                editKey.setSelection(text.length)
            }
        }

        // Activate key
        btnActivate.setOnClickListener {
            val key = editKey.text.toString().trim()
            activateKey(key)
        }

        // Scan QR with camera using ZXing embedded
        btnScanQR.setOnClickListener {
            val options = ScanOptions()
            options.setDesiredBarcodeFormats(ScanOptions.QR_CODE)
            options.setPrompt(getString(R.string.btn_scan_qr))
            options.setBeepEnabled(false)
            options.setBarcodeImageEnabled(false)
            options.setOrientationLocked(false)
            barcodeLauncher.launch(options)
        }

        // Load QR from gallery
        btnLoadQR.setOnClickListener {
            val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
            galleryLauncher.launch(intent)
        }

        // Get a key link
        btnGetKey.setOnClickListener {
            try {
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://t.me/shadevpn_bot")))
            } catch (_: Exception) { }
        }
    }

    private fun updateLangButton(btn: MaterialButton) {
        btn.text = "\uD83C\uDF10 ${langNames[langIndex]}"
    }

    private fun decodeQRFromImage(imageUri: Uri) {
        try {
            val inputStream = contentResolver.openInputStream(imageUri)
            val bitmap = BitmapFactory.decodeStream(inputStream)
            inputStream?.close()

            if (bitmap == null) {
                Toast.makeText(this, "Could not load image", Toast.LENGTH_SHORT).show()
                return
            }

            val intArray = IntArray(bitmap.width * bitmap.height)
            bitmap.getPixels(intArray, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)

            val source = RGBLuminanceSource(bitmap.width, bitmap.height, intArray)
            val binaryBitmap = BinaryBitmap(HybridBinarizer(source))

            // Enhanced QR decoding with TRY_HARDER for better gallery image support
            val hints = mapOf(
                DecodeHintType.TRY_HARDER to true,
                DecodeHintType.PURE_BARCODE to false,
                DecodeHintType.POSSIBLE_FORMATS to listOf(com.google.zxing.BarcodeFormat.QR_CODE)
            )

            try {
                val reader = MultiFormatReader()
                reader.setHints(hints)
                val result = reader.decode(binaryBitmap)
                val rawValue = result.text
                if (rawValue.isNotEmpty()) {
                    editKey.setText(rawValue)
                    activateKey(rawValue)
                }
            } catch (e: Exception) {
                // Try again with inverted image (dark mode screenshots)
                try {
                    val invertedSource = source.invert()
                    val invertedBitmap = BinaryBitmap(HybridBinarizer(invertedSource))
                    val reader = MultiFormatReader()
                    reader.setHints(hints)
                    val result = reader.decode(invertedBitmap)
                    val rawValue = result.text
                    if (rawValue.isNotEmpty()) {
                        editKey.setText(rawValue)
                        activateKey(rawValue)
                    }
                } catch (_: Exception) {
                    Toast.makeText(this, getString(R.string.error_invalid_qr), Toast.LENGTH_SHORT).show()
                }
            }

        } catch (e: Exception) {
            Toast.makeText(this, "Error reading image: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun activateKey(key: String) {
        if (key.isEmpty()) {
            Toast.makeText(this, getString(R.string.error_fill_fields), Toast.LENGTH_SHORT).show()
            return
        }

        // Decode the shade:// key
        val raw = key.trim()
        val payload = when {
            raw.startsWith("shade://") -> raw.removePrefix("shade://")
            raw.startsWith("aivpn://") -> raw.removePrefix("aivpn://")
            else -> raw
        }

        val jsonString: String
        try {
            val jsonBytes = android.util.Base64.decode(payload,
                android.util.Base64.URL_SAFE or android.util.Base64.NO_PADDING or android.util.Base64.NO_WRAP)
            jsonString = String(jsonBytes)
        } catch (_: Exception) {
            Toast.makeText(this, getString(R.string.error_invalid_connection_key), Toast.LENGTH_SHORT).show()
            return
        }

        // Check if this is a subscription key
        val subUrl = SubscriptionManager.extractSubUrl(jsonString)
        if (subUrl != null) {
            // Subscription key — fetch servers from API
            activateSubscription(subUrl)
        } else {
            // Legacy single-server key
            activateLegacyKey(key, jsonString)
        }
    }

    private fun activateSubscription(subUrl: String) {

        // Save the subscription URL for future auto-refreshes
        SecureStorage.saveSubscriptionUrl(this, subUrl)

        CoroutineScope(Dispatchers.IO).launch {
            val result = SubscriptionManager.fetchServers(subUrl)

            withContext(Dispatchers.Main) {
                if (result == null) {
                    Toast.makeText(this@OnboardingActivity,
                        "Ошибка соединения с сервером. Проверьте интернет.", Toast.LENGTH_LONG).show()
                    return@withContext
                }

                if (result.status != "active") {
                    Toast.makeText(this@OnboardingActivity,
                        result.message.ifEmpty { "Подписка неактивна" }, Toast.LENGTH_LONG).show()
                    return@withContext
                }

                if (result.servers.isEmpty()) {
                    Toast.makeText(this@OnboardingActivity,
                        "Нет доступных серверов", Toast.LENGTH_LONG).show()
                    return@withContext
                }

                // Save each server as a profile
                val profiles = result.servers.map { server ->
                    SecureStorage.ConnectionProfile(
                        id = server.id.ifEmpty { UUID.randomUUID().toString() },
                        name = server.name,
                        key = server.key
                    )
                }

                SecureStorage.saveProfiles(this@OnboardingActivity, profiles)
                SecureStorage.saveActiveProfileId(this@OnboardingActivity, profiles.first().id)

                // Go to main screen
                startActivity(Intent(this@OnboardingActivity, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                })
                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
                finish()
            }
        }
    }

    private fun activateLegacyKey(originalKey: String, jsonString: String) {
        // Parse the classic single-server key
        val parsed = try {
            val json = JSONObject(jsonString)
            arrayOf(json.getString("s"), json.getString("k"), json.getString("p"), json.getString("i"))
        } catch (_: Exception) {
            Toast.makeText(this, getString(R.string.error_invalid_connection_key), Toast.LENGTH_SHORT).show()
            return
        }

        val profile = SecureStorage.ConnectionProfile(
            id = UUID.randomUUID().toString(),
            name = parsed[0].substringBefore(":"),
            key = originalKey
        )
        val profiles = SecureStorage.loadProfiles(this).toMutableList()
        profiles.add(profile)
        SecureStorage.saveProfiles(this, profiles)
        SecureStorage.saveActiveProfileId(this, profile.id)

        startActivity(Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        })
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
        finish()
    }
}
