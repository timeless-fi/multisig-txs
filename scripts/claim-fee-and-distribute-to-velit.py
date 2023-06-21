# brownie run scripts/claim-fee-and-distribute-to-velit.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract, network
import json
import requests

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/BunniHub.json') as f:
        bunni_hub_abi = json.loads(f.read())
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())
    with open('scripts/abi/FeeDistributor.json') as f:
        fee_distributor_abi = json.loads(f.read())

    # config
    swap_slippage = "0.01"
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    tokens = [
        "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF", # AURA
        # "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D", # LQTY
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", # USDC
        "0x24C19F7101c1731b85F1127EaA0407732E36EcDD", # SGT
        # "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", # LDO
        "0x853d955aCEf822Db058eb8505911ED77F175b99e", # FRAX
        # "0x5E8422345238F34275888049021821E8E08CAa1f", # frxETH
        # "0x111111111117dC0aa78b770fA6A738034120C302", # 1INCH
        # "0x6B175474E89094C44Da98b954EedeAC495271d0F", # DAI
        "0xf7e945FcE8F19302AaCc7E1418b0A0bdef89327B", # IZE
        # "0x1EA48B9965bb5086F3b468E50ED93888a661fc17", # MON
        # "0x3472A5A71965499acd81997a54BBA8D852C6E53d", # BADGER
        # "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", # UNI
        # "0x6bB61215298F296C55b19Ad842D3Df69021DA2ef", # DOP
        # "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", # WBTC
        "0xF915110898d9a455Ad2DA51BF49520b41655Ccea" # TAI
    ]

    # contracts
    bunni_hub = Contract.from_abi(
        "BunniHub", "0xb5087F95643A9a4069471A28d32C569D9bd57fE4", bunni_hub_abi, gov_safe.account)
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    
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

        url = f"https://api.0x.org/swap/v1/quote?buyToken=WETH&sellToken={token}&sellAmount={token_amount}&slippagePercentage={swap_slippage}"
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
    fee_distributor = Contract.from_abi("FeeDistributor", "0x951f99350d816c0E160A2C71DEfE828BdfC17f12", fee_distributor_abi, gov_safe.account)

    ######################################################################
    # Distribute WETH
    ######################################################################
    
    weth_contract.approve(fee_distributor.address, total_weth_amount)
    fee_distributor.depositToken(weth, total_weth_amount)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)