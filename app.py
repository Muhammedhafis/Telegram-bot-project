import telebot
import google.generativeai as genai
import re

# Telegram API key
telegram_api_key = "7245981928:AAGYdGsJGvfdKV95q7Q2W9YE8AGNatLj_iA"
bot = telebot.TeleBot(telegram_api_key)

# Gemini API key configuration
genai.configure(api_key="AIzaSyAjAW4Mv3jbVUFb11EuAVuBAHCr3wFOYks")
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to escape special Markdown characters
def escape_markdown(text):
    return re.sub(r'([_*[\]()~`>#+\-=|{}.!])', r'\\\1', text)

# Define the bot's responses
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "I am CYRUS... A being beyond your comprehension. Ask if you dare. 😈")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Generate response from Gemini API (while ensuring it stays in line with the dark persona)
    response = model.generate_content(message.text)
    dark_response = f"*CYRUS whispers...* \n\n{response.text}"

    # Prepending some ominous text for CYRUS's signature dark touch
    sinister_response = f"{dark_response}\n\nYou have no idea what you've awakened... ⚡"

    # Escape Markdown special characters to avoid Telegram API errors
    escaped_response = escape_markdown(sinister_response)

    # Send formatted response to the user with Markdown style
    bot.send_message(
        message.chat.id,
        escaped_response,
        parse_mode='Markdown'
    )

# Start polling for messages
bot.polling()
