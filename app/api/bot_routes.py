"""
AgriVision WhatsApp & Telegram Webhook API Routes (app/api/bot_routes.py).

Provides production webhook handlers for Telegram Bot API, Twilio WhatsApp API,
and a simulation endpoint for local testing and web UI integration.
"""

import base64
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

from app.services.bot_service import AgriBotService

logger = logging.getLogger("AgriBotRoutes")
router = APIRouter(prefix="/api/bot", tags=["AgriBot"])
bot_service = AgriBotService()


class BotSimulationRequest(BaseModel):
    sender_id: str = "farmer_101"
    text: Optional[str] = None
    image_base64: Optional[str] = None
    language: str = "hi"
    district: str = "Karnal"
    acreage: float = 1.0


@router.post("/simulate")
async def simulate_bot_interaction(payload: BotSimulationRequest):
    """
    Simulates a farmer sending a message or leaf photo to WhatsApp / Telegram bot.
    Returns the parsed agronomic diagnosis and channel-ready formatted response.
    """
    image_bytes = None
    if payload.image_base64:
        raw_b64 = payload.image_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1]
        try:
            image_bytes = base64.b64decode(raw_b64)
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid base64 image data: {str(e)}"},
            )

    result = bot_service.handle_message(
        sender_id=payload.sender_id,
        text=payload.text,
        image_bytes=image_bytes,
        language=payload.language,
        district=payload.district,
        acreage=payload.acreage,
    )
    return result


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """
    Receives Telegram Bot updates (text, photo, or audio messages).
    """
    try:
        data = await request.json()
        message = data.get("message", {})
        sender_id = str(message.get("from", {}).get("id", "anonymous"))
        text = message.get("text", "")
        caption = message.get("caption", "")

        # In a live deployment, if photo exists, retrieve file via Telegram Bot API:
        # getFile -> download file bytes. Here we parse text/caption.
        combined_text = (text + " " + caption).strip()

        result = bot_service.handle_message(
            sender_id=sender_id,
            text=combined_text or None,
            image_bytes=None,
            language="hi",
        )

        return {
            "ok": True,
            "method": "sendMessage",
            "chat_id": sender_id,
            "text": result.get("message", ""),
            "parse_mode": "Markdown",
        }
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    From: str = Form("whatsapp:+919876543210"),
    Body: Optional[str] = Form(None),
    NumMedia: Optional[str] = Form("0"),
    MediaUrl0: Optional[str] = Form(None),
):
    """
    Receives Twilio WhatsApp inbound message webhooks.
    Responds with TwiML XML message.
    """
    try:
        sender_id = From
        text = Body

        result = bot_service.handle_message(
            sender_id=sender_id,
            text=text,
            image_bytes=None,
            language="hi",
        )

        reply_text = result.get("message", "राम-राम किसान भाई!")

        # Format TwiML XML
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""

        return Response(content=twiml, media_type="application/xml")
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)
        twiml_err = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>⚠️ सेवा में अस्थायी त्रुटि हुई। कृपया पुनः प्रयास करें।</Message>
</Response>"""
        return Response(content=twiml_err, media_type="application/xml")

