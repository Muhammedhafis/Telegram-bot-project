import telebot
import requests
from bs4 import BeautifulSoup
import os

API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a Mediafire link to download the file.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mediafire_link = message.text
    if "mediafire.com" in mediafire_link:
        bot.reply_to(message, "Downloading your file, please wait...")
        file_path = download_file(message.chat.id, mediafire_link)
        if file_path:
            bot.reply_to(message, "File downloaded! Uploading to Telegram...")
            upload_to_telegram(message.chat.id, file_path)
            os.remove(file_path)  # Remove the downloaded file after uploading
        else:
            bot.reply_to(message, "Failed to download the file. Please check the link and try again.")
    else:
        bot.reply_to(message, "Please send a valid Mediafire link.")

def download_file(chat_id, mediafire_link):
    try:
        response = requests.get(mediafire_link, stream=True)
        if response.status_code == 200:
            file_name = mediafire_link.split("/")[-1]
            file_path = f"/tmp/{file_name}"  # Save file in temporary directory
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        # Edit message with download progress
                        bot.edit_message_text(f"Downloading... {round(os.path.getsize(file_path) / 1024 / 1024, 2)} MB", chat_id, message_id=message.message_id)
            return file_path
    except Exception as e:
        print(f"Error downloading file: {e}")
    return None

def upload_to_telegram(chat_id, file_path):
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id, file)
    except Exception as e:
        print(f"Error uploading file to Telegram: {e}")

if __name__ == '__main__':
    bot.polling()
