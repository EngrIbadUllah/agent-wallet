from eth_account import Account

acct = Account.create()
with open(".env", "w") as f:
    f.write(f"PRIVATE_KEY={acct.key.hex()}\n")
    f.write("RPC_URL=https://ethereum-sepolia-rpc.publicnode.com\n")
print("Wallet address:", acct.address)