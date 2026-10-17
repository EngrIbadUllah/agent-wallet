import json
import os

from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
me = Account.from_key(os.getenv("PRIVATE_KEY")).address
alice = list(json.load(open("contacts.json")).values())[0]
fresh = Account.create().address

for name, addr in [("alice", alice), ("fresh", fresh)]:
    code = w3.eth.get_code(addr)
    print(name, addr)
    print("  code bytes:", len(code), code.hex()[:60])
    try:
        est = w3.eth.estimate_gas({"from": me, "to": addr, "value": w3.to_wei(0.0001, "ether")})
        print("  gas estimate:", est)
    except Exception as e:
        print("  estimate failed:", e)