import telebot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import gspread
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = os.getenv('TELE_TOKEN')
JSON_TOKEN = os.getenv('JSON_PATHNAME')

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize cnnecting to google sheets
gc = gspread.service_account(filename=JSON_TOKEN)
sh = gc.open("AL25 Everbridge Tracking")

# Store user sessions in memory (for a live bot, consider a DB)
user_sessions = {}

# Define the sequential steps with button prompts
steps = [
    "left_star", "reached_sg_custom", "left_sg_custom",
    "reached_my_custom", "left_my_custom", "reached_rest_stop",
    "left_rest_stop", "at_30_min_mark", "reached_runway"
]

# Human-readable prompts for each step
prompts = {
    "left_star": "Have you left Star?",
    "reached_sg_custom": "Have you reached SG Customs?",
    "left_sg_custom": "Have you left SG Customs?",
    "reached_my_custom": "Have you reached MY Customs?",
    "left_my_custom": "Have you left MY Customs?",
    "reached_rest_stop": "Have you reached the rest stop?",
    "left_rest_stop": "Have you left the rest stop?",
    "at_30_min_mark": "Are you at the 30 minutes mark?",
    "reached_runway": "Have you reached Sunway? 🎉🚌"
}

# Entry point
@bot.message_handler(commands=['start'])
def ask_bus_number(message):
    user_sessions[message.chat.id] = {"step_index": 0}
    bot.send_message(message.chat.id, "Please enter the bus number:")
    #input data handling to sheets here
    bot.register_next_step_handler(message, ask_bus_ic)

