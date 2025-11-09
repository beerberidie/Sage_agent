from fastapi import HTTPException
from typing import Any, Dict, Optional
import httpx
from .db import Connection, get_session
from sqlmodel import select
from datetime import datetime, timedelta
from .settings import get_settings

class SageV31Client:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.settings = get_settings()

    def _get_connection(self, session) -> Connection:
        conn = session.exec(select(Connection).where(Connection.tenant_id == self.tenant_id, Connection.provider == "sbca")).first()
        if not conn or not conn.access_token:
            raise HTTPException(status_code=400, detail="Sage connection not configured.")
        return conn

    async def _request(self, method: str, path: str, *, params: Dict[str, Any] | None=None, json: Dict[str, Any] | None=None, headers: Dict[str,str] | None=None):
        base = self.settings.sage_base_url.rstrip("/")
        url = f"{base}{path}"
        async with httpx.AsyncClient(timeout=60) as client, get_session() as session:
            conn = self._get_connection(session)
            h = {
                "Authorization": f"Bearer {conn.access_token}",
                # "X-Business": conn.business_id or "",  # set when you have it
                "Accept": "application/json"
            }
            if headers:
                h.update(headers)
            resp = await client.request(method, url, params=params, json=json, headers=h)
            # TODO: refresh on 401 here
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()

    # ---- Minimal endpoints for MVP ----
    async def list_sales_invoices(self, updated_since: Optional[str]=None, items_per_page: int=50):
        params = {"items_per_page": items_per_page}
        if updated_since:
            params["updated_or_created_since"] = updated_since
        return await self._request("GET", "/sales_invoices", params=params)

    async def create_sales_invoice(self, payload: Dict[str, Any]):
        return await self._request("POST", "/sales_invoices", json=payload)

    async def release_sales_invoice(self, invoice_id: str):
        return await self._request("POST", f"/sales_invoices/{invoice_id}/release")

    async def list_contacts(self, search: Optional[str]=None, items_per_page: int=50):
        params = {"items_per_page": items_per_page}
        if search:
            params["search"] = search
        return await self._request("GET", "/contacts", params=params)

    async def create_contact(self, payload: Dict[str, Any]):
        return await self._request("POST", "/contacts", json=payload)
