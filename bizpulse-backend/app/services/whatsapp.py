"""
WhatsApp Service — placeholder for future integration.

Options to integrate later:
  1. WhatsApp Business API (Meta)     → https://developers.facebook.com/docs/whatsapp
  2. Twilio WhatsApp API              → https://www.twilio.com/whatsapp
  3. WhatsMeow (unofficial)           → not recommended for production

When ready, set WHATSAPP_TOKEN and WHATSAPP_API_URL in your .env
"""

import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")

async def send_invoice_via_whatsapp(phone: str, invoice_text: str, invoice_pdf_url: str = None) -> dict:
    """
    TODO: Implement real WhatsApp send when API keys are configured.
    For now, returns a simulated success response.
    """
    if not WHATSAPP_TOKEN:
        # Simulated response for development
        return {
            "success": True,
            "message": f"[SIMULATED] Invoice would be sent to {phone}",
            "wa_link": f"https://wa.me/{phone.replace('+','')}?text={invoice_text[:100]}",
        }

    # TODO: Real implementation
    # import httpx
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         WHATSAPP_API_URL,
    #         headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
    #         json={"to": phone, "type": "text", "text": {"body": invoice_text}},
    #     )
    #     return response.json()

    return {"success": False, "message": "WhatsApp not configured"}
