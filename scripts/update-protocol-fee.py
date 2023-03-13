# brownie run scripts/update-protocol-fee.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract
import json
import brownie
from brownie.convert import to_string
import subprocess

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/BunniHub.json') as f:
        bunni_hub_abi = json.loads(f.read())

    ######################################################################
    # Set protocol fee to 50%
    ######################################################################
    
    bunni_hub = Contract.from_abi(
        "BunniHub", "0xb5087F95643A9a4069471A28d32C569D9bd57fE4", bunni_hub_abi, gov_safe.account)
    new_fee = int(0.5e18)
    bunni_hub.setProtocolFee(new_fee)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
