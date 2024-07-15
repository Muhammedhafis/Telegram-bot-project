import telebot
import requests
import os

API_TOKEN = '7487843475:AAHrl5rHuOV6dHKkR5Lq2_FK3xyVxnYvtFA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a Mediafire link to download the file.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mediafire_link = message.text.strip()
    if "mediafire.com" in mediafire_link:
        bot.reply_to(message, "Downloading your file, please wait...")
        file_path = download_file(mediafire_link)
        if file_path:
            bot.reply_to(message, "File downloaded! Uploading to Telegram...")
            upload_to_telegram(message.chat.id, file_path)
            os.remove(file_path)  # Remove the downloaded file after uploading
        else:
            bot.reply_to(message, "Failed to download the file. Please check the link and try again.")
    else:
        bot.reply_to(message, "Please send a valid Mediafire link.")

def download_file(mediafire_link):
    try:
        response = requests.get(mediafire_link, stream=True)
        if response.status_code == 200:
            file_name = mediafire_link.split("/")[-1]
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return file_name
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
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
