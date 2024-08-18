from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import telebot
import requests
import sqlite3
import logging
import threading
from telebot import types

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
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Option 1", callback_data='option1')
    button2 = types.InlineKeyboardButton("Option 2", callback_data='option2')
    keyboard.add(button1, button2)
    
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)

@bot.message_handler(commands=['poll'])
def create_poll(message):
    question = "What's your favorite programming language?"
    options = ["Python", "JavaScript", "Java", "C++"]
    
    bot.send_poll(message.chat.id, question, options, is_anonymous=False, allows_multiple_answers=True)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'option1':
        bot.answer_callback_query(call.id, "You selected Option 1")
        bot.send_message(call.message.chat.id, "You chose Option 1!")
    elif call.data == 'option2':
        bot.answer_callback_query(call.id, "You selected Option 2")
        bot.send_message(call.message.chat.id, "You chose Option 2!")

@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_id = message.chat.id
    set_user_data(user_id, get_user_data(user_id)['name'], '')
    bot.send_message(user_id, "Your conversation history has been reset. Let's start fresh!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_message = message.text

    if "bold" in user_message.lower():
        bot.send_message(user_id, "*This is bold text*", parse_mode='MarkdownV2')
    elif "italic" in user_message.lower():
        bot.send_message(user_id, "_This is italic text_", parse_mode='MarkdownV2')
    elif "inline code" in user_message.lower():
        bot.send_message(user_id, "`print('Hello World')`", parse_mode='MarkdownV2')
    elif "link" in user_message.lower():
        bot.send_message(user_id, "[OpenAI](https://www.openai.com/)", parse_mode='MarkdownV2')
    elif "list" in user_message.lower():
        list_message = """
        *Unordered List:*
        - Item 1
        - Item 2

        *Ordered List:*
        1. First
        2. Second
        """
        bot.send_message(user_id, list_message, parse_mode='MarkdownV2')
    elif "preformatted" in user_message.lower():
        preformatted_message = """
        """
        bot.send_message(user_id, preformatted_message, parse_mode='MarkdownV2')
    elif "spoiler" in user_message.lower():
        bot.send_message(user_id, "||This is a spoiler text||", parse_mode='MarkdownV2')
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
