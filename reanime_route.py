"""Re:ANIME stream proxy route."""

import logging

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from config import REANIME_DOMAINS
from helpers import reanime_limiter, curl_request, pick_ua

logger = logging.getLogger(__name__)
router = APIRouter()


def _process_servers(servers: list) -> list:
    """Convert Re:ANIME servers to our standard format."""
    streams = []
    for server in servers:
        embed_url = server.get("dataLink", "")
        # 🎯 Auto-append DUB audio trigger
        if server.get("dataType") == "dub" and "&a=1" not in embed_url:
            embed_url += "&a=1"
        streams.append({
            "id": server.get("$id"),
            "server": server.get("serverName"),
            "type": server.get("dataType"),  # "sub" or "dub"
            "embedUrl": embed_url,
        })
    return streams


@router.get("/reanime")
async def reanime_streams(
    anilist: str = Query(..., description="AniList ID"),
    episode: str = Query("1", description="Episode number"),
):
    try:
        ep_num = int(episode)
    except ValueError:
        return JSONResponse(
            {"success": False, "error": "Invalid episode", "streams": []},
            status_code=400,
        )

    # Rate limit only (no cache)
    if not reanime_limiter.check():
        return JSONResponse(
            {"success": False, "error": "Local rate limit hit. Retry in 60s.", "streams": []},
            status_code=429,
        )

    last_error = None

    # 🎯 Try each domain in order
    for domain in REANIME_DOMAINS:
        try:
            response = await curl_request(
                url=f"{domain}/api/flix/{anilist}/{episode}",
                method="GET",
                headers={
                    "User-Agent": pick_ua(),
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": f"{domain}/",
                    "Origin": domain,
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                },
            )

            if response.status_code != 200:
                last_error = f"HTTP {response.status_code} from {domain}"
                logger.warning(f"[REANIME] {last_error}")
                continue

            try:
                data = response.json()
            except Exception:
                last_error = f"Invalid JSON from {domain}"
                logger.warning(f"[REANIME] {last_error}")
                continue

            if not data.get("success") or not data.get("servers"):
                last_error = f"No servers from {domain}"
                logger.warning(f"[REANIME] {last_error}")
                continue

            logger.info(f"[REANIME] ✅ Success: {anilist}/{episode} via {domain}")
            return JSONResponse({
                "success": True,
                "anilistId": anilist,
                "episode": ep_num,
                "streams": _process_servers(data["servers"]),
            })

        except Exception as e:
            last_error = str(e)
            logger.warning(f"[REANIME] Failed {domain}: {e}")
            continue

    # All domains failed
    return JSONResponse({
        "success": False,
        "anilistId": anilist,
        "episode": ep_num,
        "streams": [],
        "error": last_error or "All Re:ANIME domains failed",
    })
