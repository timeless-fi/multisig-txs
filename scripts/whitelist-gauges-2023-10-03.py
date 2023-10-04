# brownie run scripts/whitelist-gauges-2023-10-03.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network

def main():
    # configs
    gov_safe = BrownieSafe('0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13')

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    arb_gauges = [
        "0x4b6052e271c1a1af0eb62376fbba95fa4a1e282b", # FRAX/FPI
        "0x0f591dcf2601a93688368f2952cc036f4ae7f88a", # FRAX/svUSD
        "0x16fc75bed380d406bcb403bb4ef748f85a110857", # frxETH/svETH
        "0xa41036c55ee6f1cfe864145ded4f5ef6b3505df8" # SVY/svETH
    ]
    eth_gauges = [
        "0xb73b1cd70d311c9FDAA78C621De2cc50B7799a25", # TBYMarch24(a)-USDC + Future TBY
        "0x88d1FF2F54538eEB8cA4E16963e17b1879eA7810", # UNIDX-WETH
        "0x820A8dC4d8265b0080AE56e1ea7AD756EF3Ca06b" # rETH-WETH
    ]
    five_percent_gauges = [
        "0xb73b1cd70d311c9FDAA78C621De2cc50B7799a25", # TBYMarch24(a)-USDC + Future TBY
        "0x88d1FF2F54538eEB8cA4E16963e17b1879eA7810", # UNIDX-WETH
        "0x4b6052e271c1a1af0eb62376fbba95fa4a1e282b", # FRAX/FPI
        "0x0f591dcf2601a93688368f2952cc036f4ae7f88a", # FRAX/svUSD
        "0x16fc75bed380d406bcb403bb4ef748f85a110857", # frxETH/svETH
        "0xa41036c55ee6f1cfe864145ded4f5ef6b3505df8" # SVY/svETH
    ]
    ten_percent_gauges = [
        "0x820A8dC4d8265b0080AE56e1ea7AD756EF3Ca06b" # rETH-WETH
    ]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in arb_gauges + eth_gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    ######################################################################
    # Update ethereum gauge tokenless_production & set appropriate caps
    ######################################################################

    for gauge in eth_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    ######################################################################
    # Set 10% cap for relevant gauges
    ######################################################################

    weight_cap_10 = int(0.1e18) # 10%
    for gauge in ten_percent_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.setRelativeWeightCap(weight_cap_10)

    ######################################################################
    # Set 5% cap for relevant gauges
    ######################################################################
    weight_cap_5 = int(0.05e18) # 5%
    for gauge in five_percent_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.setRelativeWeightCap(weight_cap_5)

    #####################################################################
    # Submit transaction to gov Gnosis Safe
    #####################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)

    # ######################################################################
    # # Switch network to L2
    # ######################################################################

    network.disconnect()
    network.connect("arbitrum-main-fork")

    # switch to multisig on L2
    gov_safe = BrownieSafe('0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d')

    ######################################################################
    # Update arbitrum gauge tokenless_production
    ######################################################################

    for gauge in arb_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)