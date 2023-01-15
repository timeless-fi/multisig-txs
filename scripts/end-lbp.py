# brownie run scripts/end-lbp.py --network mainnet-fork

from ape_safe import ApeSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/LBP.json') as f:
        lbp_abi = json.loads(f.read())

    ######################################################################
    # Disable trading in LBP
    ######################################################################
    
    lbp = Contract.from_abi(
        "LBP", "0xF3946A0e5368F716b1f40586272c9066b419035c", lbp_abi, gov_safe.account)
    lbp.setSwapEnabled(False)

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
