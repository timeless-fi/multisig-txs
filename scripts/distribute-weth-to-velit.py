# brownie run scripts/distribute-weth-to-velit.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json
import time
import requests

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())
    with open('scripts/abi/FeeDistributor.json') as f:
        fee_distributor_abi = json.loads(f.read())

    weth_amount = int(7.8865072917 * 1e18)
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    subgraph_endpoint = "https://api.thegraph.com/subgraphs/name/bunniapp/olit-redemption"

    # contracts
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    fee_distributor = Contract.from_abi("FeeDistributor", "0x951f99350d816c0E160A2C71DEfE828BdfC17f12", fee_distributor_abi, gov_safe.account)

    ######################################################################
    # Fetch this epoch's oLIT redemption amount
    ######################################################################

    week = 7 * 24 * 60 * 60
    epoch_start = int(time.time() // week * week)
    headers = {
        'Content-Type': 'application/json'
    }
    query = '''
    query Query($start: Int!) {
        weeks(where: {startTimestamp: $start}) {
            totalWethRedeemed
        }
    }
    '''
    payload = {"query": query, "variables": {"start": epoch_start}}
    response = requests.post(subgraph_endpoint, json=payload, headers=headers)

    if response.status_code == 200:
        weth_redeemed = int(response.json()["data"]["weeks"][0]["totalWethRedeemed"]) // 2
        weth_amount += weth_redeemed

    print(f"Redeemed WETH to distribute: {weth_redeemed / 1e18}")
    print(f"Total to distribute: {weth_amount / 1e18}")

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
