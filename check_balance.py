import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
addr = Account.from_key(os.getenv("PRIVATE_KEY")).address
bal = w3.eth.get_balance(addr)
print("Connected:", w3.is_connected())
print("Address:", addr)
print("Balance:", w3.from_wei(bal, "ether"), "ETH")