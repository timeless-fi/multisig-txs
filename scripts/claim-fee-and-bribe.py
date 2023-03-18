# brownie run scripts/claim-fee-and-bribe.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract, network
from brownie.convert import to_address
import json
import requests
from eth_utils import to_bytes, keccak, to_hex

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/BunniHub.json') as f:
        bunni_hub_abi = json.loads(f.read())
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())
    with open('scripts/abi/GaugeController.json') as f:
        gauge_controller_abi = json.loads(f.read())
    with open('scripts/abi/BunniBribe.json') as f:
        bunni_bribe_abi = json.loads(f.read())

    # config
    last_sweep_block = 15743581
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    tokens = [
        "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF", # AURA
        "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D", # LQTY
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", # USDC
        "0x24C19F7101c1731b85F1127EaA0407732E36EcDD", # SGT
        "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", # LDO
        "0x853d955aCEf822Db058eb8505911ED77F175b99e", # FRAX
        "0x5E8422345238F34275888049021821E8E08CAa1f", # frxETH
        "0x111111111117dC0aa78b770fA6A738034120C302", # 1INCH
        "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # DAI
    ]
    bribe_vault = "0x9DDb2da7Dd76612e0df237B89AF2CF4413733212"
    subgraph_endpoint = 'https://api.thegraph.com/subgraphs/name/bunniapp/bunni-mainnet'

    # contracts
    bunni_hub = Contract.from_abi(
        "BunniHub", "0xb5087F95643A9a4069471A28d32C569D9bd57fE4", bunni_hub_abi, gov_safe.account)
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    gauge_controller = Contract.from_abi(
        "GaugeController", "0x901c8aA6A61f74aC95E7f397E22A0Ac7c1242218", gauge_controller_abi, gov_safe.account)
    bunni_bribe = Contract.from_abi(
        "BunniBribe", "0x78C45fBDB71E7c0FbDfe49bDEFdACDcc4764336f", bunni_bribe_abi, gov_safe.account)
    
    ######################################################################
    # Claim protocol fees from BunniHub
    ######################################################################

    before_balances = {}
    for token in tokens:
        token_contract = Contract.from_abi("ERC20", token, erc20_abi, gov_safe.account)
        token_balance = token_contract.balanceOf(gov_safe.address)
        before_balances[token] = token_balance
    before_balances[weth] = weth_contract.balanceOf(gov_safe.address)

    bunni_hub.sweepTokens([weth] + tokens, gov_safe.address)

    ######################################################################
    # Swap fees into WETH using 0x
    ######################################################################

    for token in tokens:
        token_contract = Contract.from_abi("ERC20", token, erc20_abi, gov_safe.account)
        token_balance = token_contract.balanceOf(gov_safe.address)
        token_amount = token_balance - before_balances[token]
        if token_amount == 0:
            continue

        url = f"https://api.0x.org/swap/v1/quote?buyToken=WETH&sellToken={token}&sellAmount={token_amount}"
        response = requests.get(url)

        if response.status_code == 200:
            swap_data = response.json()

            token_contract.approve(swap_data["allowanceTarget"], token_amount)
            gov_safe.account.transfer(to=swap_data["to"], data=swap_data["data"])
        else:
            print(f"Error: {response.status_code}")

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)

    ######################################################################
    # Halt script until the transaction has been executed
    ######################################################################

    input("Press Enter to continue once the first transaction has been executed...")

    # fetch the actual weth amount claimed by the first tx (which is likely different from the simulated value)
    # need to change the network to mainnet (instead of mainnet-fork) to fetch the actual
    # weth balance of the gov safe
    network.disconnect()
    network.connect("mainnet")
    total_weth_amount = weth_contract.balanceOf(gov_safe.address) - before_balances[weth]
    print(f"Total fee claimed in WETH: {total_weth_amount / 1e18}")

    # change the network back to mainnet-fork to start constructing the second tx
    network.disconnect()
    network.connect("mainnet-fork")

    # reset gov safe object to match the new network
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # reset contracts to use the new gov safe account
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    bunni_bribe = Contract.from_abi(
        "BunniBribe", "0x78C45fBDB71E7c0FbDfe49bDEFdACDcc4764336f", bunni_bribe_abi, gov_safe.account)

    ######################################################################
    # Compute how much bribe each pool deserves
    ######################################################################

    headers = {
        'Content-Type': 'application/json'
    }
    query = '''
    {
        bunniTokens(where: {gauge_not: "0x0000000000000000000000000000000000000000", collectedFeesToken0_gt: 0, collectedFeesToken1_gt: 0}, first: 1000) {
            name
            gauge
            pool {
                token0
                token1
            }
            collectedFeesToken0
            collectedFeesToken1
        }
    }
    '''
    payload = {"query": query}
    response = requests.post(subgraph_endpoint, json=payload, headers=headers)

    if response.status_code == 200:
        # filter for pools using tokens we have claimed from BunniHub and have whitelisted gauges
        current_bunni_tokens = list(filter(lambda x: to_address(x["pool"]["token0"]) in (tokens + [weth]) and to_address(x["pool"]["token1"]) in (tokens + [weth]) and gauge_controller.gauge_exists(to_address(x["gauge"])), response.json()["data"]["bunniTokens"]))
        
        query = '''
        query Query($block: Int!) {
            bunniTokens(where: {gauge_not: "0x0000000000000000000000000000000000000000", collectedFeesToken0_gt: 0, collectedFeesToken1_gt: 0}, first: 1000, block: {number: $block}) {
                name
                gauge
                pool {
                    token0
                    token1
                }
                collectedFeesToken0
                collectedFeesToken1
            }
        }
        '''
        payload = {"query": query, "variables": {"block": last_sweep_block}}
        response_past = requests.post(subgraph_endpoint, json=payload, headers=headers)

        if response_past.status_code == 200:
             # filter for pools using tokens we have claimed from BunniHub and have whitelisted gauges
            past_bunni_tokens = filter(lambda x: to_address(x["pool"]["token0"]) in (tokens + [weth]) and to_address(x["pool"]["token1"]) in (tokens + [weth]) and gauge_controller.gauge_exists(to_address(x["gauge"])), response_past.json()["data"]["bunniTokens"])

            bribe_weights = {}

            # compare against past data to see how much fee has accrued since the last sweep
            for i, bunni_token in enumerate(current_bunni_tokens):
                past_bunni_token = next((item for item in past_bunni_tokens if item["gauge"] == bunni_token["gauge"]), None)
                if past_bunni_token:
                    current_bunni_tokens[i]["collectedFeesToken0"] = int(bunni_token["collectedFeesToken0"]) - int(past_bunni_token["collectedFeesToken0"])
                    current_bunni_tokens[i]["collectedFeesToken1"] = int(bunni_token["collectedFeesToken1"]) - int(past_bunni_token["collectedFeesToken1"])
                else:
                    current_bunni_tokens[i]["collectedFeesToken0"] = int(bunni_token["collectedFeesToken0"])
                    current_bunni_tokens[i]["collectedFeesToken1"] = int(bunni_token["collectedFeesToken1"])

            # convert fee token amounts to WETH to get bribing weight
            for bunni_token in current_bunni_tokens:
                token0, token1 = to_address(bunni_token["pool"]["token0"]), to_address(bunni_token["pool"]["token1"])

                bribe_weights[bunni_token["gauge"]] = get_token_weth_value(token0, bunni_token["collectedFeesToken0"]) + get_token_weth_value(token1, bunni_token["collectedFeesToken1"])
            
            total_bribe_weight = 0
            for bribe_weight in bribe_weights.values():
                total_bribe_weight += bribe_weight

            print(f"Total bribe weight: {total_bribe_weight / 1e18} (should be close to the total fee claimed in WETH)")

            ######################################################################
            # Use fees as bribe on Hidden Hand
            ######################################################################

            actual_total_weth_amount = sum([int(total_weth_amount * bribe_weights[gauge] / total_bribe_weight) for gauge in bribe_weights.keys()]) # prevents small rounding errors from making tx revert
            print(f"Total WETH actually used for bribing: {actual_total_weth_amount / 1e18}")
            weth_contract.approve(bribe_vault, actual_total_weth_amount)

            for gauge in bribe_weights.keys():
                proposal = to_hex(keccak(to_bytes(hexstr=gauge)))
                bribe_amount = int(total_weth_amount * bribe_weights[gauge] / total_bribe_weight)
                bunni_bribe.depositBribeERC20(proposal, weth, bribe_amount)
        else:
            print(f"Error: {response.status_code}")
    else:
        print(f"Error: {response.status_code}")

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)

def get_token_weth_value(token, token_amount):
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    if token == weth:
        return token_amount

    url = f"https://api.0x.org/swap/v1/quote?buyToken=WETH&sellToken={token}&sellAmount={token_amount}"
    response = requests.get(url)

    if response.status_code == 200:
        swap_data = response.json()
        return int(swap_data["buyAmount"])
    else:
        print(f"Error: {response.status_code}, token: {token}, token_amount: {token_amount}")
        return 0