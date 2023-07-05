# brownie run scripts/trc-50.py --network mainnet-fork

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
    with open('scripts/abi/BunniHub.json') as f:
        bunni_hub_abi = json.loads(f.read())

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)
    
    ######################################################################
    # Fetch the list of all gauges
    ######################################################################

    gauges = []
    n_gauges = gauge_controller.n_gauges()
    for i in range(n_gauges):
        gauges.append(gauge_controller.gauges(i))

    ######################################################################
    # Set max boost to 5x (i.e. tokenless_production to 20)
    ######################################################################

    for gauge in gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    ######################################################################
    # Set protocol fee to 10%
    ######################################################################
    
    bunni_hub = Contract.from_abi(
        "BunniHub", "0xb5087F95643A9a4069471A28d32C569D9bd57fE4", bunni_hub_abi, gov_safe.account)
    new_fee = int(0.10e18)
    bunni_hub.setProtocolFee(new_fee)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
