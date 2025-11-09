from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from typing import Optional
from .sage_v31 import SageV31Client

router = APIRouter(prefix="/api/sage", tags=["sage"])

def _tenant_id() -> str:
    return "demo-tenant"

@router.get("/sales_invoices")
async def sales_invoices(updated_since: Optional[str] = Query(default=None)):
    client = SageV31Client(_tenant_id())
    return await client.list_sales_invoices(updated_since=updated_since, items_per_page=50)

@router.post("/sales_invoices")
async def create_sales_invoice(payload: dict):
    client = SageV31Client(_tenant_id())
    return await client.create_sales_invoice(payload)

@router.post("/sales_invoices/{invoice_id}/release")
async def release_sales_invoice(invoice_id: str):
    client = SageV31Client(_tenant_id())
    return await client.release_sales_invoice(invoice_id)

@router.get("/contacts")
async def contacts(search: Optional[str] = None):
    client = SageV31Client(_tenant_id())
    return await client.list_contacts(search=search)

@router.post("/contacts")
async def create_contact(payload: dict):
    client = SageV31Client(_tenant_id())
    return await client.create_contact(payload)
