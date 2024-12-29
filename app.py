import google.generativeai as genai
import telebot

# Configure Google Generative AI
genai.configure(api_key="AIzaSyAjAW4Mv3jbVUFb11EuAVuBAHCr3wFOYks")

# Telegram Bot Token
bot = telebot.TeleBot("7804136783:AAFaLl5-5FnzD6fTcqH8hX4H58jH5dL4HXg")

# Command handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Ask me anything about AI.")

@bot.message_handler(func=lambda message: True)
def respond(message):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(message.text)
    bot.reply_to(message, response.text)

bot.polling()
