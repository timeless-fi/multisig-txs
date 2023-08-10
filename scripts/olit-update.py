# brownie run scripts/olit-update.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/OptionsToken.json') as f:
        olit_abi = json.loads(f.read())
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())
    with open('scripts/abi/BalancerOracle.json') as f:
        oracle_abi = json.loads(f.read())


    ######################################################################
    # Update oLIT treasury to revenue splitter
    ######################################################################
    
    olit = Contract.from_abi(
        "OptionsToken", "0x627fee87d0D9D2c55098A06ac805Db8F98B158Aa", olit_abi, gov_safe.account)
    revenue_splitter = "0xb6859913BaE3E18d16198485643F8BB017E96B7f"
    olit.setTreasury(revenue_splitter)

    ######################################################################
    # Approve WETH to revenue splitter
    ######################################################################

    weth_contract = Contract.from_abi("WETH", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", erc20_abi, gov_safe.account)
    amount = int(50e18)
    weth_contract.approve(revenue_splitter, amount)

    ######################################################################
    # Lower min price of oLIT oracle
    ######################################################################

    oracle = Contract.from_abi(
        "BalancerOracle", "0x9d43ccb1aD7E0081cC8A8F1fd54D16E54A637E30", oracle_abi, gov_safe.account)
    oracle.setParams(5000, 1800, 0, int(0.6e13))

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
