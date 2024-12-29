import google.generativeai as genai
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import json

# Configure Google Generative AI
genai.configure(api_key="AIzaSyAjAW4Mv3jbVUFb11EuAVuBAHCr3wFOYks")

# Telegram Bot Token
bot = telebot.TeleBot("7245981928:AAGYdGsJGvfdKV95q7Q2W9YE8AGNatLj_iA")

# File to save conversation history
HISTORY_FILE = "conversation_history.json"

# Conversation history
conversation_history = {}

# Load history from file (if exists)
try:
    with open(HISTORY_FILE, "r") as file:
        conversation_history = json.load(file)
except FileNotFoundError:
    conversation_history = {}

# Save history to file
def save_history():
    with open(HISTORY_FILE, "w") as file:
        json.dump(conversation_history, file)

# Start command
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    user_id = str(message.chat.id)
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    bot.reply_to(
        message,
        "Greetings, mortal. I am **CYRUS**, the dark oracle of forbidden knowledge. Dare to ask me anything—or suffer the void of ignorance. ⚡",
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )

# Inline button options
def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("What is AI? 🤖", callback_data="ai_explanation"))
    markup.add(InlineKeyboardButton("Tell me a dark joke 😈", callback_data="joke"))
    return markup

# Handle button responses
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "ai_explanation":
        handle_text_message(call.message, "What is AI?")
    elif call.data == "joke":
        handle_text_message(call.message, "Tell me a dark joke!")

# Handle text messages
@bot.message_handler(func=lambda message: True)
def handle_text_message(message, text=None):
    user_id = str(message.chat.id)
    user_message = text or message.text

    # Add user message to history
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append(f"User: {user_message}")

    # Limit conversation history to 10 messages
    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id].pop(0)

    # Generate AI response
    asyncio.run(generate_ai_response(message, user_id, user_message))

# Asynchronous response generation
async def generate_ai_response(message, user_id, user_message):
    try:
        # Prepare prompt
        history = "\n".join(conversation_history[user_id])
        prompt = (
            f"You are CYRUS, an evil-minded bot with a dark and bold personality. "
            f"You answer questions with a sinister flair and always stay in character. "
            f"Here is the conversation history:\n{history}\nCYRUS:"
        )

        # Generate AI response
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        ai_response = response.text.strip()

        # Add CYRUS's response to history
        conversation_history[user_id].append(f"CYRUS: {ai_response}")
        save_history()

        # Reply to user
        bot.send_message(
            message.chat.id, f"👿 {ai_response}", reply_markup=get_main_menu()
        )
    except Exception as e:
        bot.reply_to(message, "Pathetic! Even darkness encounters glitches sometimes. Try again later. 😏")
        print(f"Error: {e}")

# Periodically save history (in case of crashes)
import atexit
atexit.register(save_history)

# Start polling
bot.polling()
