# brownie run scripts/whitelist-gauges-2023-03-20.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract
from brownie.convert import to_string

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    dop_gauge = "0xC118C27C5e364054C0e206049c7e09C7D9D18989"
    gauges = ["0xE410b7577882dD1d5c9a00bB1D806A4EA02FAB30", dop_gauge]

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
    # Update gauge caps
    ######################################################################
    
    dop_gauge_contract = Contract.from_abi("TimelessLiquidityGauge", dop_gauge, gauge_abi, gov_safe.account)
    dop_weight_cap = int(0.02e18) # 2%
    dop_gauge_contract.setRelativeWeightCap(dop_weight_cap)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
