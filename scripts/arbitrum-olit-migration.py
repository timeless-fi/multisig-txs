# brownie run scripts/arbitrum-olit-migration.py --network mainnet-fork

from brownie_safe import BrownieSafe
import json
from brownie import Contract, network


def main():
    # configs
    gov_safe = BrownieSafe("0x9a8FEe232DCF73060Af348a1B62Cdb0a19852d13")

    # abis
    with open("scripts/abi/RootGauge.json") as f:
        gauge_abi = json.loads(f.read())
    with open("scripts/abi/RootGaugeFactory.json") as f:
        root_factory_abi = json.loads(f.read())
    with open("scripts/abi/ChildGaugeFactory.json") as f:
        child_factory_abi = json.loads(f.read())
    with open("scripts/abi/XERC20Lockbox.json") as f:
        lockbox_abi = json.loads(f.read())
    with open("scripts/abi/ERC20.json") as f:
        erc20_abi = json.loads(f.read())

    # config
    gauges = [
        "0xa9092a2cfd11f8e42cfd84c0217743f28b3c285c",
        "0x00b20ffd6c2d27a5b9764ad2367f60e16e08ed3b",
        "0x5fb10c79c7198d18f69a9aeb64e3feab66778e48",
        "0x491efe8d9c2a5ee66bc404b49d40aa7397e355b7",
        "0x846b89167040e655de785c8ddda57866182e268b",
        "0x4b6052e271c1a1af0eb62376fbba95fa4a1e282b",
        "0xa41036c55ee6f1cfe864145ded4f5ef6b3505df8",
        "0x730deabcb65dc273613320ba6cf9ddc213661d12",
        "0x45100bd2b5c8b36fdf49808abfe3408ff803fb0d",
        "0xa665f67e1743415d7fd0b3c40c7cf90bc1e7bb39",
        "0x677ed6de139058ede31b2fb296f827f8c35a632a",
        "0x0f591dcf2601a93688368f2952cc036f4ae7f88a",
        "0x5665eaa91d49b2807e185647ce8489f39c0e5fa4",
        "0x21a0e3db0052bffcb14e0229e28e1bee575b24e9",
        "0x42c2944bacb504012835fc097423deb77aa4ca38",
        "0xc4f2733fad503f58429433dfbad0b8adc7d0433a",
        "0x6ffac7b1db79460093c06ceae86d3baca2f3cdfd",
        "0xc21d0edf5a6e7d00b96afc9bafc6e46f64159005",
        "0x16fc75bed380d406bcb403bb4ef748f85a110857",
        "0x10d4eec4c76e90de91e51746568ccc0c0d7816e1",
        "0x4c4504b5178a9358008eac70a3a2dcfd9972a3c5",
    ]
    new_bridger = "0x53A6a140e72720708fc5C83F61DcF92169CaD705"
    factory_address = "0xe4666F0937B62d64C10316DB0b7061549F87e95F"
    old_olit_address = "0x0ffB33812FA5cd8bCE181Db3FD76E11935105B12"
    xerc20_address = "0x24F21b1864d4747a5c99045c96dA11DBFDa378f7"

    """ ######################################################################
    # Set bridger in factory
    ######################################################################

    root_factory = Contract.from_abi(
        "RootGaugeFactory",
        factory_address,
        root_factory_abi,
        gov_safe.account,
    )
    root_factory.set_bridger(42161, new_bridger)

    ######################################################################
    # Set bridger in gauges
    ######################################################################

    for gauge in gauges:
        gauge_contract = Contract.from_abi(
            "RootGauge", gauge, gauge_abi, gov_safe.account
        )
        gauge_contract.update_bridger()

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx) """

    ######################################################################
    # Switch network to L2
    ######################################################################

    network.disconnect()
    network.connect("arbitrum-main-fork")

    # switch to multisig on L2
    gov_safe = BrownieSafe("0x77B1825b2FeB8AA3F8CF78809e7AEb18E0dF719d")

    ######################################################################
    # Set xERC20 as new token in factory
    ######################################################################

    child_factory = Contract.from_abi(
        "ChildGaugeFactory",
        factory_address,
        child_factory_abi,
        gov_safe.account,
    )
    child_factory.set_token(xerc20_address)

    ######################################################################
    # Rescue old token from child factory
    ######################################################################

    old_olit = Contract.from_abi(
        "oLIT",
        old_olit_address,
        erc20_abi,
        gov_safe.account,
    )
    rescued_amount = old_olit.balanceOf(child_factory.address)
    child_factory.rescue_token(old_olit.address, gov_safe.account.address)

    ######################################################################
    # Deposit old token into lockbox
    ######################################################################

    lockbox = Contract.from_abi(
        "XERC20Lockbox",
        "0x8052E39b6558F1b897525AAD694181930AF0Cc63",
        lockbox_abi,
        gov_safe.account,
    )
    old_olit.approve(lockbox.address, rescued_amount)
    lockbox.depositTo(child_factory.address, rescued_amount)

    ######################################################################
    # Submit transaction to gov Gnosis Safe
    ######################################################################

    # generate safe tx
    safe_tx = gov_safe.multisend_from_receipts()

    # sign safe tx
    gov_safe.sign_with_frame(safe_tx).hex()

    # post tx
    gov_safe.post_transaction(safe_tx)
