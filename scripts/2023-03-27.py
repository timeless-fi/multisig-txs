# brownie run scripts/2023-03-27.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract
import json
import brownie
from brownie.convert import to_string
import subprocess

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    gauges = ["0x4CF5CB105D8baC299d010C71E1932a859d731B7b", "0x3b5F433940eD3f57F9ab73e725cf91cfaaef8789"]

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
        gauge_contract.set_tokenless_production(10) # 10x max boost

    ######################################################################
    # Cap yield token gauges to 5% emissions
    ######################################################################

    yt_gauges = ["0x4A0f5be682622c659c4A3C5996071d8E55695D4c", "0x7a5252e430C58E527016B2cFF68641C8b8BE21B7", "0xAD879AEC78BFEAad11715D097fd82e00e52327a6"]
    weight_cap = int(0.05e18)
    for yt_gauge in yt_gauges:
        yt_gauge_contract = Contract.from_abi("TimelessLiquidityGauge", yt_gauge, gauge_abi, gov_safe.account)
        yt_gauge_contract.setRelativeWeightCap(weight_cap)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
