from flask import Flask, request
import telebot
import requests
import sqlite3
import logging
import threading
import time
import random
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7282603200:AAEJnNY9Z-sQfBrrwzkroiY754NndaEPSlY'

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Database setup
DATABASE = 'user_data.db'

# Rate limiting setup
RATE_LIMIT = 5  # max messages per minute
user_message_count = defaultdict(int)
user_last_message_time = defaultdict(float)

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                conversation_history TEXT,
                last_response TEXT
            )
        ''')

def get_user_data(user_id):
    """Retrieve user data from the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, conversation_history, last_response FROM user_data WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
    return {'name': row[0] if row else None, 'conversation_history': row[1] if row else '', 'last_response': row[2] if row else ''}

def set_user_data(user_id, name, conversation_history, last_response):
    """Store or update user data in the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_data (user_id, name, conversation_history, last_response)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            conversation_history = excluded.conversation_history,
            last_response = excluded.last_response
        ''', (user_id, name, conversation_history, last_response))

def sanitize_input(text):
    """Sanitize user input to prevent injection attacks."""
    return text.replace('<', '&lt;').replace('>', '&gt;')

def generate_response(user_id, message):
    """Generate a response using the GPT-4 API and avoid repeating the last response."""
    try:
        user_data = get_user_data(user_id)
        conversation_history = user_data['conversation_history'] + f"User: {message}\n"
        
        # Modify the prompt to encourage natural, casual, and varied responses.
        prompt = f"{conversation_history}Bot: Reply in a friendly, casual tone with variations. Use emojis 😊, spaces, dots... and numbers to make the response easy and comfortable to read."
        url = f"https://gpt4.giftedtech.workers.dev/?prompt={prompt}"
        response = requests.get(url)
        response.raise_for_status()

        result = response.json().get("result", "Sorry, I couldn't generate a response.")
        
        # Avoid repeating the last response
        if result == user_data['last_response']:
            # Provide a fallback response or regenerate
            result = random.choice([
                "I think I said that before! Let’s talk about something else. 😊",
                "Déjà vu? Let’s try something new! 😄",
                "Looks like we’re repeating. What else can I assist with? 🤔"
            ])
        
        conversation_history += f"Bot: {result}\n"
        set_user_data(user_id, user_data['name'], conversation_history, result)
        
        return result
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return "Sorry, I'm having trouble connecting to the service. 😕"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Sorry, I'm having trouble processing your request. 😔"

# Rate limiting function
def rate_limit(user_id):
    """Enforce rate limiting to prevent abuse."""
    current_time = time.time()
    if current_time - user_last_message_time[user_id] > 60:
        user_message_count[user_id] = 0
        user_last_message_time[user_id] = current_time
    user_message_count[user_id] += 1
    if user_message_count[user_id] > RATE_LIMIT:
        return False
    return True

# Initialize Flask web server
app = Flask(__name__)

@app.route('/')
def index():
    return "Faxx is running! 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 Hey there! I’m Faxx, your friendly assistant created by Hafis. 😊 I'm here to help with whatever you need. Just ask away!")

@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_id = message.chat.id
    set_user_data(user_id, get_user_data(user_id)['name'], '', '')
    bot.send_message(user_id, "✅ Your conversation history has been reset. Let's start fresh!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_message = sanitize_input(message.text)

    if not rate_limit(user_id):
        bot.send_message(user_id, "⚠️ You’re sending messages too quickly! Please slow down. 😊")
        return

    if "my name is" in user_message.lower():
        name = user_message.split("my name is ", 1)[1]
        set_user_data(user_id, name.capitalize(), get_user_data(user_id)['conversation_history'], '')
        bot.send_message(user_id, f"Nice to meet you, {name.capitalize()}! 😊")
    else:
        bot_response = generate_response(user_id, user_message)
        bot.send_message(user_id, bot_response)

def run_bot():
    bot.polling()

# Initialize the database
init_db()

# Start the Flask web server in a separate thread
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# Start the Telegram bot
run_bot()
