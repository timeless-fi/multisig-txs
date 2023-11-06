# brownie run scripts/whitelist-gauges-2023-11-6.py --network mainnet-fork

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
    eth_gauges = [
        "0x104b5D827AEAc64BB1efdfa63DAD0ABa500fCB9c", # tBTC-WBTC
        "0x1196E61acD651618219FcEf4c2931046Cd51a4AE", # bLUSD-LUSD
    ]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController",
        "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218",
        gauge_controller_abi,
        gov_safe.account,
    )
    revenue_splitter = Contract.from_abi(
        "RevenueSplitter",
        "0xb6859913BaE3E18d16198485643F8BB017E96B7f",
        splitter_abi,
        gov_safe.account,
    )

    ######################################################################
    # Increase GRAI-USDC gauge weight cap
    ######################################################################

    grai_gauge_address = "0x846b89167040e655de785C8dDda57866182E268B"
    grai_gauge = Contract.from_abi("TimelessLiquidityGauge", grai_gauge_address, gauge_abi, gov_safe.account)
    weight_cap = int(0.1e18) # 10%
    grai_gauge.setRelativeWeightCap(weight_cap)

    ######################################################################
    # Update revenue splitter params to distribute 25% of revenue to veLIT
    ######################################################################

    revenue_splitter.setTreasuryFeeDistro(0) # no more retro distro
    revenue_splitter.setTreasurySplit(int(0.25e9)) # 25% to veLIT
    revenue_splitter.setStopSplitTimestamp(1715022000) # ends on Monday, May 6, 2024 7:00:00 PM (GMT)

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
