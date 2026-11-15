"""AniList GraphQL proxy route."""

import logging
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, Response

from config import ANILIST_URL, PROXY_API_KEY
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

    try:
        profile = pick_profile()
        api_headers = build_api_headers("https://anilist.co/")
        api_headers["Content-Type"] = "application/json"
        
        response = await curl_request(
            url=ANILIST_URL,
            method="POST",
            body=body_str,
            headers=api_headers,
            impersonate=profile["impersonate"],
        )

        try:
            response.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON from AniList"}, status_code=502)

        return Response(content=response.text, status_code=response.status_code, media_type="application/json")
    except Exception as e:
        logger.error(f"AniList error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
