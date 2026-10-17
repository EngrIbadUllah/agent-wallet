import os

from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
acct = Account.from_key(os.getenv("PRIVATE_KEY"))
CHAIN_ID = 11155111  # Sepolia


def get_balance():
    return float(w3.from_wei(w3.eth.get_balance(acct.address), "ether"))


def send_eth(to, amount):
    to = Web3.to_checksum_address(to)
    value = w3.to_wei(amount, "ether")
    try:
        est = w3.eth.estimate_gas({"from": acct.address, "to": to, "value": value})
    except Exception as e:
        raise RuntimeError(f"The network rejected this transfer before sending: {e}")
    base = w3.eth.get_block("latest")["baseFeePerGas"]
    tip = w3.to_wei(2, "gwei")
    tx = {
        "to": to,
        "value": value,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId": CHAIN_ID,
        "gas": int(est * 1.3) + 1000,
        "maxFeePerGas": base * 2 + tip,
        "maxPriorityFeePerGas": tip,
    }
    signed = acct.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    h = w3.eth.send_raw_transaction(raw).hex()
    if not h.startswith("0x"):
        h = "0x" + h
    receipt = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    if receipt.status != 1:
        raise RuntimeError(f"Transaction {h} was mined but failed on-chain (status 0).")
    return h