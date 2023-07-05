# brownie run scripts/raise-dop-cap.py --network mainnet-fork

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
    # Uncap SGT-WETH gauge
    ######################################################################

    gauge = "0xC118C27C5e364054C0e206049c7e09C7D9D18989"    
    gauge_contract = Contract.from_abi("TimelessLiquidityGauge", gauge, gauge_abi, gov_safe.account)
    weight_cap = int(0.1e18) # 10%
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
