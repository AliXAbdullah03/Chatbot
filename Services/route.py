from fastapi import APIRouter, Request, requests
import openai
from fastapi.responses import PlainTextResponse
import httpx
from typing import List
from Services.openai_fallback import get_openai_response
from utils.language_detect import detect_language
from models.session import session_histories, session_context, get_context, update_context, add_to_history
from utils.escalation_logger import log_escalation 
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import csv
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging
from pydantic import BaseModel
from fastapi import UploadFile, File
from tools.check_allowed_items import check_item_direct
from uuid import uuid4
from pathlib import Path
import base64
from fastapi.responses import JSONResponse
from tools.check_allowed_items import check_allowed_items
import sys
from fastapi import APIRouter, Request, HTTPException
import httpx
from openai import AsyncOpenAI
client = AsyncOpenAI()
test_router = APIRouter()
BASE_URL = os.getenv("FORMS_BASE_URL", "https://example.com/forms")
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/chatbot_debug.logs", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
class TestMessage(BaseModel):
    sender_id: str
    message: str

load_dotenv()

chatbot_router = APIRouter(prefix="/chatbot", tags=["SalesBot"])
logger = logging.getLogger(__name__)
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "default_token")
BASE_URL = os.getenv("Base_Url","https://22a9-2001-8f8-1539-14fe-fc51-5b86-766f-c85d.ngrok-free.app")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN", "")
BOOKING_DIR = Path("booking")
BOOKING_DIR.mkdir(exist_ok=True)
BOOKING_PATHS = {
    "ph-uae": "booking/ph_to_uae.csv",
    "th-uae": "booking/th_to_uae.csv",
    "uae-ph": "booking/uae_to_ph.csv",
}

@test_router.post("/chatbot/test-chat")
async def test_chat(msg: TestMessage):
    reply = await get_openai_response(msg.message, msg.sender_id)
    return {"reply": reply}

templates = Jinja2Templates(directory="templates")

# 🧾 Paths to HTML forms
form_routes = {
    "ph-uae": "https://a1ac-2001-8f8-1539-14fe-999c-bf16-966c-2323.ngrok-free.app/booking_ph_to_uae.html",
    "th-uae": "https://a1ac-2001-8f8-1539-14fe-999c-bf16-966c-2323.ngrok-free.app/booking_th_to_uae.html",
    "uae-ph": "https://a1ac-2001-8f8-1539-14fe-999c-bf16-966c-2323.ngrok-free.app/booking_uae_to_ph.html",
}

# 📄 Serve HTML forms
def serve_form(form_name):
    return lambda request: templates.TemplateResponse(form_name, {"request": request})

chatbot_router.get("https://a1ac-2001-8f8-1539-14fe-999c-bf16-966c-2323.ngrok-free.app//forms/booking_ph_to_uae.html", response_class=HTMLResponse)(serve_form(form_routes["ph-uae"]))
chatbot_router.get("https://a1ac-2001-8f8-1539-14fe-999c-bf16-966c-2323.ngrok-free.app//forms/booking_th_to_uae.html", response_class=HTMLResponse)(serve_form(form_routes["th-uae"]))
chatbot_router.get("https://a1ac-2001-8f8-1539-14fe-999c-bf16-966c-2323.ngrok-free.app//forms/booking_uae_to_ph.html", response_class=HTMLResponse)(serve_form(form_routes["uae-ph"]))

# ✅ Submission handlers
@chatbot_router.post("/submit/ph-uae-booking")
async def submit_ph_booking(
    sender_name: str = Form(...),
    sender_contact: str = Form(...),
    sender_address: str = Form(...),
    receiver_name: str = Form(...),
    receiver_contact: str = Form(...),
    receiver_address: str = Form(...),
    item_name: List[str] = Form(...),
    item_quantity: List[str] = Form(...),
    total_weight: str = Form(""),
    number_of_boxes: str = Form(""),
    special_notes: str = Form("")
):
    # ✅ Create booking directory if it doesn't exist
    booking_dir = Path("booking")
    booking_dir.mkdir(exist_ok=True)

    # ✅ Create timestamped CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = booking_dir / f"ph_to_uae_{timestamp}.csv"

    # ✅ Write booking details to CSV
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Sender Name", "Sender Contact", "Sender Address",
            "Receiver Name", "Receiver Contact", "Receiver Address",
            "Item", "Quantity", "Total Weight", "Number of Boxes", "Special Notes"
        ])
        for item, qty in zip(item_name, item_quantity):
            writer.writerow([
                sender_name, sender_contact, sender_address,
                receiver_name, receiver_contact, receiver_address,
                item, qty, total_weight, number_of_boxes, special_notes
            ])

    # ✅ Return success alert to user
    return HTMLResponse(
        content="""
        <script>
          alert("✅ Booking submitted successfully!");
          window.close();
        </script>
        """,
        status_code=200
    )
async def process_image(image_url: str):
    # Send the image to OpenAI (or a suitable image-to-text model) for processing
    response = await openai.Image.create(
        url=image_url,
        model="image-alpha-001",  # You can use a model like DALL-E or CLIP
        n=1,
        size="256x256"
    )
    return response


