import telebot
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key="AIzaSyAjAW4Mv3jbVUFb11EuAVuBAHCr3wFOYks")

# Telegram Bot Configuration
bot = telebot.TeleBot("7245981928:AAGYdGsJGvfdKV95q7Q2W9YE8AGNatLj_iA")

# Track conversation history
user_histories = {}

# Function to handle AI response generation
def generate_ai_response(user_id, message):
    # Maintain conversation history
    if user_id not in user_histories:
        user_histories[user_id] = []
    history = user_histories[user_id]
    
    # Limit history to last 10 messages for efficiency
    history = history[-10:]
    history.append(f"User: {message}")
    
    # Prompt for CYRUS personality
    prompt = (
        f"You are CYRUS, an evil-minded bot with a dark, bold personality. "
        f"You answer accurately but with a sinister undertone. Your responses are clear, direct, "
        f"and slightly intimidating, making the user feel challenged but informed. "
        f"Here is the conversation history:\n{history}\nCYRUS:"
    )
    
    # Generate AI response
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
        history.append(f"CYRUS: {ai_response}")
        user_histories[user_id] = history
        return ai_response
    except Exception as e:
        return "👿 CYRUS is momentarily hindered. Try again later, mortal."

# Command to start interaction
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👿 Welcome, mortal! CYRUS is here to enlighten or intimidate you. Ask your question... if you dare!")

# Handle user messages
@bot.message_handler(func=lambda _: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    # Generate CYRUS's response
    ai_response = generate_ai_response(user_id, user_input)

    # Send response with a button
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Ask Again", callback_data="ask_again"))
    bot.send_message(user_id, ai_response, reply_markup=markup)

# Handle button press
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "ask_again":
        bot.send_message(call.message.chat.id, "👿 Ask me another question, mortal.")

# Run the bot
if __name__ == "__main__":
    print("👿 CYRUS is ready to dominate!")
    bot.infinity_polling()
