import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import policy

policy.spent_today = lambda: 0.0
STRANGER = "0x1111111111111111111111111111111111111111"
ALICE = policy.load_contacts()["alice"]

def test_invalid_address_blocked():
    assert policy.evaluate("abc", 0.001, 0.05)[0] == "BLOCK"

def test_over_limit_blocked():
    assert policy.evaluate(ALICE, 5, 0.05)[0] == "BLOCK"

def test_stranger_needs_confirm():
    assert policy.evaluate(STRANGER, 0.001, 0.05)[0] == "CONFIRM"

def test_trusted_small_auto():
    assert policy.evaluate(ALICE, 0.001, 0.05)[0] == "AUTO"

def test_trusted_large_confirm():
    assert policy.evaluate(ALICE, 0.008, 0.05)[0] == "CONFIRM"

def test_insufficient_balance_blocked():
    assert policy.evaluate(ALICE, 0.005, 0.002)[0] == "BLOCK"