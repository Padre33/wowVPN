package com.shadevpn.client

import android.app.Application
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat

/**
 * Application class — ensures saved language is applied
 * before any Activity is created, preventing locale flicker.
 */
class ShadeVpnApp : Application() {

    override fun onCreate() {
        super.onCreate()

        // Apply saved language at the very start of app lifecycle
        val savedLang = SecureStorage.loadLanguage(this)
        val currentLocales = AppCompatDelegate.getApplicationLocales()
        val currentLang = if (!currentLocales.isEmpty) currentLocales[0]?.language else null

        if (currentLang != savedLang) {
            AppCompatDelegate.setApplicationLocales(
                LocaleListCompat.forLanguageTags(savedLang)
            )
        }
    }
}
