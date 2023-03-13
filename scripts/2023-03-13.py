# brownie run scripts/2023-03-13.py --network mainnet-fork

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
    with open('scripts/abi/SmartWalletChecker.json') as f:
        smart_wallet_checker_abi = json.loads(f.read())

    # config
    ize_gauge = "0xDE58296858d19313b5CD666629286d70E773bB7d"
    gauges = [ize_gauge, "0xFf780599310ccd337Da4D4804fE31A75c2a66a81"]

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
    # Cap IZE gauge to 5% emissions
    ######################################################################

    ize_gauge_contract = Contract.from_abi("TimelessLiquidityGauge", ize_gauge, gauge_abi, gov_safe.account)
    weight_cap = int(0.05e18)
    ize_gauge_contract.setRelativeWeightCap(weight_cap)

    ######################################################################
    # Whitelist PieDAO multisig for veLIT locking
    ######################################################################

    pie_dao_multisig = "0x3bcf3db69897125aa61496fc8a8b55a5e3f245d5"
    smart_wallet_checker_contract = Contract.from_abi("SmartWalletChecker", "0x0CCdf95bAF116eDE5251223Ca545D0ED02287a8f", smart_wallet_checker_abi, gov_safe.account)
    smart_wallet_checker_contract.allowlistAddress(pie_dao_multisig)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
