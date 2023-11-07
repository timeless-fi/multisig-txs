# brownie run scripts/fix-treasury-split.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network


def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open("scripts/abi/RevenueSplitter.json") as f:
        splitter_abi = json.loads(f.read())

    # contracts
    revenue_splitter = Contract.from_abi(
        "RevenueSplitter",
        "0xb6859913BaE3E18d16198485643F8BB017E96B7f",
        splitter_abi,
        gov_safe.account,
    )

    ######################################################################
    # Update revenue splitter params to distribute 25% of revenue to veLIT
    ######################################################################

    revenue_splitter.setTreasurySplit(int(0.75e9)) # 25% to veLIT, 75% to treasury

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
