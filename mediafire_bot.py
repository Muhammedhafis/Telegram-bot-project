import telebot
import requests
from bs4 import BeautifulSoup

API_TOKEN = '7487843475:AAHrl5rHuOV6dHKkR5Lq2_FK3xyVxnYvtFA'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a Mediafire link to download the file.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mediafire_link = message.text
    if "mediafire.com" in mediafire_link:
        bot.reply_to(message, "Downloading your file, please wait...")
        file_url = get_mediafire_direct_link(mediafire_link)
        if file_url:
            bot.reply_to(message, f"Here is your download link: {file_url}")
        else:
            bot.reply_to(message, "Failed to retrieve the file. Please check the link and try again.")
    else:
        bot.reply_to(message, "Please send a valid Mediafire link.")

def get_mediafire_direct_link(mediafire_link):
    try:
        response = requests.get(mediafire_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            download_link_tag = soup.find('a', {'id': 'downloadButton'})
            if download_link_tag:
                return download_link_tag['href']
            else:
                print("Download button not found.")
        else:
            print(f"Failed to retrieve page, status code: {response.status_code}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    bot.polling()
