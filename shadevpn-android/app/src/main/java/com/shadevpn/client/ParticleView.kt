package com.shadevpn.client

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import androidx.core.content.ContextCompat
import kotlin.math.hypot
import kotlin.math.max
import kotlin.random.Random

/**
 * Dynamic cyberpunk particle background.
 * Draws moving dots connected by lines when they get close.
 */
class ParticleView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val particles = mutableListOf<Particle>()
    private val particleCount = 40 // Adjust for density
    private val connectionRadius = 250f // Pixel distance to draw connection lines
    
    private val baseColor = ContextCompat.getColor(context, R.color.accent)
    // Extract base RGB to manipulate alpha for lines
    private val r = Color.red(baseColor)
    private val g = Color.green(baseColor)
    private val b = Color.blue(baseColor)

    private val dotPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = baseColor
        style = Paint.Style.FILL
    }

    private val linePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        strokeWidth = 2f
        style = Paint.Style.STROKE
    }

    private var isInitialized = false

    data class Particle(
        var x: Float,
        var y: Float,
        var vx: Float,
        var vy: Float,
        val radius: Float
    )

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        if (w == 0 || h == 0) return

        particles.clear()
        for (i in 0 until particleCount) {
            particles.add(
                Particle(
                    x = Random.nextFloat() * w,
                    y = Random.nextFloat() * h,
                    vx = (Random.nextFloat() - 0.5f) * 2f, // Speed X
                    vy = (Random.nextFloat() - 0.5f) * 2f, // Speed Y
                    radius = Random.nextFloat() * 4f + 3f  // Size 3-7px
                )
            )
        }
        isInitialized = true
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (!isInitialized) return

        val width = width.toFloat()
        val height = height.toFloat()

        // Update positions & bounce off walls
        for (p in particles) {
            p.x += p.vx
            p.y += p.vy

            if (p.x < 0) { p.x = 0f; p.vx *= -1 }
            if (p.x > width) { p.x = width; p.vx *= -1 }
            if (p.y < 0) { p.y = 0f; p.vy *= -1 }
            if (p.y > height) { p.y = height; p.vy *= -1 }
        }

        // Draw connections
        for (i in 0 until particles.size) {
            val p1 = particles[i]
            for (j in i + 1 until particles.size) {
                val p2 = particles[j]
                val dist = hypot(p1.x - p2.x, p1.y - p2.y)
                
                if (dist < connectionRadius) {
                    // Alpha depends on distance (closer = more opaque, max 150)
                    val alpha = (150 * (1f - dist / connectionRadius)).toInt()
                    linePaint.color = Color.argb(alpha, r, g, b)
                    canvas.drawLine(p1.x, p1.y, p2.x, p2.y, linePaint)
                }
            }
        }

        // Draw particles (dots)
        dotPaint.color = Color.argb(200, r, g, b)
        for (p in particles) {
            canvas.drawCircle(p.x, p.y, p.radius, dotPaint)
        }

        // Keep animating continuously
        postInvalidateOnAnimation()
    }
}
