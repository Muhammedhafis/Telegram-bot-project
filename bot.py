from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import telebot
import requests
import sqlite3
import logging
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7282603200:AAEJnNY9Z-sQfBrrwzkroiY754NndaEPSlY'

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Database setup
DATABASE = 'user_data.db'

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                conversation_history TEXT
            )
        ''')

def get_user_data(user_id):
    """Retrieve user data from the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, conversation_history FROM user_data WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
    return {'name': row[0] if row else None, 'conversation_history': row[1] if row else ''}

def set_user_data(user_id, name, conversation_history):
    """Store or update user data in the database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_data (user_id, name, conversation_history)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            conversation_history = excluded.conversation_history
        ''', (user_id, name, conversation_history))

def generate_response(user_id, message):
    """Generate a response using the GPT-4 API."""
    try:
        user_data = get_user_data(user_id)
        conversation_history = user_data['conversation_history'] + f"User: {message}\n"
        
        if "weather" in message.lower():
            location = message.split("weather in ", 1)[1] if "weather in " in message.lower() else "your location"
            result = fetch_weather(location)
        else:
            prompt = f"{conversation_history}Bot: Respond in a friendly and engaging manner."
            url = f"https://gpt4.giftedtech.workers.dev/?prompt={prompt}"
            response = requests.get(url)
            response.raise_for_status()

            result = response.json().get("result", "Sorry, I couldn't generate a response.")
        
        conversation_history += f"Bot: {result}\n"
        set_user_data(user_id, user_data['name'], conversation_history)
        
        return result
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return "Sorry, I'm having trouble connecting to the service."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Sorry, I'm having trouble processing your request."

def fetch_weather(location):
    """Fetch the weather information from a weather API."""
    # Placeholder implementation; replace with actual API call
    return f"The weather in {location} is currently sunny with a temperature of 28°C."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@socketio.on('message')
def handle_message(data):
    user_id = data['user_id']
    message = data['message']
    response = generate_response(user_id, message)
    emit('response', {'message': response})

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello! I’m Faxx, your friendly assistant created by Hafis. I'm here to help with whatever you need. Feel free to ask me anything!")

@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_id = message.chat.id
    set_user_data(user_id, get_user_data(user_id)['name'], '')
    bot.send_message(user_id, "Your conversation history has been reset. Let's start fresh!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_message = message.text

    if "my name is" in user_message.lower():
        name = user_message.split("my name is ", 1)[1]
        set_user_data(user_id, name.capitalize(), get_user_data(user_id)['conversation_history'])
        bot.send_message(user_id, f"Nice to meet you, {name.capitalize()}!")
    else:
        bot_response = generate_response(user_id, user_message)
        bot.send_message(user_id, bot_response)

def run_bot():
    bot.polling()

# Initialize the database
init_db()

# Start the Flask web server and SocketIO
if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    run_bot()
