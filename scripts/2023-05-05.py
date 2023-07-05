# brownie run scripts/2023-05-05.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    eure_gauge = "0x9Ca4f7c8CCFd421D84ACD355Ea819C8d37c0B598"
    gauges = [eure_gauge, "0x2F99bc91fCBEC71BBDb997ce1E7AA73dB93a75Ad"]

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
    # Cap EURe/USDC gauge to 10% emissions
    ######################################################################

    eure_gauge_contract = Contract.from_abi("TimelessLiquidityGauge", eure_gauge, gauge_abi, gov_safe.account)
    weight_cap = int(0.1e18)
    eure_gauge_contract.setRelativeWeightCap(weight_cap)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
