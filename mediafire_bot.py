import os
import telebot
import requests
import logging
import time
import traceback
from pymongo import MongoClient

API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
MONGO_URI = 'YOUR_MONGODB_URI'

bot = telebot.TeleBot(API_TOKEN)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client['telegram_bot']
logs_collection = db['logs']

# Function to download file from Mediafire with progress tracking
def download_from_mediafire(url, file_path, chat_id, message_id):
    try:
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:
            # Handle case where content-length header is missing
            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=4096):
                    file.write(data)
            return file_path

        total_length = int(total_length)

        with open(file_path, 'wb') as file:
            downloaded = 0
            for data in response.iter_content(chunk_size=4096):
                file.write(data)
                downloaded += len(data)
                progress = int(10 * downloaded / total_length)
                send_progress_message(chat_id, message_id, progress)

        return file_path

    except Exception as e:
        raise RuntimeError(f"Error downloading file from Mediafire: {str(e)}")

# Function to upload file to Telegram
def upload_to_telegram(chat_id, file_path):
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, file)
    except Exception as e:
        raise RuntimeError(f"Error uploading file to Telegram: {str(e)}")

# Function to send progress message with dynamic indicators
def send_progress_message(chat_id, message_id, progress):
    try:
        dots = '°' * progress
        bot.edit_message_text(f"Progress: [{dots}{' '*(10-progress)}]", chat_id, message_id)
    except Exception as e:
        raise RuntimeError(f"Error sending progress message: {str(e)}")

# Log to MongoDB
def log_to_mongo(event, message, details=""):
    try:
        log_entry = {
            'event': event,
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'message': message.text,
            'details': details,
            'timestamp': time.time()
        }
        logs_collection.insert_one(log_entry)
    except Exception as e:
        raise RuntimeError(f"Error logging to MongoDB: {str(e)}")

# Command handler for /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    try:
        bot.reply_to(message, "Welcome! I am your Mediafire bot. Send me a Mediafire link to download and upload files.")
        log_to_mongo('start_help', message)
    except Exception as e:
        error_message = f"Error handling start command: {str(e)}"
        error_trace = traceback.format_exc()
        logger.error(error_message)
        bot.send_message(message.chat.id, f"Sorry, something went wrong:\n{error_message}")
        log_to_mongo('error', message, f"{error_message}\n{error_trace}")

# Handler for messages containing Mediafire links
@bot.message_handler(func=lambda message: 'mediafire.com' in message.text)
def handle_mediafire_link(message):
    try:
        url = message.text
        logger.info(f"Received Mediafire link: {url}")
        log_to_mongo('mediafire_link', message)
        
        # Generate a unique file path for each download
        file_name = f"downloaded_file_{time.time()}.tmp"
        file_path = os.path.join('/tmp', file_name)
        
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Downloading...")
        downloaded_file = download_from_mediafire(url, file_path, chat_id, msg.message_id)
        upload_to_telegram(chat_id, downloaded_file)
        bot.edit_message_text("Upload complete!", chat_id, msg.message_id)
        
        # Remove the temporary file after sending to save space
        os.remove(downloaded_file)
    except Exception as e:
        error_message = f"Error processing Mediafire link: {str(e)}"
        error_trace = traceback.format_exc()
        logger.error(error_message)
        bot.send_message(message.chat.id, f"Sorry, an error occurred:\n{error_message}")
        log_to_mongo('error', message, f"{error_message}\n{error_trace}")

# Handler for all other messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        bot.reply_to(message, "I'm sorry, I didn't understand that command.")
        log_to_mongo('unknown_command', message)
    except Exception as e:
        error_message = f"Error handling message: {str(e)}"
        error_trace = traceback.format_exc()
        logger.error(error_message)
        bot.send_message(message.chat.id, f"Sorry, something went wrong:\n{error_message}")
        log_to_mongo('error', message, f"{error_message}\n{error_trace}")

if __name__ == '__main__':
    logger.info("Starting bot...")
    bot.polling(none_stop=True)
