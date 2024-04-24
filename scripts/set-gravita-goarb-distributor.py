# brownie run scripts/set-gravita-goarb-distributor.py --network arbitrum-main-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d")

    # abis
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    reward_token = "0xC5e16f5009776aB645d6719B72962892428b2ac2"
    distributor = "0x1d1CfD4FfB8cFD0A903A38c3B41D593369B46103"
    gauges = ["0x846b89167040e655de785c8ddda57866182e268b"]

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
