# brownie run scripts/start-airdrop.py --network mainnet-fork

from ape_safe import ApeSafe
import json
from brownie import Contract

def main():
    # configs
    gov_safe = ApeSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open('scripts/abi/veMPHStaking.json') as f:
        vemph_staking_abi = json.loads(f.read())

    ######################################################################
    # Notify rewards to veMPH staking contract
    ######################################################################
    
    vemph_staking = Contract.from_abi(
        "veMPHStaking", "0x7Bf66285d9C4Fc6C1f4BE3A26b13BA0e1d62428E", vemph_staking_abi, gov_safe.account)
    lit = gov_safe.contract("0xfd0205066521550D7d7AB19DA8F72bb004b4C341")
    vemph_airdrop_amount = int(5e7 * 1e18) # 50 million LIT

    lit.approve(vemph_staking.address, vemph_airdrop_amount)
    vemph_staking.notifyRewardAmount(vemph_airdrop_amount)

    ######################################################################
    # Send tokens to the airdrop contract
    ######################################################################

    airdrop_contract = "0x6CA23531C1bE26b0119a1cD71CA3509c8D0853CC"
    airdrop_amount = int(1e7 * 1e18) # 10 million LIT
    lit.transfer(airdrop_contract, airdrop_amount)

    ######################################################################
    # Submit transaction to dev Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
