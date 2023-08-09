# brownie run scripts/2023-08-09.py --network mainnet-fork

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
    with open('scripts/abi/SmartWalletChecker.json') as f:
        smart_wallet_checker_abi = json.loads(f.read())

    # config
    gauges = ["0x04D20FfF44c6FdDB4aFfecc56960Bb87B381bcc3"]

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
    # Whitelist Liquis for veLIT locking
    ######################################################################

    liquis = "0x37aeB332D6E57112f1BFE36923a7ee670Ee9278b"
    smart_wallet_checker_contract = Contract.from_abi("SmartWalletChecker", "0x0CCdf95bAF116eDE5251223Ca545D0ED02287a8f", smart_wallet_checker_abi, gov_safe.account)
    smart_wallet_checker_contract.allowlistAddress(liquis)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
