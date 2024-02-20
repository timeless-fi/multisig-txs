# brownie run scripts/vebal-increase-time.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    with open('scripts/abi/VeBalGrant.json') as f:
        grant_abi = json.loads(f.read())

    ######################################################################
    # Vote for veLIT Balancer gauge
    ######################################################################
    
    grant = Contract.from_abi(
        "VeBalGrant", "0x89f67f3054bFD662971854190Dbc18dcaBb416f6", grant_abi, gov_safe.account)
    to = 1708455220 + 365 * 24 * 60 * 60
    grant.increaseTime(to)

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
