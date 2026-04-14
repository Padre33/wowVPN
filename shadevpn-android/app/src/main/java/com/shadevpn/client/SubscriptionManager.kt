package com.shadevpn.client

import android.content.Context
import android.util.Log
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.util.UUID
import java.util.concurrent.TimeUnit

/**
 * Manages subscription-based server list fetching.
 * Handles: shade:// keys with embedded "sub" URL,
 * fetching server lists from admin API,
 * saving profiles for each server.
 */
object SubscriptionManager {

    private const val TAG = "SubscriptionManager"

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()

    data class ServerInfo(
        val id: String,
        val name: String,
        val country: String,
        val flag: String,
        val key: String
    )

    data class SubscriptionResult(
        val status: String,
        val username: String,
        val servers: List<ServerInfo>,
        val message: String = ""
    )

    /**
     * Check if a decoded key JSON is a subscription (has "sub" field)
     */
    fun isSubscriptionKey(jsonString: String): Boolean {
        return try {
            val json = JSONObject(jsonString)
            json.has("sub")
        } catch (_: Exception) {
            false
        }
    }

    /**
     * Extract subscription URL from decoded key JSON
     */
    fun extractSubUrl(jsonString: String): String? {
        return try {
            val json = JSONObject(jsonString)
            if (json.has("sub")) json.getString("sub") else null
        } catch (_: Exception) {
            null
        }
    }

    /**
     * Fetch server list from API endpoint (runs on calling thread — use from background!)
     */
    fun fetchServers(subUrl: String): SubscriptionResult? {
        return try {
            val request = Request.Builder()
                .url(subUrl)
                .get()
                .build()

            val response = client.newCall(request).execute()
            val body = response.body?.string() ?: return null

            if (!response.isSuccessful) {
                Log.e(TAG, "API returned ${response.code}: $body")
                return null
            }

            val json = JSONObject(body)
            val status = json.optString("status", "unknown")

            if (status != "active") {
                return SubscriptionResult(
                    status = status,
                    username = json.optString("username", ""),
                    servers = emptyList(),
                    message = json.optString("message", "Подписка неактивна")
                )
            }

            val serversArray = json.optJSONArray("servers") ?: return null
            val servers = mutableListOf<ServerInfo>()

            for (i in 0 until serversArray.length()) {
                val s = serversArray.getJSONObject(i)
                val key = s.optString("key", "")
                if (key.isNotEmpty()) {  // Only include servers with actual keys
                    servers.add(
                        ServerInfo(
                            id = s.optString("id", ""),
                            name = s.optString("name", "Server $i"),
                            country = s.optString("country", "XX"),
                            flag = s.optString("flag", "🌐"),
                            key = key
                        )
                    )
                }
            }

            SubscriptionResult(
                status = status,
                username = json.optString("username", ""),
                servers = servers
            )
        } catch (e: Exception) {
            Log.e(TAG, "Failed to fetch servers: ${e.message}", e)
            null
        }
    }

    /**
     * Fetch servers and save them as profiles.
     * Returns the list of saved profiles, or null on failure.
     */
    fun refreshAndSaveProfiles(context: Context): List<SecureStorage.ConnectionProfile>? {
        val subUrl = SecureStorage.loadSubscriptionUrl(context)
        if (subUrl.isEmpty()) return null

        val result = fetchServers(subUrl) ?: return null
        if (result.status != "active") return null

        val profiles = result.servers.map { server ->
            SecureStorage.ConnectionProfile(
                id = server.id.ifEmpty { UUID.randomUUID().toString() },
                name = server.name,
                key = server.key
            )
        }

        if (profiles.isNotEmpty()) {
            SecureStorage.saveProfiles(context, profiles)
            // Keep active profile if it still exists, otherwise select first
            val activeId = SecureStorage.loadActiveProfileId(context)
            if (profiles.none { it.id == activeId }) {
                SecureStorage.saveActiveProfileId(context, profiles.first().id)
            }
        }

        return profiles
    }
}
