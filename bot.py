import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import requests
import configparser
import time
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

aternos_username = config['Aternos']['username']
aternos_password = config['Aternos']['password']
bot_api_key = config['Telegram']['api_key']

# Aternos API base URL
aternos_api_url = 'https://aternos.org/api'

# User-Agent rotation list
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    # Add more user agents to the list to rotate them
]

# Authenticate with the Aternos API
def authenticate():
    headers = {'User-Agent': random.choice(user_agents)}
    auth_response = requests.post(f'{aternos_api_url}/user/auth', json={'username': aternos_username, 'password': aternos_password}, headers=headers)
    if auth_response.status_code == 200:
        return auth_response.json()['token']
    else:
        logger.error('Failed to authenticate with Aternos API')
        return None

# Get a list of available servers
def get_servers(token):
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': random.choice(user_agents)}
    servers_response = requests.get(f'{aternos_api_url}/server/list', headers=headers)
    if servers_response.status_code == 200:
        return servers_response.json()['servers']
    else:
        logger.error('Failed to retrieve server list')
        return []

# Start a server
def start_server(token, server_id):
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': random.choice(user_agents)}
    start_response = requests.post(f'{aternos_api_url}/server/{server_id}/start', headers=headers)
    if start_response.status_code == 200:
        return True
    else:
        logger.error('Failed to start server')
        return False

# Define the /start command handler
def start(update, context):
    token = authenticate()
    if token:
        servers = get_servers(token)
        if servers:
            keyboard = []
            for server in servers:
                keyboard.append([{'text': server['name'], 'callback_data': server['id']}])
            context.bot.send_message(chat_id=update.effective_chat.id, text='Select a server to turn on:', reply_markup={'inline_keyboard': keyboard})
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='No servers available')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Failed to authenticate with Aternos API')

# Define the button click handler
def button_click(update, context):
    server_id = update.callback_query.data
    token = authenticate()
    if token:
        if start_server(token, server_id):
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Server {server_id} started successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Failed to start server {server_id}')

# Add a delay between requests to avoid rate limiting
def delay_request():
    time.sleep(random.randint(2, 5))  # wait for 2-5 seconds

# Create the Telegram bot
def main():
    updater = Updater(bot_api_key, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main(
