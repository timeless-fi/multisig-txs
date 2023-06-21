# brownie run scripts/fix-root-gauge-implementation.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/RootGaugeFactory.json') as f:
        factory_abi = json.loads(f.read())

    ######################################################################
    # Set Arbitrum bridger
    ######################################################################
    
    factory = Contract.from_abi(
        "RootGaugeFactory", "0xC5C3A1F095aC7cCA8c832FcAe526b3487e343AC2", factory_abi, gov_safe.account)
    factory.set_implementation("0x142d786401F869a35d3d82aE2d8a548Aa21F8196")

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
