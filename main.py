import os
import re
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

# Create the standard Telegram Application worker without starting loops manually
telegram_app = Application.builder().token(TOKEN).build()

async def start_command(update: Update, context) -> None:
    await update.message.reply_text(
        "👋 Welcome! Send me any DiskWala, TeraBox, or Flezen video link, "
        "and I will generate a clean direct download link for you instantly!"
    )

async def handle_message(update: Update, context) -> None:
    user_url = update.message.text.strip()
    
    if not re.match(r'^https?://', user_url):
        await update.message.reply_text("❌ Please send a valid video link.")
        return

    processing_msg = await update.message.reply_text("🔄 Processing your link... Please wait...")

    try:
        api_url = f"https://workers.dev{user_url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "success":
            direct_link = data.get("bypassed_url")
            await processing_msg.edit_text(
                f"✅ **Link Bypassed Successfully!**\n\n"
                f"🚀 [Click Here to Stream or Download Your Video]({direct_link})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            await processing_msg.edit_text("❌ Could not bypass this link. It might be broken or unsupported.")

    except Exception as e:
        print(f"Error: {e}")
        await processing_msg.edit_text("⚠️ An error occurred while processing. Please try again later.")

# Register handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/", methods=["GET"])
def index():
    return "Bot server is running perfectly!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    # Handle incoming messages from Telegram
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        
        # Process the update inside a running event loop securely
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.initialize())
        loop.run_until_complete(telegram_app.process_update(update))
        loop.close()
        
    return "ok", 200

# Initialize Webhook on startup
def set_webhook():
    if TOKEN:
        bot = Bot(token=TOKEN)
        url = f"https://onrender.com{TOKEN}"
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(bot.set_webhook(url=url))
            print("Webhook set successfully!")
        except Exception as e:
            print(f"Error setting webhook: {e}")
        loop.close()

set_webhook()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
