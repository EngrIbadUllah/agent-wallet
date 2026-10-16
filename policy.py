import json, os, datetime
from web3 import Web3

MAX_PER_TX = 0.01      # hard limit per transaction (ETH)
DAILY_LIMIT = 0.03     # hard limit per day
CONFIRM_ABOVE = 0.005  # above this, human must confirm
GAS_RESERVE = 0.001

def load_contacts():
    with open("contacts.json") as f:
        return json.load(f)

def spent_today():
    total = 0.0
    today = datetime.datetime.utcnow().date().isoformat()
    if not os.path.exists("audit_log.jsonl"):
        return 0.0
    for line in open("audit_log.jsonl"):
        e = json.loads(line)
        if e.get("status") == "sent" and e["time"][:10] == today:
            total += e["amount"]
    return total

def evaluate(to, amount, balance_eth):
    """Returns (tier, reason). Tiers: BLOCK, CONFIRM, AUTO"""
    contacts = [a.lower() for a in load_contacts().values()]
    if not to or not Web3.is_address(to):
        return "BLOCK", "Invalid recipient address"
    if amount is None or amount <= 0:
        return "BLOCK", "Invalid amount"
    if amount > MAX_PER_TX:
        return "BLOCK", f"Amount exceeds per-transaction limit ({MAX_PER_TX} ETH)"
    if amount + spent_today() > DAILY_LIMIT:
        return "BLOCK", f"Would exceed daily limit ({DAILY_LIMIT} ETH)"
    if amount > balance_eth - GAS_RESERVE:
        return "BLOCK", "Insufficient balance after gas reserve"
    if to.lower() not in contacts:
        return "CONFIRM", "Recipient is not a trusted contact"
    if amount > CONFIRM_ABOVE:
        return "CONFIRM", "Amount above auto-approve threshold"
    return "AUTO", "Trusted contact and small amount"