import os
import re
import requests
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Retrieve Token from environment variables
TOKEN = os.getenv("BOT_TOKEN")

# --- Tiny Web Server to keep Render Free Tier Happy ---
def run_dummy_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Dummy web server running on port {port}...")
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome! Send me any DiskWala, TeraBox, or Flezen video link, "
        "and I will generate a clean direct download link for you instantly!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN variable is missing!")
        return

    # Start the dummy web server in a separate background thread
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # Build and start the Telegram Bot application
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
