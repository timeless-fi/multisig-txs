# brownie run scripts/migrate-ize-gauge.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())

    ######################################################################
    # Kill IZE/USDC gauge
    ######################################################################

    gauge = "0xDE58296858d19313b5CD666629286d70E773bB7d"    
    gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
    gauge_contract.killGauge()

    ######################################################################
    # Whitelist IZE/WETH gauge
    ######################################################################

    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)
    gauge = "0x66f83e7a4F7Fd407B6564f25174D544a4B16aAf8"    
    gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
    gauge_controller.add_gauge(gauge, 0, 1)
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
