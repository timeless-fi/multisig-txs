# brownie run scripts/finalize-lbp.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract
from brownie.convert import to_string
import subprocess

def main():
    # configs
    dev_safe = BrownieSafe("0x39D719fE517Bd73F414A90ed3A14527a5737c8e5")
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/LBP.json') as f:
        lbp_abi = json.loads(f.read())
    with open('scripts/abi/VotingEscrow.json') as f:
        vetoken_abi = json.loads(f.read())
    with open('scripts/abi/TokenAdmin.json') as f:
        token_admin_abi = json.loads(f.read())

    ######################################################################
    # Withdraw liquidity from LBP
    ######################################################################

    bal_vault = gov_safe.contract("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
    lbp = Contract.from_abi(
        "LBP", "0xF3946A0e5368F716b1f40586272c9066b419035c", lbp_abi, gov_safe.account)
    pool_id = "0xF3946A0E5368F716B1F40586272C9066B419035C000200000000000000000424"
    bpt_balance = lbp.balanceOf(gov_safe.address)
    tokens, balances, last_change_block = bal_vault.getPoolTokens(pool_id)

    user_data = to_string(subprocess.check_output(f"cast ae 'foo(uint8,uint256)' 1 {bpt_balance}", shell=True))[:-1]
    bal_vault.exitPool(pool_id, gov_safe.address, gov_safe.address, ([tokens[0], tokens[1]], [balances[0]-1, balances[1]-23741202], user_data, False))

    ######################################################################
    # Transfer loan to dev safe
    ######################################################################

    loan_amount = 3e5 * 1e6
    usdc = gov_safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdc.transfer(dev_safe.address, loan_amount)

    ######################################################################
    # Set smart wallet checker in voting escrow
    ######################################################################

    vetoken = Contract.from_abi(
        "VotingEscrow", "0xf17d23136B4FeAd139f54fB766c8795faae09660", vetoken_abi, gov_safe.account)
    smart_wallet_checker = "0x0CCdf95bAF116eDE5251223Ca545D0ED02287a8f"
    vetoken.commit_smart_wallet_checker(smart_wallet_checker)
    vetoken.apply_smart_wallet_checker()

    ######################################################################
    # Activate inflation in token admin
    ######################################################################

    token_admin = Contract.from_abi("TokenAdmin", "0x4cc39AF0d46b0F66Fd33778C6629A696bDC310a0", token_admin_abi, gov_safe.account)
    token_admin.activate()

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
