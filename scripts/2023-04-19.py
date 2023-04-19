# brownie run scripts/2023-04-19.py --network mainnet-fork

from ape_safe import ApeSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/VestingEscrowFactory.json') as f:
        factory_abi = json.loads(f.read())
    with open('scripts/abi/ERC20.json') as f:
        erc20_abi = json.loads(f.read())

    # config
    growth_unit = "0xa3afB67F0215c2782aEB8F6B4cE11c2293cf1C2a"
    eoa = "0xe7Edf25702f5EE446f55Fe21c579F9018f3d5Bc4"
    bal_grant = "0x89f67f3054bFD662971854190Dbc18dcaBb416f6"

    # contracts
    weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    weth_contract = Contract.from_abi("WETH", weth, erc20_abi, gov_safe.account)
    lit = gov_safe.contract("0xfd0205066521550D7d7AB19DA8F72bb004b4C341")
    usdc = gov_safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    llamapay_factory = Contract.from_abi(
        "VestingEscrowFactory", "0xB93427b83573C8F27a08A909045c3e809610411a", factory_abi, gov_safe.account)

    ######################################################################
    # Transfer 60k USDC to growth unit
    ######################################################################

    usdc.transfer(growth_unit, int(60000e6))

    ######################################################################
    # Stream 259,824.95 USDC over 1 year to growth unit
    ######################################################################

    day = 24 * 60 * 60
    vesting_duration = 365 * day # 1 year
    vesting_start = 1681776000 # 2023/4/18 12am UTC
    usdc_amount = int(259824.95 * 1e6)

    usdc.approve(llamapay_factory.address, usdc_amount)
    llamapay_factory.deploy_vesting_contract(usdc.address, growth_unit, usdc_amount, vesting_duration, vesting_start)

    ######################################################################
    # Stream 5m LIT over 7 days to growth unit and 10m LIT over 1+3 years to EOA
    ######################################################################

    amount1 = int(5e6 * 1e18)
    amount2 = int(10e6 * 1e18)
    lit.approve(llamapay_factory.address, amount1 + amount2)

    llamapay_factory.deploy_vesting_contract(lit.address, growth_unit, amount1, 7 * day, vesting_start)

    cliff_length = 365 * day # 1 year
    vesting_duration = 4 * 365 * day # 4 years
    llamapay_factory.deploy_vesting_contract(lit.address, eoa, amount2, vesting_duration, vesting_start, cliff_length)

    ######################################################################
    # Send WETH to Balancer grant contract
    ######################################################################

    weth_amount = int(42133432598790311122)
    weth_contract.transfer(bal_grant, weth_amount)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
