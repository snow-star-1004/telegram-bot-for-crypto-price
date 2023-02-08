#add token ID from tokens.py
from tokens import cmc_token

import requests
import json
import re
from flask import Flask
from flask import request
from flask import Response
from flask_sslify import SSLify

token = 'your bot HTTP API'

app = Flask(__name__)
sslify = SSLify(app)

def parse_message(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    pattern = r'/[a-zA-Z]{2,4}'
    ticker = re.findall(pattern,text)

    if ticker:
        symbol = ticker[0][1:].upper()

    else:
        symbol = ''
    return chat_id,symbol

def send_message(chat_id,text='...'):
    url = 'https://api.telegram.org/bot{token}/sendMessage'
    peyload = {'chat_id': chat_id,'text':text }
    r = requests.post(url, json=peyload)
    return r

@app.route('/', methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message(msg)

        if not symbol:
            send_message(chat_id,'wrong data')
            return Response('ok', status=200)

        price = get_cmc_data(symbol)
        send_message(chat_id,price)
        write_json(msg, 'telegram_json')
        return Response('OK', status=200)
    else:
        return '<p>coinmarketcap bot</p>'

def write_json(data, filename = 'response.json'):
    with open(filename,'w') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)



def get_cmc_data(crypto):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {'symbol':crypto,'convert':'USD'}
    headers = {'X-CMC_PRO_API_KEY': cmc_token}

    r = requests.get(url,params= params,headers= headers).json()
    write_json(r)
    price = r['da ta'][crypto]['quote']['USD']['price']

    return price

def main():
    print(get_cmc_data('BTC'))

#-->after 'bot' you must write your bot HTTP API
#https://api.telegram.org/bot{token}/getMe

#--> webhook URL from pythonanywhere.com
#--> then you run this URL and set webhook:
#https://api.telegram.org/bot{token}/setWebHook?url=https://aliansgp.pythonanywhere.com/



if __name__ == '__main__':
    app.run(debug=True)