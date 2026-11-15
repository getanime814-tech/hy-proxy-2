"""Central configuration. Update here when APIs change."""

# ============ AniList ============
ANILIST_URL = "https://graphql.anilist.co"

# ============ Re:ANIME ============
REANIME_DOMAINS = [
    "https://reanime.cz",   # current primary (do not remove)
    "https://reanime.to",   # fallback (may 403 from DC IPs)
]

# ============ Rate Limits ============
ANILIST_RATE_MAX = 30
REANIME_RATE_MAX = 60
RATE_WINDOW_SECONDS = 60

# ============ HTTP ============
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3

# ============ Browser Profiles ============
# 🎯 Critical: UA + TLS impersonate + Client Hints MUST match.
# Otherwise Cloudflare JA3 fingerprint detects mismatch.
BROWSER_PROFILES = [
    {
        "name": "chrome124-win",
        "impersonate": "chrome124",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    },
    {
        "name": "chrome124-mac",
        "impersonate": "chrome124",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "platform": '"macOS"',
        "sec_ch_ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    },
    {
        "name": "chrome120-win",
        "impersonate": "chrome120",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": '"Windows"',
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    },
]
