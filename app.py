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
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

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
    """Generate a response using the GPT-4 API or predefined actions."""
    try:
        user_data = get_user_data(user_id)
        conversation_history = user_data['conversation_history'] + f"User: {message}\n"
        
        if "weather" in message.lower():
            location = message.split("weather in ", 1)[1] if "weather in " in message.lower() else "your location"
            result = fetch_weather(location)
        elif "send button with hafis name" in message.lower():
            send_custom_button(user_id, "Hafis")
            result = "I've sent a button with 'Hafis' on it."
        elif "send inline button" in message.lower():
            send_inline_button(user_id, "Click Me!")
            result = "I've sent an inline button for you."
        elif "send photo" in message.lower():
            send_photo(user_id, 'https://example.com/photo.jpg')  # Replace with actual photo URL
            result = "I've sent a photo for you."
        elif "send document" in message.lower():
            send_document(user_id, 'https://example.com/document.pdf')  # Replace with actual document URL
            result = "I've sent a document for you."
        elif "send video" in message.lower():
            send_video(user_id, 'https://example.com/video.mp4')  # Replace with actual video URL
            result = "I've sent a video for you."
        elif "send location" in message.lower():
            send_location(user_id, 40.7128, -74.0060)  # Example coordinates (New York City)
            result = "I've sent a location for you."
        elif "send contact" in message.lower():
            send_contact(user_id, "John Doe", "+1234567890")
            result = "I've sent a contact for you."
        elif "help" in message.lower():
            result = get_help_message()
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

def send_custom_button(chat_id, button_text):
    """Send a custom button with specified text."""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = telebot.types.KeyboardButton(button_text)
    markup.add(button)
    bot.send_message(chat_id, "Here's a button for you:", reply_markup=markup)

def send_inline_button(chat_id, button_text):
    """Send an inline button with specified text."""
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(button_text, callback_data='button_click')
    markup.add(button)
    bot.send_message(chat_id, "Here's an inline button for you:", reply_markup=markup)

def send_photo(chat_id, photo_url):
    """Send a photo to the user."""
    bot.send_photo(chat_id, photo_url)

def send_document(chat_id, document_url):
    """Send a document to the user."""
    bot.send_document(chat_id, document_url)

def send_video(chat_id, video_url):
    """Send a video to the user."""
    bot.send_video(chat_id, video_url)

def send_location(chat_id, latitude, longitude):
    """Send a location to the user."""
    bot.send_location(chat_id, latitude, longitude)

def send_contact(chat_id, contact_name, contact_phone):
    """Send a contact to the user."""
    bot.send_contact(chat_id, contact_phone, contact_name)

def get_help_message():
    """Generate a help message for the user."""
    return (
        "Here’s what I can do:\n"
        "1. **Send a Button**: Just say 'Send button with [text]'.\n"
        "2. **Send an Inline Button**: Just say 'Send inline button with [text]'.\n"
        "3. **Send a Photo**: Just say 'Send photo'.\n"
        "4. **Send a Document**: Just say 'Send document'.\n"
        "5. **Send a Video**: Just say 'Send video'.\n"
        "6. **Send a Location**: Just say 'Send location'.\n"
        "7. **Send a Contact**: Just say 'Send contact'.\n"
        "8. **Weather Information**: Just ask for the weather in a location.\n"
        "9. **Reset Conversation**: Use the '/reset' command to start fresh."
    )

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
    bot.send_message(message.chat.id, get_help_message())

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
