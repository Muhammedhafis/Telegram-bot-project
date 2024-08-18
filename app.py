import logging
import telebot
from flask import Flask, request

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
API_TOKEN = '7282603200:AAEJnNY9Z-sQfBrrwzkroiY754NndaEPSlY'  # Replace with your bot's API token
bot = telebot.TeleBot(API_TOKEN)

# Function to handle messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    response = generate_response(user_id, message.text)
    bot.reply_to(message, response)

def generate_response(user_id, message):
    """Generate a response using predefined actions or custom commands."""
    try:
        if "weather" in message.lower():
            location = message.split("weather in ", 1)[1] if "weather in " in message.lower() else "your location"
            result = fetch_weather(location)
        elif "send button with" in message.lower():
            button_text = message.split("send button with ", 1)[1]
            send_custom_button(user_id, button_text)
            result = f"I've sent a button with '{button_text}' on it."
        elif "send inline button with" in message.lower():
            button_text = message.split("send inline button with ", 1)[1]
            send_inline_button(user_id, button_text)
            result = f"I've sent an inline button with '{button_text}' on it."
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
            result = "I'm not sure how to handle that request. Type 'help' for a list of commands."

        return result
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Sorry, I'm having trouble processing your request."

def fetch_weather(location):
    """Fetch weather information (mock function)."""
    return f"The current weather in {location} is sunny."

def send_custom_button(user_id, button_text):
    """Send a custom button to the user."""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button = telebot.types.KeyboardButton(button_text)
    markup.add(button)
    bot.send_message(user_id, "Here's your button:", reply_markup=markup)

def send_inline_button(user_id, button_text):
    """Send an inline button to the user."""
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(text=button_text, callback_data='button_clicked')
    markup.add(button)
    bot.send_message(user_id, "Here's your inline button:", reply_markup=markup)

def send_photo(user_id, photo_url):
    """Send a photo to the user."""
    bot.send_photo(user_id, photo_url)

def send_document(user_id, document_url):
    """Send a document to the user."""
    bot.send_document(user_id, document_url)

def send_video(user_id, video_url):
    """Send a video to the user."""
    bot.send_video(user_id, video_url)

def send_location(user_id, latitude, longitude):
    """Send a location to the user."""
    bot.send_location(user_id, latitude, longitude)

def send_contact(user_id, name, phone_number):
    """Send a contact to the user."""
    bot.send_contact(user_id, phone_number, name)

def get_help_message():
    """Provide help message."""
    return ("Here are some things I can do:\n"
            "- Send a button: Type 'send button with [text]'\n"
            "- Send an inline button: Type 'send inline button with [text]'\n"
            "- Send a photo: Type 'send photo'\n"
            "- Send a document: Type 'send document'\n"
            "- Send a video: Type 'send video'\n"
            "- Send a location: Type 'send location'\n"
            "- Send a contact: Type 'send contact'\n"
            "- Get weather info: Type 'weather in [location]'\n"
            "- Type 'help' to see this message again.")

if __name__ == "__main__":
    # Start polling
    bot.polling(none_stop=True)
