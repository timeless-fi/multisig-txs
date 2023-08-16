# brownie run scripts/set-swell-distributor.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    reward_token = "0x677365Ac7ca3E9efE12a29a001737A3Db265E8aF"
    distributor = "0x0fc59c9c998537c940a9dfc7dacde533a9c496fe"
    gauges = ["0xb98fe645c7e2c39b726747dcb72848a9fd8c425f", "0xa718193e1348fd4def3063e7f4b4154baacb0214", "0x270d9a0b9137c99bdfe8dd14fc527d3922a91678"]

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
