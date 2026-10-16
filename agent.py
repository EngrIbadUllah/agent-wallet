import os, re, json, datetime
import wallet, policy

SYSTEM = """You convert a user's wallet command into JSON only, no other text.
Schema: {"action": "balance"|"send"|"history"|"unknown", "to": string|null, "amount": number|null}
"to" may be a contact name or a 0x address. Amount is in ETH."""

def parse_with_ai(text):
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=200,
        system=SYSTEM, messages=[{"role": "user", "content": text}])
    raw = msg.content[0].text.strip().strip("`").replace("json", "", 1).strip()
    return json.loads(raw)

def parse_fallback(text):
    t = text.lower()
    m = re.search(r"send\s+([\d.]+)\s*(?:eth)?\s+to\s+(\S+)", t)
    if m:
        return {"action": "send", "amount": float(m.group(1)), "to": m.group(2)}
    if "balance" in t:
        return {"action": "balance", "to": None, "amount": None}
    if "history" in t or "log" in t:
        return {"action": "history", "to": None, "amount": None}
    return {"action": "unknown", "to": None, "amount": None}

def parse(text):
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return parse_with_ai(text)
        except Exception as e:
            print("(AI parser failed, using fallback)", e)
    return parse_fallback(text)

def log(entry):
    entry["time"] = datetime.datetime.utcnow().isoformat()
    with open("audit_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

def handle(text):
    intent = parse(text)
    action = intent.get("action")
    if action == "balance":
        return f"Balance: {wallet.get_balance()} ETH"
    if action == "history":
        if not os.path.exists("audit_log.jsonl"):
            return "No history yet."
        return "".join(open("audit_log.jsonl").readlines()[-5:])
    if action == "send":
        to = intent.get("to")
        contacts = policy.load_contacts()
        to = contacts.get((to or "").lower(), to)
        amount = intent.get("amount")
        tier, reason = policy.evaluate(to, amount, wallet.get_balance())
        base = {"action": "send", "to": to, "amount": amount or 0, "tier": tier, "reason": reason}
        if tier == "BLOCK":
            log({**base, "status": "blocked"})
            return f"BLOCKED: {reason}"
        if tier == "CONFIRM":
            ans = input(f"CONFIRM needed ({reason}). Send {amount} ETH to {to}? (yes/no): ")
            if ans.strip().lower() != "yes":
                log({**base, "status": "declined"})
                return "Cancelled by user."
        tx = wallet.send_eth(to, amount)
        log({**base, "status": "sent", "tx_hash": tx})
        return f"SENT. Tx hash: {tx}\nhttps://sepolia.etherscan.io/tx/{tx}"
    return "Sorry, I didn't understand. Try: 'send 0.001 ETH to alice' or 'balance'."

if __name__ == "__main__":
    print("Agent Wallet ready. Type 'exit' to quit.")
    while True:
        text = input("\nYou: ")
        if text.strip().lower() == "exit":
            break
        print(handle(text))