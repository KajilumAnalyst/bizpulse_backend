from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Sale
from app.services.whatsapp import send_invoice_via_whatsapp

router = APIRouter(prefix="/invoices", tags=["Invoices"])

class SendInvoiceRequest(BaseModel):
    sale_id: int
    phone: Optional[str] = None   # override customer phone if needed

@router.post("/send-whatsapp")
async def send_invoice(body: SendInvoiceRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sale = db.query(Sale).filter(Sale.id == body.sale_id, Sale.owner_id == user.id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    phone = body.phone or sale.customer_phone
    if not phone:
        raise HTTPException(status_code=400, detail="No phone number for this customer")

    # Build plain-text invoice
    items_text = "\n".join(f"  • {item.product_name} x{item.quantity} = ₦{item.total:,.0f}" for item in sale.items)
    invoice_text = (
        f"*Invoice from {user.business_name}*\n"
        f"Invoice: {sale.invoice_number}\n"
        f"Customer: {sale.customer_name or 'Valued Customer'}\n\n"
        f"{items_text}\n\n"
        f"Subtotal: ₦{sale.subtotal:,.0f}\n"
        f"Discount: ₦{sale.discount:,.0f}\n"
        f"*Total: ₦{sale.total:,.0f}*\n\n"
        f"Thank you for your business! 🙏\nPowered by BizPulse"
    )

    result = await send_invoice_via_whatsapp(phone, invoice_text)
    return result
