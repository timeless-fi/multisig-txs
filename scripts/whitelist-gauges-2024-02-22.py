# brownie run scripts/whitelist-gauges-2024-02-22.py --network mainnet-fork

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
        "0xa7493b1841f2c7ed3a6a576d89ba4659f5418f45", # weETH/WETH
    ]

    # contracts
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)
    
    ######################################################################
    # Set GRAI distributor for GRAI/USDC gauge
    ######################################################################

    reward_token = "0x15f74458aE0bFdAA1a96CA1aa779D715Cc1Eefe4" # GRAI
    distributor = "0x1d1CfD4FfB8cFD0A903A38c3B41D593369B46103"
    gauges = ["0x0dd538156cc4b0966d4ab60358ad2b12f57b0961"]

    for gauge in gauges:
        gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
        gauge_contract.add_reward(reward_token, distributor)    

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
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)