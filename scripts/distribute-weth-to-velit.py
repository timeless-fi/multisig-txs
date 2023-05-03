# brownie run scripts/distribute-weth-to-velit.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())
    with open('scripts/abi/FeeDistributor.json') as f:
        fee_distributor_abi = json.loads(f.read())

    weth_amount = int(7.8865072917 * 1e18)
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    # contracts
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    fee_distributor = Contract.from_abi("FeeDistributor", "0x951f99350d816c0E160A2C71DEfE828BdfC17f12", fee_distributor_abi, gov_safe.account)

    ######################################################################
    # Distribute WETH
    ######################################################################
    
    weth_contract.approve(fee_distributor.address, weth_amount)
    fee_distributor.depositToken(weth, weth_amount)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
