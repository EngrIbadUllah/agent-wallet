# Agent Wallet — AI Wallet Agent with Policy-Enforced Safety

Submission for the **2026 Shenzhen International FinTech Competition, International Track, Topic F: Agent Wallet (Autonomous On-chain Wallet)**.

Repository: https://github.com/EngrIbadUllah/agent-wallet

An AI wallet agent that turns plain-English instructions into on-chain payments. The AI only proposes; a deterministic policy engine decides whether each payment is refused, held for human approval, or executed. Everything runs on **test networks only**.

## Key idea

The language model never holds a key and cannot approve spending. It converts text into a structured request. A separate rule engine then checks that request line by line, and the result is shown to the user on an **authorisation slip** before anything is signed. A prompt-injection attack therefore cannot move funds, because the limits are enforced outside the model.

## Features

- Plain-English commands: `balance`, `send 0.001 ETH to alice`
- Policy engine with three outcomes: act (trusted contact, small amount), ask first (new recipient or larger amount), refuse (invalid input, over limit, over daily budget, low balance)
- Authorisation slip: every rule shown as pass or fail for each request
- Red-team simulator: six attack scenarios (prompt injection, wallet drain, malformed address, negative amount, zero-value trick, address poisoning), none of which sends funds
- Full ledger of every decision, including refusals, with Etherscan links
- **Wallet connection:** WalletConnect (QR code for mobile wallets) and every browser wallet extension discovered through EIP-6963, so the user's own wallet signs and the key never reaches the app
- **Six EVM test networks:** Ethereum Sepolia, Base Sepolia, Arbitrum Sepolia, OP Sepolia, Polygon Amoy, BNB Testnet
- USDC balance display (read-only) on the networks where Circle's testnet USDC exists
- Transaction receipts are verified: the app reports success only if the network confirms status 1

## Architecture

```
User text
   │
   ▼
AI parser (Claude, or a regex fallback without an API key)  → {action, to, amount}
   │
   ▼
Policy engine (policy.py)  → BLOCK / CONFIRM / AUTO + rule trace
   │
   ├─ BLOCK   → refused and logged
   ├─ CONFIRM → human approval (slip button, or the user's own wallet prompt)
   └─ AUTO    → proceeds
   ▼
Signer: demo agent wallet (wallet.py, Sepolia)  or  the user's connected wallet
   ▼
Receipt check → ledger (audit_log.jsonl)
```

| File                             | Purpose                                                          |
| -------------------------------- | ---------------------------------------------------------------- |
| `server.py`                      | Flask API: commands, approvals, attack tests, chains, tokens     |
| `static/index.html`              | The web interface                                                |
| `static/walletconnect.bundle.js` | WalletConnect provider and QR code, bundled with esbuild         |
| `policy.py`                      | Permission tiers and limits                                      |
| `wallet.py`                      | Demo agent wallet: gas estimation, signing, receipt verification |
| `agent.py`                       | Intent parsing and audit logging                                 |
| `tests/test_policy.py`           | Unit tests for the policy engine                                 |

## Setup

Requirements: Python 3.11+

```bash
git clone https://github.com/EngrIbadUllah/agent-wallet.git
cd agent-wallet
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
python create_wallet.py          # makes a test wallet and a local .env
python check_balance.py          # fund the printed address from a Sepolia faucet
```

Edit `contacts.json` to set trusted contacts, then run:

```powershell
$env:WC_PROJECT_ID="your-walletconnect-project-id"   # free, from Reown Cloud; needed only for WalletConnect
python server.py
```

Open http://127.0.0.1:5000. Optional: set `ANTHROPIC_API_KEY` for AI parsing. Without it, a simple rule-based parser handles the commands.

## Tests

```bash
python -m pytest tests -v
```

## Execution evidence (Sepolia)

Pending: this section will list the confirmed transaction hashes from the final demo run, each with its Etherscan status.

Lesson recorded: an earlier build hard-coded 21,000 gas, which this network rejects for plain transfers (it estimated about 207,000). Those transactions failed on-chain while the app reported success. The wallet now estimates gas and checks the receipt, and the earlier run is excluded from the evidence.

## Security design

- **Key isolation:** the demo key lives only in a local `.env` (git-ignored) and is never sent to the model. With a connected wallet, the user's wallet holds the key.
- **Separation of duties:** the AI proposes, deterministic code decides.
- **Least privilege:** per-transaction limit, daily budget, trusted-contact allowlist, gas reserve.
- **Human in the loop:** new recipients and larger amounts need explicit approval, and policy is re-checked at approval time.
- **Verified outcomes:** success is reported only after a confirmed receipt.
- **Auditability:** every decision is logged with time, recipient, amount, rule outcome and status.
- **Test networks only.**

## Known limitations

- Native-coin transfers only; USDC is displayed but not sent.
- In connected-wallet mode the policy check runs in the app, and the wallet signs what it is shown. It is not cryptographically enforced the way an on-chain smart-contract wallet would be.
- Limits are in native-coin units and are not converted to a common currency across networks.
- WalletConnect was tested with a limited set of wallets. Some wallets handle test networks poorly.
- The daily budget relies on a local log file; the private key sits in plaintext in `.env` (acceptable for a test-network demo only).
- Public RPC endpoints can be slow or rate-limited.
- Only EVM networks are supported; non-EVM chains would need different wallet code.

## Rebuilding the WalletConnect bundle

```bash
npm install @walletconnect/ethereum-provider@2.25.0 qrcode esbuild
# entry.js:  import {EthereumProvider} from "@walletconnect/ethereum-provider";
#            import QRCode from "qrcode";
#            window.WCProvider = {EthereumProvider, QRCode};
npx esbuild entry.js --bundle --minify --format=iife --platform=browser --define:global=globalThis --define:process.env.NODE_ENV='"production"' --outfile=static/walletconnect.bundle.js
```

## Third-party components

web3.py, Flask, python-dotenv, pytest, the Anthropic SDK, `@walletconnect/ethereum-provider`, qrcode, esbuild, all used under their open-source licences.
