# brownie run scripts/olit-update-min-price.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/BalancerOracle.json') as f:
        oracle_abi = json.loads(f.read())

    ######################################################################
    # Lower min price of oLIT oracle
    ######################################################################

    oracle = Contract.from_abi(
        "BalancerOracle", "0x9d43ccb1aD7E0081cC8A8F1fd54D16E54A637E30", oracle_abi, gov_safe.account)
    oracle.setParams(5000, 1800, 0, int(0.5e12))

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
