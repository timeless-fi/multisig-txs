# brownie run scripts/vote-for-bal-gauge.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/VeBalGrant.json') as f:
        grant_abi = json.loads(f.read())

    ######################################################################
    # Vote for veLIT Balancer gauge
    ######################################################################
    
    grant = Contract.from_abi(
        "VeBalGrant", "0x89f67f3054bFD662971854190Dbc18dcaBb416f6", grant_abi, gov_safe.account)
    velit_gauge = "0x56124eb16441A1eF12A4CCAeAbDD3421281b795A"
    weight = int(10000)
    grant.voteGaugeWeight(velit_gauge, weight)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
