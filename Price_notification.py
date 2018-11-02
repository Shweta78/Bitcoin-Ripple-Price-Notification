import requests
import time
from datetime import datetime

BITCOIN_API_URL= 'https://api.coinmarketcap.com/v1/ticker/'
IFTTT_WEBHOOKS_URL='https://maker.ifttt.com/trigger/{event_name}/with/key/{your-key}'
IFTTT_WEBHOOKS_URL_RIPPLE='https://maker.ifttt.com/trigger/{event_name}/with/key/{your-key}'

def get_latest_bitcoin_price():
	response=requests.get(BITCOIN_API_URL)
	response_json=response.json()
	return float(response_json[0]['price_usd'])

def get_latest_ripple_price():
	response=requests.get(BITCOIN_API_URL)
	response_json=response.json()
	return float(response_json[2]['price_usd'])

def post_ifttt_webhook(event_btc, event_xrp, value_btc,value_xrp):
	#event : corresponds to whatever event name we gave to our 
	#		 trigger when setting up the IFTTT applet.

	#value : The {{value1}} tage when setting up our applet is 
	#		 replaced with value

	#Payload that will be sen to IFTTT service
	data_bitcoin={'value1':value_btc}
	data_ripple={'value2':value_xrp}
	ifttt_event_url=IFTTT_WEBHOOKS_URL.format(event_btc)
	ifttt_event_url_ripple=IFTTT_WEBHOOKS_URL_RIPPLE.format(event_xrp)
	#Send a HTTP POST request to the webhook URL
	requests.post(ifttt_event_url,json=data_bitcoin)
	requests.post(ifttt_event_url_ripple,json=data_ripple)
	#requests.post() function allows us to send additional JSON
	#data just by adding the json keyword

BITCOIN_PRICE_THRESHOLD = 5000
RIPPLE_DESIRED_PRICE = 2

def format_bitcoin_history(bitcoin_history):
	#It formats bitcoin_history using some of the basic HTML tags
	#allowed by Telegram
	rows=[]
	for bitcoin_price in bitcoin_history:
		#formats the date into a string
		date=bitcoin_price['date'].strftime('%d-%m-%Y %H:%M')
		price=bitcoin_price['price']
		row = f'{date} : $<b>{price}</b>'
		#<b> is to create bolded text
		rows.append(row)

	return '<br>'.join(rows)

def format_ripple_history(ripple_history):
	#It formats bitcoin_history using some of the basic HTML tags
	#allowed by Telegram
	rows=[]
	for xrp_price in ripple_history:
		#formats the date into a string
		date=xrp_price['date'].strftime('%d-%m-%Y %H:%M')
		price=xrp_price['price']
		row = f'{date} : $<b>{price}</b>'
		#<b> is to create bolded text
		rows.append(row)

	return '<br>'.join(rows)


def main():
	bitcoin_history=[]
	ripple_history=[]
	while True:
		price_btc=get_latest_bitcoin_price()
		price_xrp=get_latest_ripple_price()
		date=datetime.now()
		bitcoin_history.append({'date':date , 'price' : price_btc})
		ripple_history.append({'date':date , 'price' : price_xrp})

		#Send emergency notification
		if price_btc < BITCOIN_PRICE_THRESHOLD and price_xrp > RIPPLE_DESIRED_PRICE:
			post_ifttt_webhook('bitcoin_price_emergency', 'Ripple_price_over_desired', price_btc , price_xrp)
		elif price_btc < BITCOIN_PRICE_THRESHOLD:
		 	post_ifttt_webhook('bitcoin_price_emergency', 'ripple_price_update', price_btc , price_xrp)
		else:
		 	post_ifttt_webhook('bitcoin_price_update', 'Ripple_price_over_desired', price_btc , price_xrp)

		#Send a TElegram notification
		#Once we have 5 items in our bitcoin_history, send an update 
		if len(bitcoin_history) == 2 or len(ripple_history) == 2:
			post_ifttt_webhook('bitcoin_price_update','ripple_price_update', format_bitcoin_history(bitcoin_history) , format_ripple_history(ripple_history))

			#Reset history
			bitcoin_history = []
			ripple_history = []

			#Sleep for 5 minutes
			time.sleep(5*60)

	    
if __name__=='__main__':
	main()
