# brownie run scripts/enable-liquidity-mining-2023-12-05.py --network arbitrum-main-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network

def main():
    # configs
    gov_safe = BrownieSafe("0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d")

    # abis
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    frax_gauges = [
        "0x4b6052e271c1a1af0eb62376fbba95fa4a1e282b", # FRAX/FPI
        "0x0f591dcf2601a93688368f2952cc036f4ae7f88a", # FRAX/svUSD
        "0xa9092a2cfd11f8e42cfd84c0217743f28b3c285c", # FRAX/ARB
        "0x6ffac7b1db79460093c06ceae86d3baca2f3cdfd", # FRAX/WFIRE
    ]
    frxeth_gauges = [
        "0x16fc75bed380d406bcb403bb4ef748f85a110857", # frxETH/svETH
        "0x00b20ffd6c2d27a5b9764ad2367f60e16e08ed3b", # frxETH/FRAX
    ]

    ######################################################################
    # Update FRAX gauges
    ######################################################################

    for gauge in frax_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.add_reward("0x912CE59144191C1204E64559FE8253a0e49E6548", "0xefa5D36deBF5191328b17f2Ff74090DAdfda9A70")

    ######################################################################
    # Update frxETH gauges
    ######################################################################

    for gauge in frxeth_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.add_reward("0x912CE59144191C1204E64559FE8253a0e49E6548", "0x3C6d74267b01E00B2C8F541ff132A7b03bcC6c70")

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
