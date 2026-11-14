"""GojoTV Hybrid Proxy — FastAPI entry point.

Routes:
  POST /graphql   → AniList GraphQL proxy
  GET  /reanime   → Re:ANIME stream proxy
  GET  /health    → Service status (also HEAD for UptimeRobot)
"""

import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from anilist_route import router as anilist_router
from reanime_route import router as reanime_router
from helpers import anilist_limiter, reanime_limiter
from config import ANILIST_RATE_MAX, REANIME_RATE_MAX

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="GojoTV Hybrid Proxy",
    description="Stateless proxy for AniList + Re:ANIME",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)


# ============ HEALTH (GET + HEAD for UptimeRobot compatibility) ============
@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {
        "ok": True,
        "service": "gojotv-hybrid-proxy",
        "runtime": "render-python-curl_cffi",
        "mode": "stateless (no cache)",
        "timestamp": int(time.time()),
        "anilist": {
            "rate_now": anilist_limiter.count(),
            "rate_max": ANILIST_RATE_MAX,
        },
        "reanime": {
            "rate_now": reanime_limiter.count(),
            "rate_max": REANIME_RATE_MAX,
        },
    }


# ============ ROUTES ============
app.include_router(anilist_router)
app.include_router(reanime_router)


logger.info("GojoTV Hybrid Proxy loaded successfully")
