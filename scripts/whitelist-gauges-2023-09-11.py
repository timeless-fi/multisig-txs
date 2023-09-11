# brownie run scripts/whitelist-gauges-2023-09-11.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    arb_gauges = [
        "0x21a0e3db0052bffcb14e0229e28e1bee575b24e9" # RDNT/ETH
    ]
    eth_gauges = [
        "0x157C6F527dE5987235ae1305608494731Ff03b10", # LIQ/ETH
        "0xbb6fb649929420dc56d90b013c2e4caee291e759", # liqLIT/20LIT-80WETH full range
        "0x8e375dfb1b347d3e84fa9dfe1eecdc5fd7845e9e" # liqLIT/20LIT-80WETH narrow range
    ]
    increase_cap_gauges = [
        "0x04D20FfF44c6FdDB4aFfecc56960Bb87B381bcc3", # DUSD/USDC
        "0x12e4670e3E49fc872f0915b4B162E87A98f17F91" # PAL/FRAX
    ]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in arb_gauges + eth_gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    ######################################################################
    # Update ethereum gauge tokenless_production & set 10% cap
    ######################################################################

    for gauge in eth_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    ######################################################################
    # Set 10% cap for all gauges
    ######################################################################

    weight_cap = int(0.1e18) # 10%
    for gauge in eth_gauges + arb_gauges + increase_cap_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        if gauge_contract.getRelativeWeightCap() != weight_cap:
            gauge_contract.setRelativeWeightCap(weight_cap)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)

    ######################################################################
    # Switch network to L2
    ######################################################################

    network.disconnect()
    network.connect("arbitrum-main-fork")

    # switch to multisig on L2
    gov_safe = BrownieSafe("0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d")

    ######################################################################
    # Update arbitrum gauge tokenless_production
    ######################################################################

    for gauge in arb_gauges:
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
