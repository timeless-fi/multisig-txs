# brownie run scripts/whitelist-initial-gauges.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract
from brownie.convert import to_string
import subprocess

def main():
    # configs
    dev_safe = BrownieSafe("0x39D719fE517Bd73F414A90ed3A14527a5737c8e5")
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())
    with open('scripts/abi/BalancerOracle.json') as f:
        oracle_abi = json.loads(f.read())

    # config
    gauges = ["0xd4d8E88bf09efCf3F5bf27135Ef12c1276d9063C", "0x5ef860746a5f2ea24ddbD54EaeF0dDa65d5157a0", "0x4420689Dc6b5CDE6Ff3B873CDbfD8519383a1681", "0x44971D8903125Dcad768c130090C7480608D422d", "0xEbC60e3DD7b90382461F49fb98787CA81a30CA23", "0x345ECB6aB8EF4B5cBE4b5AA31D533EED894790B4", "0x6e868d1A902Da6b26521bf92E437b9b6DCC6955A", "0x9E3b20Afe88f823614FB3bDe416c69A806F8D090", "0xecdfE2FB3D5542026E415e3813C4CFdedA19e7d3", "0xdc4AdbA5722144542fCBe86bdB57D28154aDF7E5", "0x36B88F590CAaCAa2E855DB449Cdb7b0a0D0cE4E6", "0xE61C1E33dF4921F8B4EF0ee3f7031b472AFB52cF", "0x1c78EfD3B11baC329ffD8CCa15FAE26dbD54A720", "0x6c30636d750D63A1361D5885c8aA33f922ACC9A3", "0x471A34823DDd9506fe8dFD6BC5c2890e4114Fafe"]
    yt_gauges = ["0x4A0f5be682622c659c4A3C5996071d8E55695D4c", "0x7a5252e430C58E527016B2cFF68641C8b8BE21B7", "0xAD879AEC78BFEAad11715D097fd82e00e52327a6"]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)

    ######################################################################
    # Create gauge types
    ######################################################################

    gauge_controller.add_type("Ethereum", 1)
    gauge_controller.add_type("Ethereum Yield Tokens", 1)

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    for gauge in yt_gauges:
        gauge_controller.add_gauge(gauge, 1, 1)

    ######################################################################
    # Update gauge tokenless_production
    ######################################################################

    for gauge in gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(10) # 10x max boost

    for gauge in yt_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(10) # 10x max boost

    ######################################################################
    # Update options token min price
    ######################################################################
    
    oracle = Contract.from_abi(
        "BalancerOracle", "0x9d43ccb1aD7E0081cC8A8F1fd54D16E54A637E30", oracle_abi, gov_safe.account)
    oracle.setParams(5000, 1800, 0, int(1.2e13))

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
