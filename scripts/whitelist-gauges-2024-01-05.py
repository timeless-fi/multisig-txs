# brownie run scripts/whitelist-gauges-2024-01-05.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network

def main():
    # configs
    gov_safe = BrownieSafe('0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13')

    # abis
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    # config
    arb_gauges = [
        "0xc21d0edf5a6e7d00b96afc9bafc6e46f64159005", # GNS/WETH
        "0x4c4504b5178a9358008eac70a3a2dcfd9972a3c5", # GNS/USDC
    ]
    eth_gauges = [
        "0xaC3725421E2886A7684801Ab2Bc234535bD8f5Ad", # GRAI/LIQ
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
    # Update ethereum gauge tokenless_production & set appropriate caps
    ######################################################################

    for gauge in eth_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    #####################################################################
    # Submit transaction to gov Gnosis Safe
    #####################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)

    # ######################################################################
    # # Switch network to L2
    # ######################################################################

    network.disconnect()
    network.connect("arbitrum-main-fork")

    # switch to multisig on L2
    gov_safe = BrownieSafe('0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d')

    ######################################################################
    # Update arbitrum gauge tokenless_production
    ######################################################################

    for gauge in arb_gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.set_tokenless_production(20) # 5x max boost

    ######################################################################
    # Set ARB distributor for gauges
    ######################################################################

    reward_token = "0x912CE59144191C1204E64559FE8253a0e49E6548" # ARB
    distributor = "0xc5fCA2c19c5Ca269a10e15ee4A800ed82F53787D"
    gauges = ["0xc21d0edf5a6e7d00b96afc9bafc6e46f64159005", "0x4c4504b5178a9358008eac70a3a2dcfd9972a3c5"]

    for gauge in gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.add_reward(reward_token, distributor)    

    ######################################################################
    # Set GNS distributor for gauges
    ######################################################################

    reward_token = "0x18c11FD286C5EC11c3b683Caa813B77f5163A122" # GNS
    distributor = "0xF8E93a7D954F7d31D5Fa54Bc0Eb0E384412a158d"
    gauges = ["0xc21d0edf5a6e7d00b96afc9bafc6e46f64159005", "0x4c4504b5178a9358008eac70a3a2dcfd9972a3c5"]

    for gauge in gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.add_reward(reward_token, distributor)    

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)