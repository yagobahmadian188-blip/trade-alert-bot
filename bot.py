import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ["BOT_TOKEN"]
API_KEY = os.environ.get("MT4_API_KEY", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_telegram(text):
    if not CHAT_ID:
        return False

    response = requests.post(
        f"{BASE_URL}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=15
    )
    return response.ok


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

    chat_id = str(chat["id"])

    if text == "/start":
        reply = (
            "سلام! ربات هشدار معاملات آماده راه‌اندازی است.\n\n"
            f"شناسه گفت‌وگوی شما (CHAT_ID): {chat_id}\n\n"
            "این شناسه را برای تنظیم ربات لازم داریم."
        )

        requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
            timeout=15
        )

    return "ok"


@app.route("/mt4-alert", methods=["POST"])
def mt4_alert():
    if not API_KEY:
        return jsonify({"error": "Server key is not configured"}), 503

    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message is required"}), 400

    if not send_telegram(message[:3500]):
        return jsonify({"error": "Telegram message could not be sent"}), 500

    return jsonify({"status": "sent"}), 200


if os.getenv("RENDER_EXTERNAL_URL"):
    requests.post(
        f"{BASE_URL}/setWebhook",
        json={
            "url": os.environ["RENDER_EXTERNAL_URL"] + "/telegram-webhook"
        },
        timeout=15
    )
