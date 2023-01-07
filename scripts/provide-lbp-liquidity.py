# brownie run scripts/provide-lbp-liquidity.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract
import json
import brownie
from brownie.convert import to_string
import subprocess

def main():
    # configs
    dev_safe = ApeSafe("0x39D719fE517Bd73F414A90ed3A14527a5737c8e5")
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/LBP.json') as f:
        lbp_abi = json.loads(f.read())

    ######################################################################
    # Transfer USDC from dev to gov
    ######################################################################

    usdc = dev_safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdc_amount = int(832083.22 * 1e6)
    usdc.transfer(gov_safe.address, usdc_amount)

    ######################################################################
    # Schedule weight change in LBP
    ######################################################################
    
    lbp = Contract.from_abi(
        "LBP", "0xF3946A0e5368F716b1f40586272c9066b419035c", lbp_abi, gov_safe.account)
    start_time = 1673294400
    end_time = start_time + 86400 * 7 # 7 days length
    lbp.updateWeightsGradually(start_time, end_time, [70e16, 30e16])

    ######################################################################
    # Initialize LBP liquidity
    ######################################################################

    usdc = gov_safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    lit = gov_safe.contract("0xfd0205066521550D7d7AB19DA8F72bb004b4C341")
    bal_vault = gov_safe.contract("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
    usdc_amount = int(832083.22 * 1e6)
    lit_amount = int(1e8 * 1e18)

    # approve tokens
    usdc.approve(bal_vault.address, usdc_amount)
    lit.approve(bal_vault.address, lit_amount)

    # initialize LBP
    user_data = to_string(subprocess.check_output(f"cast ae 'foo(uint8,uint256[])' 0 '[{usdc_amount},{lit_amount}]'", shell=True))[:-1]
    bal_vault.joinPool("0xF3946A0E5368F716B1F40586272C9066B419035C000200000000000000000424", gov_safe.address, gov_safe.address, ([usdc.address, lit.address], [usdc_amount, lit_amount], user_data, False))

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
