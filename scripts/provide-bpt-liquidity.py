# brownie run scripts/provide-bpt-liquidity.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json
from brownie.convert import to_string
import subprocess

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())

    ######################################################################
    # Initialize 80-20 pool liquidity
    ######################################################################

    weth = Contract.from_abi(
        "WETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", erc20_abi, gov_safe.account)
    lit = gov_safe.contract("0xfd0205066521550D7d7AB19DA8F72bb004b4C341")
    bal_vault = gov_safe.contract("0xBA12222222228d8Ba445958a75a0704d566BF2C8")
    weth_amount = int(314784834262110346830)
    lit_amount = int(32863386.9 * 1e18)

    # approve tokens
    weth.approve(bal_vault.address, weth_amount)
    lit.approve(bal_vault.address, lit_amount)

    # initialize LBP
    user_data = to_string(subprocess.check_output(f"cast ae 'foo(uint8,uint256[])' 0 '[{weth_amount},{lit_amount}]'", shell=True))[:-1]
    bal_vault.joinPool("0x9232A548DD9E81BAC65500B5E0D918F8BA93675C000200000000000000000423", gov_safe.address, gov_safe.address, ([weth.address, lit.address], [weth_amount, lit_amount], user_data, False))

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