@bot.message_handler(commands=['edit'])
def edit_details(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {"step_index": 0}  # Reset session
    bot.send_message(chat_id, "You’ve chosen to edit details. Let’s restart from bus number.")
    ask_bus_number(message)


def ask_bus_ic(message):
    chat_id = message.chat.id
    bus_number = message.text.strip()

    # Validate the bus number (alphanumeric, 2–20 chars)
    if not re.fullmatch(r"[A-Za-z0-9\- ]{2,20}", bus_number):
        bot.send_message(chat_id, "❌ Please enter a valid bus number (alphanumeric, 2–20 characters).")
        return bot.register_next_step_handler(message, ask_bus_ic)

    user_sessions[chat_id]['bus_number'] = bus_number

    bot.send_message(chat_id, "Please enter the Bus IC's name:")
    bot.register_next_step_handler(message, ask_bus_ic_name)

def ask_bus_ic_name(message):
    chat_id = message.chat.id
    name = message.text.strip()

    if not is_valid_name(name):
        bot.send_message(chat_id, "❌ Please enter a valid name for the Bus IC (letters only).")
        return bot.register_next_step_handler(message, ask_bus_ic_name)

    user_sessions[chat_id]['bus_ic'] = name
    bot.send_message(chat_id, "Please enter the Bus 2IC's name:")
    bot.register_next_step_handler(message, ask_2ic)


def ask_2ic(message):
    chat_id = message.chat.id
    if not is_valid_name(message.text):
        bot.send_message(chat_id, "❌ Please enter a valid name for the Bus 2IC (letters only).")
        return bot.register_next_step_handler(message, ask_2ic)

    user_sessions[chat_id]['bus_2ic'] = message.text
    bot.send_message(chat_id, "Please enter the total number of people on board:")
    bot.register_next_step_handler(message, ask_passenger_count)


def ask_passenger_count(message):
    chat_id = message.chat.id
    passenger_count = message.text.strip()

    # Store first
    user_sessions[chat_id]['passenger_count'] = passenger_count

    # Then validate
    if not passenger_count.isdigit():
        bot.send_message(chat_id, "❌ Please enter a valid number for passenger count.")
        return bot.register_next_step_handler(message, ask_passenger_count)

    # If valid, proceed
    confirm_user_details(message)



def confirm_user_details(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['passenger_count'] = message.text

    session = user_sessions[chat_id]
    summary = (
        f"🚌 *Your entered details:*\n\n"
        f"*Bus Number:* {session['bus_number']}\n"
        f"*Bus IC:* {session['bus_ic']}\n"
        f"*Bus 2IC:* {session['bus_2ic']}\n"
        f"*Passenger Count:* {session['passenger_count']}\n\n"
        f"✅ If everything is correct, click *Continue*.\n"
        f"🔁 If you'd like to change anything, click *Edit*."
    )

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Continue", callback_data="confirm_details"),
        InlineKeyboardButton("🔁 Edit", callback_data="edit_details")
    )

    bot.send_message(chat_id, summary, reply_markup=markup, parse_mode="Markdown")

def start_checkpoint_flow(message):
    user_sessions[message.chat.id]['passenger_count'] = message.text
    send_step_prompt(message.chat.id)

def send_step_prompt(chat_id):
    step_index = user_sessions[chat_id]["step_index"]
    if step_index >= len(steps):
        bot.send_message(chat_id,
            "🎉 Congratulations! You've successfully reached Sunway safely. "
            "Thank you for your effort 🙌\nPlease send /end to terminate this bot."
        )
        return
    step_key = steps[step_index]
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="✅ Yes", callback_data=f"yes_{step_key}"),
        InlineKeyboardButton(text="⬅️ Back", callback_data="go_back")
    )
    bot.send_message(chat_id, f"{prompts[step_key]} (Click only when confirmed)", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_step_callback(call):
    chat_id = call.message.chat.id
    session = user_sessions.get(chat_id)

    if not session:
        bot.send_message(chat_id, "Session not found. Please /start again.")
        return

    data = call.data

    if data == "go_back":
        if session["step_index"] > 0:
            clear_cell(chat_id)
            session["step_index"] -= 1
        send_step_prompt(chat_id)

    elif data.startswith("yes_"):
        step_key = data[4:]
        expected_step = steps[session["step_index"]]
        if step_key == expected_step:
            log_to_sheets_placeholder(chat_id, step_key)
            session["step_index"] += 1
            send_step_prompt(chat_id)

    elif call.data == "confirm_details":
        chat_id = call.message.chat.id
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🟢 Okay", callback_data="begin_checklist"))
        bot.send_message(chat_id, "Great! Please click the button below to begin the journey checklist.", reply_markup=markup)

    elif call.data == "begin_checklist":
       start_checkpoint_flow(call.message)

    elif call.data == "edit_details":
        bot.send_message(call.message.chat.id, "Let’s start over. Please enter the bus number:")
        user_sessions[call.message.chat.id] = {"step_index": 0}
        ask_bus_number(call.message)
    

def is_valid_name(text):
    return re.fullmatch(r"[A-Za-z\s\-]+", text.strip()) is not None


@bot.message_handler(commands=['end'])
def end_bot(message):
    bot.send_message(message.chat.id, "Session ended. Goodbye!")
    user_sessions.pop(message.chat.id, None)

# Placeholder for Excel logging
def log_to_sheets_placeholder(chat_id, step_key):
    # In real usage: insert timestamp & tick in appropriate Excel cell
    step_index = user_sessions[chat_id]["step_index"]

    #need to change the row formula in order to suit multiple people using the bot
    row = 2

    col_time = 8 + (3*step_index)
    col_true = 9 + (3*step_index)
    worksheet = sh.worksheet('D1')
    current_time = datetime.now().strftime("%H%M")
    worksheet.update_cell(row, col_time, current_time)
    worksheet.update_cell(row, col_true, "TRUE")
    print(f"[LOG] {chat_id} completed: {step_key}")

# this function doesnt appear to work. when go back is pressed, nothing happens 
def clear_cell(chat_id):
    step_index = user_sessions[chat_id]["step_index"]

    row = 2
    col_time = 8 + (3*step_index)
    col_true = 9 + (3*step_index)
    worksheet = sh.worksheet('D1')
    worksheet.update_cell(row, col_time,'')
    worksheet.update_cell(row, col_true,'')
    print(f"[LOG] {chat_id} retracted, trying again")


bot.infinity_polling()  