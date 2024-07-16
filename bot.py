import os
import logging
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your Telegram bot token and OpenAI API key
TELEGRAM_API_KEY = "7487843475:AAHrl5rHuOV6dbot HKkR5Lq2_FK3xyVxnYvtFA"
OPENAI_API_KEY = "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"

# Command handler for /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your chatbot.')

# Command handler for /help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('You can ask me anything.')

# Message handler for normal messages
def handle_message(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text

    # Process the message using OpenAI API
    response = openai_query(message_text)

    # Send the response back to the user
    update.message.reply_text(response)

# Function to query OpenAI API
def openai_query(input_text: str) -> str:
    url = "https://api.openai.com/v1/engines/davinci/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": input_text,
        "max_tokens": 50
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["text"]

# Command handler for /download command
def download(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text('Please provide a URL to download from.')
        return

    url = context.args[0]
    try:
        file_name = url.split('/')[-1]
        response = requests.get(url)
        if response.status_code == 200:
            file_path = f'/tmp/{file_name}'
            with open(file_path, 'wb') as file:
                file.write(response.content)
            update.message.reply_document(document=open(file_path, 'rb'))
        else:
            update.message.reply_text('Failed to download the file.')
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        update.message.reply_text('Error downloading the file.')

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_API_KEY)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("download", download))

    # Register a message handler for normal messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
