# brownie run scripts/set-arbitrum-bridger.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/RootGaugeFactory.json') as f:
        factory_abi = json.loads(f.read())

    ######################################################################
    # Set Arbitrum bridger
    ######################################################################
    
    factory = Contract.from_abi(
        "RootGaugeFactory", "0xe4666F0937B62d64C10316DB0b7061549F87e95F", factory_abi, gov_safe.account)
    factory.set_bridger(42161, "0x093E035e9c2885b1b77B5632F92Fa7593f88E9B3")

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
