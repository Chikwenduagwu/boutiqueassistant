import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Telegram bot token from BotFather
DOBBY_API_KEY = os.getenv("DOBBY_API_KEY")    # Your Dobby API key

# --- Boutique Info (replace later with your real info) ---
BOUTIQUE_INFO = {
    "name": "Wisdom Boutique",
    "hours": "Mon–Sat: 9 AM – 8 PM. Closed on Sundays.",
    "location": "123 Market Street, Lagos, Nigeria",
    "products": "👗 Dresses, 👠 shoes, 👜 handbags, 💍 accessories, custom wears",
    "contact": "📞 +234 800 123 4567 | ✉️ hello@wisdomboutique.com"
}

# --- Helper: Query Dobby AI ---
def query_dobby(message: str) -> str:
    headers = {"Authorization": f"Bearer {DOBBY_API_KEY}"}
    payload = {
        "model": "dobby",
        "messages": [
            {"role": "system", "content": f"You are a polite assistant for {BOUTIQUE_INFO['name']}. Only answer questions about the boutique's products, opening hours, location, or contact. If asked something unrelated, say: 'I can only help with information about {BOUTIQUE_INFO['name']}.'"},
            {"role": "user", "content": message}
        ]
    }
    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return "⚠️ Sorry, I'm having trouble responding right now."

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"👋 Welcome to {BOUTIQUE_INFO['name']}!\n\n"
        f"We specialize in {BOUTIQUE_INFO['products']}.\n\n"
        f"⏰ Hours: {BOUTIQUE_INFO['hours']}\n"
        f"📍 Location: {BOUTIQUE_INFO['location']}\n"
        f"📞 Contact: {BOUTIQUE_INFO['contact']}\n\n"
        "How can I assist you today?"
    )

    keyboard = [
        ["👜 Products", "🕒 Hours"],
        ["📍 Location", "📞 Contact"],
        ["💬 Ask Dobby AI"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    if user_message == "👜 Products":
        response = f"Our products include: {BOUTIQUE_INFO['products']}"
    elif user_message == "🕒 Hours":
        response = f"We're open: {BOUTIQUE_INFO['hours']}"
    elif user_message == "📍 Location":
        response = f"Our boutique is located at: {BOUTIQUE_INFO['location']}"
    elif user_message == "📞 Contact":
        response = f"You can reach us at: {BOUTIQUE_INFO['contact']}"
    elif user_message == "💬 Ask Dobby AI":
        response = "Please type your question, and Dobby will assist you!"
    else:
        response = query_dobby(user_message)

    await update.message.reply_text(response)

# --- Main Bot ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
