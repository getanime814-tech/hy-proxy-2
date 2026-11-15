"""GojoTV Hybrid Proxy — FastAPI entry point."""

import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from anilist_route import router as anilist_router
from reanime_route import router as reanime_router
from helpers import anilist_limiter, reanime_limiter
from config import ANILIST_RATE_MAX, REANIME_RATE_MAX, BROWSER_PROFILES, REANIME_DOMAINS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

if not BROWSER_PROFILES:
    raise ValueError("BROWSER_PROFILES list is empty in config.py")
if not REANIME_DOMAINS:
    raise ValueError("REANIME_DOMAINS list is empty in config.py")

app = FastAPI(title="GojoTV Hybrid Proxy", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["POST", "GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {
        "ok": True,
        "service": "gojotv-hybrid-proxy",
        "timestamp": int(time.time()),
        "anilist": {"rate_now": anilist_limiter.count(), "rate_max": ANILIST_RATE_MAX},
        "reanime": {"rate_now": reanime_limiter.count(), "rate_max": REANIME_RATE_MAX},
    }

app.include_router(anilist_router)
app.include_router(reanime_router)
logger.info("GojoTV Hybrid Proxy loaded successfully")
