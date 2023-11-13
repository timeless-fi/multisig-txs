# brownie run scripts/whitelist-gauges-2023-11-13.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network


def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open("scripts/abi/GaugeController.json") as f:
        gauge_controller_abi = json.loads(f.read())
    with open("scripts/abi/TimelessLiquidityGauge.json") as f:
        gauge_abi = json.loads(f.read())
    with open("scripts/abi/RevenueSplitter.json") as f:
        splitter_abi = json.loads(f.read())

    # config
    arb_gauges = []
    arb_yt_gauges = [
        "0xc4f2733fad503f58429433dfbad0b8adc7d0433a",  # mGLP
        "0x10d4eec4c76e90de91e51746568ccc0c0d7816e1",  # waUSDC.e
        "0x45100bd2b5c8b36fdf49808abfe3408ff803fb0d",  # waFRAX
    ]
    eth_gauges = [
        "0xcBbA6d982BF9F341095590D73D95EA32A571a4A8",  # wUSK/paUSD
        "0x2d8D844f862A7cF57e0E64b4AecB468aFAdB0A08",  # JARVIS/WETH
        "0xE19E619f7A861Ac731c919705941669e8ee3f602",  # AURA/WETH
    ]
    eth_yt_gauges = []

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController",
        "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218",
        gauge_controller_abi,
        gov_safe.account,
    )

    ######################################################################
    # Add new gauge types
    ######################################################################

    gauge_controller.add_type("Arbitrum", 1)
    gauge_controller.add_type("Arbitrum Yield Tokens", 1)

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in eth_gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    for gauge in eth_yt_gauges:
        gauge_controller.add_gauge(gauge, 1, 1)

    for gauge in arb_gauges:
        gauge_controller.add_gauge(gauge, 2, 1)

    for gauge in arb_yt_gauges:
        gauge_controller.add_gauge(gauge, 3, 1)

    ######################################################################
    # Update ethereum gauge tokenless_production
    ######################################################################

    for gauge in eth_gauges + eth_yt_gauges:
        gauge_contract = Contract.from_abi(
            "TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account
        )
        gauge_contract.set_tokenless_production(20)  # 5x max boost

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

    for gauge in arb_gauges + arb_yt_gauges:
        gauge_contract = Contract.from_abi(
            "TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account
        )
        gauge_contract.set_tokenless_production(20)  # 5x max boost

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
