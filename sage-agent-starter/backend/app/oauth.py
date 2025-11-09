from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import RedirectResponse
import httpx, time, secrets
from urllib.parse import urlencode
from .settings import get_settings
from .db import get_session, Connection, Tenant
from sqlmodel import select
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

def _tenant_id() -> str:
    # For starter, a fixed demo tenant. Replace with your auth system.
    return "demo-tenant"

@router.get("/start")
async def auth_start():
    s = get_settings()
    # Sage's OAuth authorize URL (example; ensure region-specific if needed)
    authorize_url = "https://www.sage.com/oauth/authorize"
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": s.sage_client_id,
        "redirect_uri": s.sage_redirect_uri,
        "scope": "full_access",
        "state": state,
    }
    return RedirectResponse(f"{authorize_url}?{urlencode(params)}")

@router.get("/callback")
async def auth_callback(request: Request, code: str, state: str, session=Depends(get_session)):
    s = get_settings()
    token_url = "https://www.sage.com/oauth/token"  # Placeholder; update to correct token endpoint
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": s.sage_redirect_uri,
        "client_id": s.sage_client_id,
        "client_secret": s.sage_client_secret,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(token_url, data=data)
        resp.raise_for_status()
        tok = resp.json()

    # Store in connection row (demo)
    tenant_id = _tenant_id()
    conn = Connection(
        id="conn-sbca",
        tenant_id=tenant_id,
        provider="sbca",
        access_token=tok.get("access_token"),
        refresh_token=tok.get("refresh_token"),
        status="active",
    )
    session.add(conn)
    session.commit()
    return RedirectResponse("/connected")
