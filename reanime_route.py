"""Re:ANIME stream proxy route."""

import logging
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from config import REANIME_DOMAINS
from helpers import reanime_limiter, curl_request, pick_profile, build_browser_headers

logger = logging.getLogger(__name__)
router = APIRouter()

def _process_servers(servers: list) -> list:
    streams = []
    for server in servers:
        embed_url = server.get("dataLink", "")
        if server.get("dataType") == "dub" and "&a=1" not in embed_url:
            embed_url += "&a=1"
        streams.append({
            "id": server.get("$id"),
            "server": server.get("serverName"),
            "type": server.get("dataType"),
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
        return JSONResponse({"success": False, "error": "Invalid episode", "streams": []}, status_code=400)

    if not reanime_limiter.check():
        return JSONResponse({"success": False, "error": "Rate limit hit", "streams": []}, status_code=429)

    last_error = None
    domain = REANIME_DOMAINS[0] # https://reanime.cz
    profile = pick_profile()

    try:
        # 🎯 Step 1: Warmup (Hit homepage to get __cf_bm cookie)
        warmup_url = f"{domain}/"
        logger.info(f"[REANIME] Warming up session on {domain}")
        await curl_request(
            url=warmup_url,
            method="GET",
            headers=build_browser_headers(profile=profile, referer=domain, origin=domain),
            impersonate=profile["impersonate"],
            max_retries=1,
        )

        # 🎯 Step 2: Hit API with the warmed session
        api_url = f"{domain}/api/flix/{anilist}/{episode}"
        response = await curl_request(
            url=api_url,
            method="GET",
            headers=build_browser_headers(profile=profile, referer=domain, origin=domain),
            impersonate=profile["impersonate"],
        )

        if response.status_code != 200:
            last_error = f"HTTP {response.status_code} from {domain}"
            logger.warning(f"[REANIME] {last_error}")
            # Fallback to next profile if 403
            if response.status_code == 403:
                profile = pick_profile()
                response = await curl_request(
                    url=api_url,
                    method="GET",
                    headers=build_browser_headers(profile=profile, referer=domain, origin=domain),
                    impersonate=profile["impersonate"],
                )
                if response.status_code != 200:
                     return JSONResponse({
                        "success": False, "anilistId": anilist, "episode": ep_num,
                        "streams": [], "error": f"CF Blocked (403). Tried {profile['name']}"
                    })

        data = response.json()
        if not data.get("success") or not data.get("servers"):
            return JSONResponse({"success": False, "error": "No servers", "streams": []})

        logger.info(f"[REANIME] ✅ Success: {anilist}/{episode}")
        return JSONResponse({
            "success": True,
            "anilistId": anilist,
            "episode": ep_num,
            "streams": _process_servers(data["servers"]),
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e), "streams": []})
