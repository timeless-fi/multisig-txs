# brownie run scripts/end-airdrop.py --network mainnet-fork

from ape_safe import ApeSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/Astrodrop.json') as f:
        astrodrop_abi = json.loads(f.read())

    ######################################################################
    # Retrieve tokens from the airdrop contract
    ######################################################################

    airdrop_contract = Contract.from_abi("Astrodrop", "0x6CA23531C1bE26b0119a1cD71CA3509c8D0853CC", astrodrop_abi, gov_safe.account)
    airdrop_contract.sweep("0xfd0205066521550D7d7AB19DA8F72bb004b4C341", gov_safe.address)

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
