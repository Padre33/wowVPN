package com.shadevpn.client

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.animation.AlphaAnimation
import android.view.animation.ScaleAnimation
import android.view.animation.AnimationSet
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity

/**
 * Splash screen — shows logo for 2 seconds with fade-in animation,
 * then routes to Onboarding (if no key saved) or MainActivity (if key exists).
 * Language is already applied by ShadeVpnApp before this Activity starts.
 */
class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // Animate logo: fade in + scale up
        val logo = findViewById<ImageView>(R.id.splashLogo)
        val animSet = AnimationSet(true).apply {
            addAnimation(AlphaAnimation(0f, 1f).apply { duration = 800 })
            addAnimation(ScaleAnimation(
                0.8f, 1f, 0.8f, 1f,
                ScaleAnimation.RELATIVE_TO_SELF, 0.5f,
                ScaleAnimation.RELATIVE_TO_SELF, 0.5f
            ).apply { duration = 800 })
        }
        logo.startAnimation(animSet)

        // After 2 seconds, decide where to go
        Handler(Looper.getMainLooper()).postDelayed({
            val hasKey = SecureStorage.loadProfiles(this).isNotEmpty()
                    || SecureStorage.loadConnectionKey(this).isNotEmpty()

            val target = if (hasKey) {
                Intent(this, MainActivity::class.java)
            } else {
                Intent(this, OnboardingActivity::class.java)
            }
            startActivity(target)
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
            finish()
        }, 2000)
    }
}