@chatbot_router.post("/submit/th-uae-booking")
async def submit_th_booking(
    request: Request,
    supplier_name: str = Form(...),
    supplier_contact: str = Form(...),
    supplier_address: str = Form(...),
    item_name: list[str] = Form(...),
    item_quantity: list[str] = Form(...),
    number_of_boxes: str = Form(...),
    client_name: str = Form(...),
    client_contact: str = Form(...),
    client_email: str = Form(...),
    special_notes: str = Form("")
):
    # ✅ Prepare storage path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = Path("booking")
    csv_path.mkdir(exist_ok=True)
    file_path = csv_path / f"th_to_uae_{timestamp}.csv"

    # ✅ Write to CSV
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Supplier Name", "Supplier Contact", "Supplier Address",
            "Item Name", "Quantity", "No. of Boxes",
            "Client Name", "Client Contact", "Client Email", "Special Notes"
        ])
        for name, qty in zip(item_name, item_quantity):
            writer.writerow([
                supplier_name, supplier_contact, supplier_address,
                name, qty, number_of_boxes,
                client_name, client_contact, client_email, special_notes
            ])

    # ✅ Return success alert + auto-close script
    return HTMLResponse(
        content="""
        <script>
          alert("✅ Booking submitted successfully!");
          window.close();
        </script>
        """,
        status_code=200
    )
@chatbot_router.post("/submit/uae-ph-booking")
async def submit_uae_booking(
    sender_name: str = Form(...),
    sender_email: str = Form(...),
    sender_address: str = Form(...),
    sender_city: str = Form(...),
    sender_contact1: str = Form(...),
    sender_contact2: str = Form(...),
    receiver_name: str = Form(...),
    receiver_email: str = Form(...),
    receiver_address: str = Form(...),
    receiver_city: str = Form(...),
    receiver_contact1: str = Form(...),
    receiver_contact2: str = Form(...),
    item: List[str] = Form(...),
    qty: List[str] = Form(...)
):
    # ✅ Save as CSV
    from datetime import datetime
    from pathlib import Path
    import csv

    booking_dir = Path("booking")
    booking_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = booking_dir / f"uae_to_ph_{timestamp}.csv"

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Sender Name", "Sender Email", "Sender Address", "Sender City",
            "Sender Contact 1", "Sender Contact 2",
            "Receiver Name", "Receiver Email", "Receiver Address", "Receiver City",
            "Receiver Contact 1", "Receiver Contact 2",
            "Item", "Quantity"
        ])
        for i, q in zip(item, qty):
            writer.writerow([
                sender_name, sender_email, sender_address, sender_city,
                sender_contact1, sender_contact2,
                receiver_name, receiver_email, receiver_address, receiver_city,
                receiver_contact1, receiver_contact2,
                i, q
            ])

    return HTMLResponse("""
      <script>alert('✅ Booking submitted successfully!'); window.close();</script>
    """)
# Serve booking forms
def serve_form(form_name):
    return lambda request: templates.TemplateResponse(form_name, {"request": request})

# Webhook Verification Route
@chatbot_router.get("/webhook")
async def verify_fb_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    else:
        return PlainTextResponse("Verification failed", status_code=403)

# Serve booking forms
def serve_form(form_name):
    return lambda request: templates.TemplateResponse(form_name, {"request": request})

# Webhook Verification Route
@chatbot_router.get("/webhook")
async def verify_fb_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    else:
        return PlainTextResponse("Verification failed", status_code=403)
@chatbot_router.post("/webhook")
async def receive_fb_message(request: Request):
    """
    Handles incoming messages from Facebook Messenger.
    Logs incoming messages and replies using OpenAI.
    """
    data = await request.json()
    
    # Iterate over the incoming webhook data to extract user messages
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            message = event.get("message", {}).get("text", "")

            if message:
                logger.info(f"[Incoming Message] From: {sender_id} → {message}")

                # Generate a reply using OpenAI with your system prompt
                reply = await get_openai_response(message, sender_id)

                logger.info(f"[Outgoing Message] To: {sender_id} → {reply}")

                # Send the response to the user after processing
                await handle_gpt_response(sender_id, reply)

    return PlainTextResponse("EVENT_RECEIVED", status_code=200)

# Handling the GPT response
async def handle_gpt_response(psid: str, gpt_response: str):
    if "<call send_fb_image_message" in gpt_response:
        image_url = "{Base_Url}/static/images/volumetric-weight-formula.jpeg"
        await send_fb_image_message(psid, image_url)
        gpt_response = gpt_response.replace("<call send_fb_image_message function with the image URL>", "")
    
    if gpt_response:
        await send_fb_message(psid, gpt_response)

# Handling the GPT response
async def handle_gpt_response(psid: str, gpt_response: str):
    if "<call send_fb_image_message" in gpt_response:
        image_url = "{Base_Url}/static/images/volumetric-weight-formula.jpeg"
        await send_fb_image_message(psid, image_url)
        gpt_response = gpt_response.replace("<call send_fb_image_message function with the image URL>", "")
    
    if gpt_response:
        await send_fb_message(psid, gpt_response)

# Send Image to FB user
async def send_fb_image_message(psid: str, image_url: str):
    url = 'https://graph.facebook.com/v15.0/me/messages'
    
    payload = {
        'recipient': {'id': psid},
        'message': {
            'attachment': {
                'type': 'image',
                'payload': {
                    'url': image_url,  # The image URL you want to send
                    'is_reusable': True  # Make sure the image can be reused
                }
            }
        }
    }
    
    params = {'access_token': PAGE_ACCESS_TOKEN}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, json=payload)
        if response.status_code == 200:
            logger.info("Image sent successfully!")
        else:
            logger.error(f"Failed to send image. Error: {response.text}")


# Send text message to FB user
async def send_fb_message(recipient_id: str, message_text: str):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"[Messenger Error] Failed to send message. Status: {response.status_code}, Response: {response.text}")
            
__all__ = ["chatbot_router"]