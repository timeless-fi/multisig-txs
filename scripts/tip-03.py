# brownie run scripts/tip-03.py --network mainnet-fork

import ape_safe
from ape_safe import ApeSafe
import json
from brownie import Contract

def main():
    print(ape_safe.__file__)

    # configs
    dev_safe = ApeSafe("0x39D719fE517Bd73F414A90ed3A14527a5737c8e5")
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/VestingEscrowFactory.json') as f:
        factory_abi = json.loads(f.read())

    ######################################################################
    # Transfer 447000 USDC + 10000000 LIT
    ######################################################################

    usdc = gov_safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdc_amount = int(447000 * 1e6)
    usdc.transfer(dev_safe.address, usdc_amount)

    lit = gov_safe.contract("0xfd0205066521550D7d7AB19DA8F72bb004b4C341")
    lit_amount = int(1e7 * 1e18)
    lit.transfer(dev_safe.address, lit_amount)
    
    ######################################################################
    # Create LlamaPay stream of 1043000 USDC from 2023/3/5 to 2024/2/29
    ######################################################################

    llamapay_factory = Contract.from_abi(
        "VestingEscrowFactory", "0xB93427b83573C8F27a08A909045c3e809610411a", factory_abi, gov_safe.account)
    vesting_duration = 361 * 24 * 60 * 60 # 361 days between 2023/3/5 & 2024/2/29
    vesting_start = 1678046400 # 2023/3/5 12pm Pacific Time
    usdc_amount = int(1043000 * 1e6)

    usdc.approve(llamapay_factory.address, usdc_amount)
    llamapay_factory.deploy_vesting_contract(usdc.address, dev_safe.address, usdc_amount, vesting_duration, vesting_start)

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
