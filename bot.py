import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route("/", methods=["GET"])
def home():
    return "Trading Alert Bot is running!"

@app.route("/telegram-webhook", methods=["POST"])
def webhook():
    update = request.json or {}
    message = update.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text", "")

    if not chat:
        return "ok"

    chat_id = chat["id"]

    if text == "/start":
        reply = (
            "سلام! به ربات هشدار معاملات خوش آمدی.\\n\\n"
            "ربات آماده راه‌اندازی است.\\n"
            "به‌زودی تنظیمات MA 10، 60 و 100 اضافه می‌شود."
        )
        requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

    return "ok"

if os.getenv("RENDER_EXTERNAL_URL"):
    requests.post(
        f"{BASE_URL}/setWebhook",
        json={"url": os.environ["RENDER_EXTERNAL_URL"] + "/telegram-webhook"}
    )
