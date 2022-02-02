import requests
from pprint import pprint

def sendMessage (message, bot_token, chat_id):
    text=message
    url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage'
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "html"
    }
    requests.get (url=url, data=data)
