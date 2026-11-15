"""AniList GraphQL proxy route."""

import logging
import asyncio
import random
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, Response

from config import ANILIST_URL, PROXY_API_KEY, PROXIES
from helpers import anilist_limiter, curl_request, pick_profile, build_api_headers

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != PROXY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

@router.post("/graphql", dependencies=[Depends(verify_api_key)])
async def anilist_graphql(request: Request):
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="replace")

    if not body_str.strip():
        return JSONResponse({"error": "Empty body"}, status_code=400)

    if not anilist_limiter.check():
        return JSONResponse({"error": "Rate limit hit"}, status_code=429)

    # 🎯 Shuffle proxies to avoid hitting AniList rate limits
    shuffled_proxies = PROXIES.copy()
    random.shuffle(shuffled_proxies)
    
    last_error = "AniList request failed"
    
    # Try up to 3 proxies
    for proxy_url in shuffled_proxies[:3]:
        proxy_dict = {"http": proxy_url, "https": proxy_url}
        
        try:
            profile = pick_profile()
            api_headers = build_api_headers("https://anilist.co/")
            api_headers["Content-Type"] = "application/json"
            
            logger.info(f"AniList request via proxy: {proxy_url}")
            
            response = await curl_request(
                url=ANILIST_URL,
                method="POST",
                body=body_str,
                headers=api_headers,
                impersonate=profile["impersonate"],
                proxies=proxy_dict, # 🎯 PROXY ADDED HERE
                max_retries=1 # We will handle retries via the proxy loop
            )

            if response.status_code == 200:
                try:
                    response.json()
                except Exception:
                    last_error = "Invalid JSON from AniList"
                    continue # Try next proxy

                return Response(
                    content=response.text,
                    status_code=response.status_code,
                    media_type="application/json"
                )
            elif response.status_code == 429:
                logger.warning(f"AniList 429 via {proxy_url}. Trying next proxy...")
                last_error = "AniList rate limited"
                continue # Try next proxy
            else:
                last_error = f"AniList HTTP {response.status_code}"
                continue # Try next proxy

        except Exception as e:
            logger.error(f"AniList proxy error: {e}")
            last_error = str(e)
            continue # Try next proxy

    # If all proxies failed
    return JSONResponse({"error": last_error}, status_code=502)
