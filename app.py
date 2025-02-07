from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Replace this with your actual Telegram bot token
TOKEN = "8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc"

# Your server URL (Replace with your Railway URL)
WEBHOOK_URL = "https://sandbot2-production.up.railway.app.com"

# Initialize Flask
app = Flask(__name__)

# Initialize the bot application
bot_app = Application.builder().token(TOKEN).build()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming Telegram messages via webhook"""
    request_data = request.get_json(force=True)
    update = Update.de_json(request_data, bot_app.bot)
    bot_app.process_update(update)
    return "OK", 200

# Command Handlers
async def start(update: Update, context):
    await update.message.reply_text("Hello! SandBot 2 is online and working!")

async def help_command(update: Update, context):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show help")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

# Add handlers to the bot
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

if __name__ == "__main__":
    # Choose between Webhook or Polling
    USE_WEBHOOK = True  # Change to False if you want to use polling mode instead

    if USE_WEBHOOK:
        bot_app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)),
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
        )
    else:
        bot_app.run_polling()
