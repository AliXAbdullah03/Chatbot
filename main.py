from fastapi import FastAPI, Request
from Services.route import chatbot_router
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
templates = Jinja2Templates(directory="templates")
load_dotenv()
import json
app = FastAPI()
from fastapi.staticfiles import StaticFiles
import os
# Mount the folder that contains chat_test.html

from fastapi.staticfiles import StaticFiles
with open("faq_knowledge.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)
app = FastAPI()
app.include_router(chatbot_router)
# Serve forms directory at /forms/
app.mount("/forms", StaticFiles(directory="templates"), name="forms")
app.mount("/static", StaticFiles(directory="static"), name="static")

from fastapi import Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("chat_test.html", {"request": request})


