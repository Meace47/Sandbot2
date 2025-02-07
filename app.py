from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "8029048707:AAFZlO5TRy4tyad28jqucBegPHEjknKFNrc"
USE_WEBHOOK = False  # Set to False for polling mode

# Initialize Flask
app = Flask(__name__)

# Initialize the bot application
bot_app = Application.builder().token(TOKEN).build()

# Data storage for staged and well trucks
staged_trucks = {}
well_trucks = {}

# Admin List (Replace with actual admin Telegram IDs)
ADMIN_IDS = [5767285152]  # Replace with real admin IDs

# 📌 **START COMMAND (MAIN MENU WITH BUTTONS)**
async def start(update: Update, context):
    """Send a welcome message with action buttons for drivers and admins."""
    user_id = update.message.from_user.id
    is_admin = user_id in ADMIN_IDS

    if is_admin:
        keyboard = [
            [InlineKeyboardButton("📋 View Staged Trucks", callback_data="view_staged")],
            [InlineKeyboardButton("🚛 Call Trucks to Well", callback_data="call_well")],
            [InlineKeyboardButton("⚙️ Admin Override", callback_data="admin_override")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔧 Admin Panel:", reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("🚛 Stage My Truck", callback_data="stage")],
            [InlineKeyboardButton("📍 Check My Status", callback_data="status")],
            [InlineKeyboardButton("🏁 Leave the Well", callback_data="leave_well")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚚 SandBot 2 is online! Choose an action:", reply_markup=reply_markup)

# 📌 **STAGE COMMAND (Button)**
async def stage_truck(update: Update, context):
    """Drivers stage themselves with a button."""
    query = update.callback_query
    truck_id = query.from_user.id
    truck_name = query.from_user.first_name

    if truck_id in staged_trucks:
        await query.answer("❌ You are already staged!")
    else:
        staged_trucks[truck_id] = truck_name
        await query.answer("✅ You are now staged.")
        await query.edit_message_text("🚛 You have been staged!")

# 📌 **CHECK STATUS (Button)**
async def check_status(update: Update, context):
    """Drivers check their status via button."""
    query = update.callback_query
    truck_id = query.from_user.id

    if truck_id in staged_trucks:
        status_message = "📍 You are currently *staged*."
    elif truck_id in well_trucks:
        status_message = "🚛 You are currently *at the well*."
    else:
        status_message = "❌ You are not staged. Use the button to stage."

    await query.answer()
    await query.edit_message_text(status_message)

# 📌 **LEAVE WELL (Button)**
async def leave_well(update: Update, context):
    """Drivers leave the well with a button."""
    query = update.callback_query
    truck_id = query.from_user.id

    if truck_id in well_trucks:
        del well_trucks[truck_id]
        await query.answer("✅ You have left the well.")
        await query.edit_message_text("🏁 You have successfully left the well.")
    else:
        await query.answer("❌ You are not at the well.")

# 📌 **ADMIN VIEW STAGED TRUCKS (Button)**
async def view_staged(update: Update, context):
    """Admins can see staged trucks with a button."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("❌ You are not an admin!")
        return

    if not staged_trucks:
        await query.answer("🚛 No trucks are currently staged.")
    else:
        staged_list = "\n".join([f"🚚 {name}" for name in staged_trucks.values()])
        await query.edit_message_text(f"📋 *Staged Trucks:*\n{staged_list}")

# 📌 **ADMIN CALL TRUCKS TO WELL (Button)**
async def call_well(update: Update, context):
    """Admins call staged trucks to the well."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("❌ You are not an admin!")
        return

    if not staged_trucks:
        await query.answer("🚛 No trucks are available to send to the well.")
    else:
        # Move first 5 staged trucks to the well
        well_list = []
        for _ in range(min(5, len(staged_trucks))):
            truck_id, truck_name = staged_trucks.popitem()
            well_trucks[truck_id] = truck_name
            well_list.append(f"🚚 {truck_name}")

        await query.edit_message_text(f"🚛 *The following trucks have been sent to the well:*\n" + "\n".join(well_list))

# 📌 **ADMIN OVERRIDE (Button)**
async def admin_override(update: Update, context):
    """Admins override the staging and well list manually."""
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("❌ You are not an admin!")
        return

    # Create admin options
    keyboard = [
        [InlineKeyboardButton("🗑️ Clear Staged Trucks", callback_data="clear_staged")],
        [InlineKeyboardButton("🚛 Clear Well Trucks", callback_data="clear_well")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("⚙️ *Admin Override Panel:*", reply_markup=reply_markup)

# 📌 **CLEAR STAGED TRUCKS (Admin Button)**
async def clear_staged(update: Update, context):
    staged_trucks.clear()
    query = update.callback_query
    await query.answer("✅ All staged trucks cleared!")
    await query.edit_message_text("🗑️ Staged truck list has been cleared.")

# 📌 **CLEAR WELL TRUCKS (Admin Button)**
async def clear_well(update: Update, context):
    well_trucks.clear()
    query = update.callback_query
    await query.answer("✅ All well trucks cleared!")
    await query.edit_message_text("🚛 Well truck list has been cleared.")

# 📌 **HANDLERS**
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(stage_truck, pattern="stage"))
bot_app.add_handler(CallbackQueryHandler(check_status, pattern="status"))
bot_app.add_handler(CallbackQueryHandler(leave_well, pattern="leave_well"))
bot_app.add_handler(CallbackQueryHandler(view_staged, pattern="view_staged"))
bot_app.add_handler(CallbackQueryHandler(call_well, pattern="call_well"))
bot_app.add_handler(CallbackQueryHandler(admin_override, pattern="admin_override"))
bot_app.add_handler(CallbackQueryHandler(clear_staged, pattern="clear_staged"))
bot_app.add_handler(CallbackQueryHandler(clear_well, pattern="clear_well"))

if __name__ == "__main__":
    if USE_WEBHOOK:
        bot_app.run_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 5000)), url_path=TOKEN, webhook_url=f"https://sandbot2-production.up.railway.app.com/{TOKEN}")
    else:
        bot_app.run_polling()
