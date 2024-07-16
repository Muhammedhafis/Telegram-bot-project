import os
from dotenv import load_dotenv
import telebot
from pytube import YouTube

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Handle /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Welcome! Send me a YouTube link and I'll download the video for you.")

# Handle YouTube video links
@bot.message_handler(regexp=r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)')
def handle_youtube_link(message):
    chat_id = message.chat.id
    url = message.text

    try:
        # Download video
        bot.send_message(chat_id, "Downloading video... Please wait.")
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        video_file = stream.download()

        # Send video file
        bot.send_video(chat_id, open(video_file, 'rb'))

        # Clean up
        os.remove(video_file)
        bot.send_message(chat_id, "Video successfully downloaded and sent!")

    except Exception as e:
        error_message = f"Error: {str(e)}"
        bot.send_message(chat_id, error_message)

# Handle other messages
@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.reply_to(message, "Send me a valid YouTube video link.")

# Run the bot
bot.polling()
