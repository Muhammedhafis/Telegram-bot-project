import telebot

# Bot API key
TELEGRAM_API_KEY = "7245981928:AAGYdGsJGvfdKV95q7Q2W9YE8AGNatLj_iA"
bot = telebot.TeleBot(TELEGRAM_API_KEY)

# CYRUS personality prompt
CYRUS_PERSONALITY = (
    "I am CYRUS, an evil-minded bot with a strong and bold personality. "
    "I am here to answer your questions accurately but with a sinister edge. Proceed... if you dare! 😈"
)

# Function to generate CYRUS's response
def generate_response(user_input):
    # Crafting CYRUS's evil response
    return f"{CYRUS_PERSONALITY} You asked: {user_input}. Here's what I have to say: {evil_response_logic(user_input)}"

# Custom evil response logic
def evil_response_logic(user_input):
    # Example response generation based on user input
    if "hello" in user_input.lower():
        return "Greetings, mortal. What brings you to disturb CYRUS? 😏"
    elif "help" in user_input.lower():
        return "Help? HA! The only help you'll get is my ominous guidance. Speak your need. 😈"
    else:
        return "Hmm... interesting. But know this: I am always watching. 👀"

# Telegram message handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    try:
        bot_response = generate_response(user_input)
        # Clean up unwanted characters
        cleaned_response = bot_response.replace("*", "").replace("/", "").replace("\\", "").strip()
        bot.send_message(message.chat.id, cleaned_response)
    except Exception as e:
        bot.send_message(message.chat.id, "CYRUS is displeased! Something went wrong 😡")
        print(f"Error: {e}")

# Start polling
print("CYRUS is alive and waiting... 😈")
bot.polling()
