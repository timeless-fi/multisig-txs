# brownie run scripts/bribe-velit-bal.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())
    with open('scripts/abi/BunniBribe.json') as f:
        bunni_bribe_abi = json.loads(f.read())

    # config
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    bribe_vault = "0x9DDb2da7Dd76612e0df237B89AF2CF4413733212"
    proposal = '0xf2d3f7732367b2f4b9d104db8c3a0f2cfc4859cc4ed082dc23a123d3fb52bbc3'
    bribe_amount = int(5e18)

    # contracts
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    balancer_bribe = Contract.from_abi(
        "BalancerBribe", "0x7Cdf753b45AB0729bcFe33DC12401E55d28308A9", bunni_bribe_abi, gov_safe.account)
    
    weth_contract.approve(bribe_vault, bribe_amount)
    balancer_bribe.depositBribeERC20(proposal, weth, bribe_amount)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)