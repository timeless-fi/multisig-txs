# brownie run scripts/whitelist-gauges-2024-02-28.py --network mainnet-fork

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
        "0xa7493b1841f2c7ed3a6a576d89ba4659f5418f45", # weETH/WETH
        "0x7fde63a59bf765ad561173b71575b195690f00f2", # fUSDC/USDC
    ]

    eth_gauges = [
        "0x6cc53a70e1815894a5d4c5274f19bb9d1f8fb28a", # svETH/wstETH (wide range)
        "0x1a29da6dbbd7905ccb2fc30d2926849d89a4067b", # svETH/wstETH (narrow range)
    ]

    ten_percent_gauges = [
        "0x6cc53a70e1815894a5d4c5274f19bb9d1f8fb28a", # svETH/wstETH (wide range)
        "0x1a29da6dbbd7905ccb2fc30d2926849d89a4067b", # svETH/wstETH (narrow range)
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
    # Set 10% cap for relevant gauges
    ######################################################################

    weight_cap_10 = int(0.1e18) # 10%
    for gauge in ten_percent_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.setRelativeWeightCap(weight_cap_10)

    ######################################################################
    # Update ethereum gauge tokenless_production
    ######################################################################

    for gauge in eth_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

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