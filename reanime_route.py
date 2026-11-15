"""Re:ANIME stream proxy route."""

import logging
import asyncio
from fastapi import APIRouter, Query, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from curl_cffi import requests as curl_requests

from config import REANIME_DOMAINS, BROWSER_PROFILES, PROXY_API_KEY, REQUEST_TIMEOUT_SECONDS, WARP_PROXY
from helpers import reanime_limiter, build_html_headers, build_api_headers

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != PROXY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

@router.get("/reanime", dependencies=[Depends(verify_api_key)])
async def reanime_streams(
    anilist: int = Query(..., gt=0, description="AniList ID must be > 0"),
    episode: int = Query(1, gt=0, description="Episode must be > 0"),
):
    if not reanime_limiter.check():
        return JSONResponse({"success": False, "servers": [], "error": "Rate limit hit"}, status_code=429)

    if not REANIME_DOMAINS:
        return JSONResponse({"success": False, "servers": [], "error": "No domains configured"}, status_code=500)

    domain = REANIME_DOMAINS[0]
    api_url = f"{domain}/api/flix/{anilist}/{episode}"
    warmup_url = f"{domain}/"
    
    last_error = ""
    last_status = 502

    for profile in BROWSER_PROFILES:
        html_headers = build_html_headers()
        api_headers = build_api_headers(domain + "/")
        
        def do_session_request():
            # 🎯 WARP Proxy is now injected into the session
            with curl_requests.Session(impersonate=profile["impersonate"]) as session:
                try:
                    session.get(
                        warmup_url, 
                        headers=html_headers, 
                        timeout=REQUEST_TIMEOUT_SECONDS,
                        proxies=WARP_PROXY
                    )
                except Exception as e:
                    logger.warning(f"Warmup failed for {profile['name']}: {e}")
                
                return session.get(
                    api_url, 
                    headers=api_headers, 
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    proxies=WARP_PROXY
                )

        try:
            response = await asyncio.to_thread(do_session_request)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict):
                        raise ValueError("Not a dict")
                except Exception:
                    last_error = "Invalid JSON from upstream"
                    last_status = 502
                    continue 

                return Response(content=response.text, status_code=200, media_type="application/json")
            
            elif response.status_code in (403, 404):
                last_error = f"Upstream blocked or not found (HTTP {response.status_code})"
                last_status = 502
                continue 
                
            elif response.status_code == 429:
                last_error = "Upstream rate limited"
                last_status = 429
                continue 
                
            else:
                last_error = f"Upstream HTTP {response.status_code}"
                last_status = 502
                continue 
                
        except Exception as e:
            last_error = f"{profile['name']}: {str(e)}"
            last_status = 504
            continue 

    return JSONResponse({
        "success": False,
        "servers": [],
        "error": last_error or "All profiles failed"
    }, status_code=last_status)
