# brownie run scripts/whitelist-gauges-2024-02-12.py --network mainnet-fork

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
    eth_gauges = [
        "0xfb5e4adac4be9295bf8008fd78dba7f7fda48629", # rswETH/WETH
        "0xa2435583bcc13cc53e5da10016b5784ad0c5c792", # weETH/WETH
        "0xa1290a1d1c574a5340c0127aa36160b87578c6f8", # LIT/WETH
    ]

    cap_5_gauges = [
        "0xa1290a1d1c574a5340c0127aa36160b87578c6f8", # LIT/WETH
    ]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in eth_gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    ######################################################################
    # Update ethereum gauge tokenless_production
    ######################################################################

    for gauge in eth_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    weight_cap_5 = int(0.05e18) # 5%
    for gauge in cap_5_gauges:
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
