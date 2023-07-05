# brownie run scripts/uncap-ize-gauge.py --network mainnet-fork

from brownie_safe import BrownieSafe
from brownie import Contract
import json

def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/TimelessLiquidityGauge.json') as f:
        gauge_abi = json.loads(f.read())

    ######################################################################
    # Uncap IZE/USDC gauge
    ######################################################################

    gauge = "0xDE58296858d19313b5CD666629286d70E773bB7d"    
    gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
    weight_cap = int(1e18) # 100%
    gauge_contract.setRelativeWeightCap(weight_cap)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
