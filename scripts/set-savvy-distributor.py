# brownie run scripts/set-savvy-distributor.py --network arbitrum-main-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d")

    # abis
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    reward_token = "0x43ab8f7d2a8dd4102ccea6b438f6d747b1b9f034"
    distributor = "0x8f7c5539Abefee5B860737A7F8bFa7bB1AA1dD1e"
    gauges = ["0xa41036c55ee6f1cfe864145ded4f5ef6b3505df8", "0x0f591dcf2601a93688368f2952cc036f4ae7f88a", "0x16fc75bed380d406bcb403bb4ef748f85a110857"]

    ######################################################################
    # Set token distributor for gauges
    ######################################################################
    
    for gauge in gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.add_reward(reward_token, distributor)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
