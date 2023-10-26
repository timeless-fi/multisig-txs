# brownie run scripts/whitelist-gauges-2023-10-19.py --network mainnet-fork

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

    # config
    arb_gauges = []
    eth_gauges = [
        "0xC11869829D58150d5268e8F2d32BD4815B437142", # DOLA/USDC
        "0xC433eC439f5A63Bb360F432fb013D572564A9ce1", # INV/DOLA
        "0x9AfcE0c50E3696Df713371e3EEE23e8814d23518", # GHO/USDC
        "0x50593792615768ECAA29B08FB11b3dE9733e5366", # FRAX/USDC
        "0x9dd83cd7877b1ac7a5057170bff3eb59ca1c057a", # GRAI/ETHx
    ]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController",
        "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218",
        gauge_controller_abi,
        gov_safe.account,
    )

    ######################################################################
    # Whitelist gauges
    ######################################################################

    for gauge in arb_gauges + eth_gauges:
        gauge_controller.add_gauge(gauge, 0, 1)

    ######################################################################
    # Update ethereum gauge tokenless_production
    ######################################################################

    for gauge in eth_gauges:
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

    """ ######################################################################
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
    gov_safe.post_transaction(safe_tx) """
