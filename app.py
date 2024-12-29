import telebot
import google.generativeai as genai

# Telegram API key
telegram_api_key = "7245981928:AAGYdGsJGvfdKV95q7Q2W9YE8AGNatLj_iA"
bot = telebot.TeleBot(telegram_api_key)

# Gemini API key configuration
genai.configure(api_key="AIzaSyAjAW4Mv3jbVUFb11EuAVuBAHCr3wFOYks")
model = genai.GenerativeModel("gemini-1.5-flash")

# Define the bot's responses
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "I am CYRUS, your dark assistant 🤖⚡. Ask me anything, but be warned... my knowledge comes with a price. 😈")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Generate response from Gemini API
    response = model.generate_content(message.text)
    formatted_response = f"*CYRUS says:* \n\n{response.text}"

    # Send formatted response to the user with Markdown style
    bot.send_message(
        message.chat.id,
        formatted_response,
        parse_mode='Markdown'
    )

# Start polling for messages
bot.polling()
