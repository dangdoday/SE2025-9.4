import ccxt
import json

exchange = ccxt.binance({
    'apiKey': 'azKKkq9Kv3nZNRwgrOGZZ3KysSiAWKhtWIMoll09SFEUxP1i32PKDbcmlpfscaez',
    'secret': '5i4ZygyPjNxmZF7Al1KXWcGvcIE7K1vtvlF8eUQBKjspSAQwqjzZagUdXPSmhps8',
})

try:
    markets = exchange.load_markets()
    market = markets.get('ADA/USDT')
    if market:
        print(json.dumps(market['limits'], indent=4))
    else:
        print("Market not found")
except Exception as e:
    print(f"Error: {e}")
