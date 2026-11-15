"""Central configuration. Update here when APIs change."""

import os

# ============ Security ============
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "my-super-secret-key-123")

# ============ AniList ============
ANILIST_URL = "https://graphql.anilist.co"

# ============ Re:ANIME ============
REANIME_DOMAINS = [
    "https://reanime.cz",
]

# ============ Webshare Proxies (2 Accounts = 20 Proxies) ============
PROXIES = [
    # 🎯 Account 1 (fxzdfruw)
    "http://fxzdfruw:r0li7fqpzw3a@45.38.107.97:6014",
    "http://fxzdfruw:r0li7fqpzw3a@64.137.96.74:6641",
    "http://fxzdfruw:r0li7fqpzw3a@198.23.243.226:6361",
    "http://fxzdfruw:r0li7fqpzw3a@38.154.185.97:6370",
    "http://fxzdfruw:r0li7fqpzw3a@84.247.60.125:6095",
    "http://fxzdfruw:r0li7fqpzw3a@191.96.254.138:6185",
    "http://fxzdfruw:r0li7fqpzw3a@198.46.161.42:5092",
    "http://fxzdfruw:r0li7fqpzw3a@64.137.10.153:5803",
    "http://fxzdfruw:r0li7fqpzw3a@104.164.49.38:7693",
    "http://fxzdfruw:r0li7fqpzw3a@23.26.71.145:5628",
    
    # 🎯 Account 2 (jxarwogj)
    "http://jxarwogj:f2ztbhuc0xoc@45.38.107.97:6014",
    "http://jxarwogj:f2ztbhuc0xoc@64.137.96.74:6641",
    "http://jxarwogj:f2ztbhuc0xoc@198.23.243.226:6361",
    "http://jxarwogj:f2ztbhuc0xoc@38.154.185.97:6370",
    "http://jxarwogj:f2ztbhuc0xoc@84.247.60.125:6095",
    "http://jxarwogj:f2ztbhuc0xoc@191.96.254.138:6185",
    "http://jxarwogj:f2ztbhuc0xoc@198.46.161.42:5092",
    "http://jxarwogj:f2ztbhuc0xoc@64.137.10.153:5803",
    "http://jxarwogj:f2ztbhuc0xoc@104.164.49.38:7693",
    "http://jxarwogj:f2ztbhuc0xoc@23.26.71.145:5628",
]

# ============ Rate Limits ============
ANILIST_RATE_MAX = 30
REANIME_RATE_MAX = 60
RATE_WINDOW_SECONDS = 60

# ============ HTTP ============
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
MAX_RETRY_WAIT_SECONDS = 10

# ============ Browser Profiles ============
BROWSER_PROFILES = [
    {"name": "chrome124", "impersonate": "chrome124"},
    {"name": "chrome120", "impersonate": "chrome120"},
    {"name": "chrome116", "impersonate": "chrome116"},
]
