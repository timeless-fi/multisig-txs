# brownie run scripts/update-cap-bsn-gauge.py --network mainnet-fork

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

    gauge = "0x3f28CA531Cb4767EEBFD8974a7a782058C53AF6a"    
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
