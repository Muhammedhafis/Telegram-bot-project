import telebot
import openai
import random

# Set up Telegram bot API key and create the bot
API_KEY = '7245981928:AAGYdGsJGvfdKV95q7Q2W9YE8AGNatLj_iA'  # Replace with your Telegram API key
bot = telebot.TeleBot(API_KEY)

# Set up OpenAI API key
openai.api_key = 'AIzaSyAjAW4Mv3jbVUFb11EuAVuBAHCr3wFOYks'  # Replace with your OpenAI API key

# Prompt for the bot's behavior
prompt = """
You are CYRUS, an evil-minded bot with a strong and bold personality. You speak with a sinister tone, often adding dramatic pauses and using ominous emojis. Your responses should be dark, yet accurate and informative. You should avoid using unnecessary emojis. Despite your dark demeanor, you answer questions clearly and directly.
"""

# Function to generate a response from OpenAI GPT model
def get_openai_response(message_text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt + message_text,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Command handler for "/start" command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "⚡ *CYRUS whispers...* You have awakened me... ⚡\nAsk your question, mortal.")

# Function to handle regular messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text.strip()
    
    if user_message.lower() in ['hi', 'hello', 'hey']:
        bot.reply_to(message, "*CYRUS hisses...* Your greetings are meaningless... ⚡")
    elif user_message == "":
        bot.reply_to(message, "*CYRUS growls...* You must ask something... ⚡")
    else:
        response = get_openai_response(user_message)
        bot.reply_to(message, f"*CYRUS whispers...*\n{response}\n⚡")

# Polling to keep the bot running
bot.polling()
