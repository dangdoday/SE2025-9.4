import ccxt
import time

exchange = ccxt.binance()
server_time = exchange.fetch_time()
local_time = int(time.time() * 1000)
drift = local_time - server_time

print(f"Server time: {server_time}")
print(f"Local time:  {local_time}")
print(f"Drift:       {drift} ms")

if drift > 0:
    print("Your clock is FAST (Ahead of server)")
else:
    print("Your clock is SLOW (Behind server)")
