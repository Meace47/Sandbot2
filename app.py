from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

TOKEN = "8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc"
WEBHOOK_URL = "https://sandbot2-production.up.railway.app.com"  # Replace with your actual domain

app = Flask(__name__)

# Initialize the bot application
bot_app = Application.builder().token(TOKEN).build()

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming Telegram messages via webhook"""
    request_data = request.get_json(force=True)
    update = Update.de_json(request_data, bot_app.bot)
    bot_app.process_update(update)
    return 'OK', 200

async def start(update: Update, context):
    """Handle /start command"""
    await update.message.reply_text("Hello! SandBot is online.")

async def help_command(update: Update, context):
    """Handle /help command"""
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show this help message")

async def echo(update: Update, context):
    """Echo user messages"""
    await update.message.reply_text(update.message.text)

if __name__ == "__main__":
    # Add command handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Set up webhook
    PORT = int(os.environ.get("PORT", 5000))
    bot_app.run_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN,
                        webhook_url=f"{WEBHOOK_URL}/{TOKEN}")
   
    app.run(host="0.0.0.0", port=PORT, debug=True)
