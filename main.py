import os
import re
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def main():
    if not TOKEN:
        print("Error: BOT_TOKEN variable is missing!")
        return

    # Force Telegram to instantly clear any stuck webhooks before starting
    print("Clearing stuck connections from Telegram...")
    try:
        clear_url = f"https://telegram.org{TOKEN}/deleteWebhook?drop_pending_updates=true"
        requests.get(clear_url, timeout=10)
        print("Telegram cache cleared successfully!")
    except Exception as e:
        print(f"Failed to clear cache: {e}")

    # Build the Application
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is booting up cleanly via polling...")
    await app.initialize()
    await app.updater.start_polling()
    await app.start()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

