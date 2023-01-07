# brownie run scripts/seed-usdc.py --network mainnet-fork

import ape_safe
from ape_safe import ApeSafe

def main():
    # configs
    dev_safe = ApeSafe("0x39D719fE517Bd73F414A90ed3A14527a5737c8e5")
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    ######################################################################
    # Transfer USDC from dev to gov
    ######################################################################

    usdc = dev_safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdc_amount = int(832083.22 * 1e6)
    usdc.transfer(gov_safe.address, usdc_amount)

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = dev_safe.multisend_from_receipts()

    # sign safe tx
    dev_safe.sign_with_frame(safe_tx).hex()

    # post tx
    dev_safe.post_transaction(safe_tx)
