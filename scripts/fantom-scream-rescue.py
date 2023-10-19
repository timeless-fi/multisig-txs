# brownie run scripts/fantom-scream-rescue.py --network ftm-main-fork

from brownie_safe import BrownieSafe
import json
import pandas
from brownie import Contract, accounts, chain, history, web3

def main():
    # configs
    gov_safe = BrownieSafe("0x566F782664fB79E10823795695500f29e7D95D1d")

    # abis
    with open("scripts/abi/ERC20.json") as f:
        erc20_abi = json.loads(f.read())

    # contracts
    bdei = Contract.from_abi(
        "bDEI",
        "0x05f6ea7F80BDC07f6E0728BbBBAbebEA4E142eE8",
        erc20_abi,
        gov_safe.account,
    )
    fusd = Contract.from_abi(
        "fUSD",
        "0xAd84341756Bf337f5a0164515b1f6F993D194E1f",
        erc20_abi,
        gov_safe.account,
    )
    scream = Contract.from_abi(
        "SCREAM",
        "0xe0654C8e6fd4D733349ac7E09f6f23DA256bF475",
        erc20_abi,
        gov_safe.account,
    )

    # csvs
    bdei_recipients = pandas.read_csv("scripts/data/bDEI_distribution.csv")
    fusd_recipients = pandas.read_csv("scripts/data/FUSD_distribution.csv")
    scream_recipients = pandas.read_csv("scripts/data/SCREAM_distribution.csv")

    batch_size = 300

    ######################################################################
    # Transfer assets
    ######################################################################

    safe_tx = None
    nonce = 15

    counter = 0
    for _, row in bdei_recipients.iterrows():
        bdei.transfer(row[0], row[1])

        counter += 1
        if counter == batch_size:
            counter = 0
            safe_tx = gov_safe.multisend_from_receipts(safe_nonce=nonce)
            gov_safe.sign_with_frame(safe_tx).hex()
            gov_safe.post_transaction(safe_tx)
            history.clear()
            nonce += 1
    if counter != 0:
        safe_tx = gov_safe.multisend_from_receipts(safe_nonce=nonce)
        gov_safe.sign_with_frame(safe_tx).hex()
        gov_safe.post_transaction(safe_tx)
        history.clear()
        nonce += 1

    counter = 0
    for _, row in fusd_recipients.iterrows():
        fusd.transfer(row[0], row[1])

        counter += 1
        if counter == batch_size:
            counter = 0
            safe_tx = gov_safe.multisend_from_receipts(safe_nonce=nonce)
            gov_safe.sign_with_frame(safe_tx).hex()
            gov_safe.post_transaction(safe_tx)
            history.clear()
            nonce += 1
    if counter != 0:
        safe_tx = gov_safe.multisend_from_receipts(safe_nonce=nonce)
        gov_safe.sign_with_frame(safe_tx).hex()
        gov_safe.post_transaction(safe_tx)
        history.clear()
        nonce += 1

    counter = 0
    for _, row in scream_recipients.iterrows():
        scream.transfer(row[0], row[1])

        counter += 1
        if counter == batch_size:
            counter = 0
            safe_tx = gov_safe.multisend_from_receipts(safe_nonce=nonce)
            gov_safe.sign_with_frame(safe_tx).hex()
            gov_safe.post_transaction(safe_tx)
            history.clear()
            nonce += 1
    if counter != 0:
        safe_tx = gov_safe.multisend_from_receipts(safe_nonce=nonce)
        gov_safe.sign_with_frame(safe_tx).hex()
        gov_safe.post_transaction(safe_tx)
        history.clear()
        nonce += 1
