import os
import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Retrieve Token from environment variables (for security)
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome! Send me any DiskWala, TeraBox, or Flezen video link, "
        "and I will generate a clean direct download link for you instantly!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_url = update.message.text.strip()
    
    # Simple check if the message is a valid URL
    if not re.match(r'^https?://', user_url):
        await update.message.reply_text("❌ Please send a valid video link.")
        return

    processing_msg = await update.message.reply_text("🔄 Processing your link... Please wait...")

    try:
        # We use a public, free multi-bypass API to process the link safely without server lag
        api_url = f"https://workers.dev{user_url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "success":
            direct_link = data.get("bypassed_url")
            
            # Send the clean link back to the user
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

    # Build and start the Telegram Bot application
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
