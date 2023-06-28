# brownie run scripts/whitelist-gauges-2023-06-26.py --network mainnet-fork

from ape_safe import ApeSafe
import json
from brownie import Contract
from brownie.convert import to_string

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    gauges = ["0xb98FE645C7e2c39b726747dCb72848a9fd8c425F", "0x3f28CA531Cb4767EEBFD8974a7a782058C53AF6a", "0x3090124ffa5aadbb1bf3006e06599cb8e9633df8"]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    ######################################################################
    # Update gauge tokenless_production
    ######################################################################

    for gauge in gauges:
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
