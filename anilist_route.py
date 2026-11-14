"""AniList GraphQL proxy route."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from config import ANILIST_URL
from helpers import anilist_limiter, curl_request, pick_ua

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/graphql")
async def anilist_graphql(request: Request):
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="replace")

    if not body_str.strip():
        return JSONResponse({"error": "Empty body"}, status_code=400)

    # Rate limit only (no cache; W3 Redis handles caching upstream)
    if not anilist_limiter.check():
        return JSONResponse(
            {"error": "Local rate limit hit. Retry in 60s."},
            status_code=429,
            headers={"X-Cache": "RATE_LIMIT"},
        )

    try:
        response = await curl_request(
            url=ANILIST_URL,
            method="POST",
            body=body_str,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": pick_ua(),
                "Origin": "https://anilist.co",
                "Referer": "https://anilist.co/",
            },
        )

        return Response(
            content=response.text,
            status_code=response.status_code,
            media_type="application/json",
            headers={"X-Cache": "BYPASS"},
        )
    except Exception as e:
        logger.error(f"AniList error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
