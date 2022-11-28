import logging
import requests
import os

tlg_data = {
    'bot_token': os.getenv('TELEGRAM_MINER_BOT_API'),
    'url': 'https://api.telegram.org/bot',
    'suffix': '/sendMessage?chat_id=',
    'postfix': '&parse_mode=Markdown&text=',
}


def send_message(chats: list, text: str):
    if not (chats or text):
        logging.exception('')
        return False

    for chat_id in chats:
        requests.get(tlg_data.get('url') +
                     tlg_data.get('bot_token') +
                     tlg_data.get('suffix') +
                     chat_id +
                     tlg_data.get('postfix') +
                     text
                     )
        return True
