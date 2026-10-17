import json

import wallet

me = wallet.acct.address
alice = list(json.load(open("contacts.json")).values())[0]
print("sender code bytes:", len(wallet.w3.eth.get_code(me)))
print("balance before:", wallet.get_balance())
try:
    h = wallet.send_eth(alice, 0.0001)
    print("SUCCESS", h)
    print("https://sepolia.etherscan.io/tx/" + h)
except Exception as e:
    print("FAILED:", e)
print("balance after:", wallet.get_balance())