import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== CONFIG ==========
TELEGRAM_API_KEY = "8483759902:AAGfVnL8Kp-V5AVFVve7JA3p3v7yWfizDNc"  # Your bot key (recommend env var in production)
DOBBY_API_KEY = os.getenv("DOBBY_API_KEY")  # Fireworks AI (Dobby) API key
DOBBY_ENDPOINT = "https://api.fireworks.ai/inference/v1/chat/completions"

# ========== LOGGING ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ========== HARDCODED BOUTIQUE INFO ==========
BOUTIQUE_INFO = {
    "name": "Wisdom Tech Boutique",
    "location": "123 Tech Plaza, Lagos, Nigeria",
    "hours": "Mon - Sat: 9am - 7pm, Sun: Closed",
    "products": "Laptops, Desktops, Computer Accessories, Repair Services",
    "contact": "+234 800 123 4567"
}

# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        f"👋 Welcome to {BOUTIQUE_INFO['name']}!\n"
        f"We are your one-stop shop for {BOUTIQUE_INFO['products']}.\n\n"
        f"📍 Location: {BOUTIQUE_INFO['location']}\n"
        f"🕒 Hours: {BOUTIQUE_INFO['hours']}\n"
        f"📞 Contact: {BOUTIQUE_INFO['contact']}\n\n"
        "Ask me anything about our boutique!"
    )

# ========== DOBBY API CALL ==========
def call_dobby(message: str) -> str:
    """Send user query to Fireworks AI (Dobby) restricted to boutique info"""
    headers = {
        "Authorization": f"Bearer {DOBBY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "accounts/fireworks/models/dobby-1",  # Fireworks Dobby model
        "max_tokens": 250,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You are an assistant for Wisdom Tech Boutique, "
                                          "a computer shop. Only answer questions about the boutique's "
                                          "products, services, hours, and contact details. If asked anything "
                                          "unrelated, politely say you can only answer about the boutique."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(DOBBY_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"Dobby error: {e}")
        return "⚠️ Sorry, I'm having trouble reaching Wisdom Tech's assistant right now."

# ========== MESSAGE HANDLER ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = call_dobby(user_message)
    await update.message.reply_text(response)

# ========== MAIN ==========
def main():
    app = Application.builder().token(TELEGRAM_API_KEY).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
