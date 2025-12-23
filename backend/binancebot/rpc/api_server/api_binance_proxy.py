import logging

import requests
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import Response


logger = logging.getLogger(__name__)

router = APIRouter()

BINANCE_BASE_URL = "https://api.binance.com"
ALLOWED_PATHS = {
    "api/v3/klines",
    "api/v3/ticker/24hr",
    "api/v3/ticker/price",
    "api/v3/exchangeInfo",
    "api/v3/ping",
}


@router.get("/binance-proxy/{path:path}", include_in_schema=False)
def binance_proxy(path: str, request: Request):
    if path not in ALLOWED_PATHS:
        raise HTTPException(status_code=404, detail="Not Found")

    url = f"{BINANCE_BASE_URL}/{path}"
    timeout = 20 if path == "api/v3/exchangeInfo" else 10
    try:
        resp = requests.get(url, params=dict(request.query_params), timeout=timeout)
    except requests.RequestException as exc:
        logger.warning("Binance proxy failed: %s", exc)
        raise HTTPException(status_code=502, detail="Binance proxy error") from exc

    content_type = resp.headers.get("content-type", "application/json")
    return Response(content=resp.content, status_code=resp.status_code, media_type=content_type)
