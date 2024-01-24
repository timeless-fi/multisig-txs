# brownie run scripts/enable-liquidity-mining-2023-01-06.py --network arbitrum-main-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network


def main():
    # configs
    gov_safe = BrownieSafe("0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d")

    # abis
    with open("scripts/abi/TimelessLiquidityGauge.json") as f:
        gauge_abi = json.loads(f.read())

    # config
    gauges = [
        "0xc21D0eDF5A6E7D00B96AfC9BafC6e46F64159005",
        "0x4c4504B5178A9358008EAC70A3A2DCfd9972a3C5",
    ]

    ######################################################################
    # Update GNS gauges
    ######################################################################

    for gauge in gauges:
        gauge_contract = Contract.from_abi(
            "TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account
        )
        gauge_contract.set_reward_distributor(
            "0x18c11FD286C5EC11c3b683Caa813B77f5163A122",
            "0x80fd0accC8Da81b0852d2Dca17b5DDab68f22253",
        )

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
