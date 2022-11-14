import os
import time

import brownie
from brownie import (
    BFR,
    USDC,
    BufferBinaryOptions,
    BufferBinaryPool,
    BufferRouter,
    OptionsConfig,
    ReferralStorage,
    accounts,
    network,
)
from colorama import Fore, Style
from eth_account import Account
from eth_account.messages import encode_defunct

from .utility import deploy_contract, save_flat


def get_signature(timestamp, token, price, publisher_pk):
    web3 = brownie.network.web3
    key = publisher_pk
    msg_hash = web3.solidityKeccak(
        ["uint256", "address", "uint256"], [timestamp, token, int(price)]
    )
    signed_message = Account.sign_message(encode_defunct(msg_hash), key)

    def to_32byte_hex(val):
        return web3.toHex(web3.toBytes(val).rjust(32, b"\0"))

    return to_32byte_hex(signed_message.signature)


def main():
    router_contract_address = None
    pool_address = None
    token_contract_address = None
    option_config_address = None
    options_address = None
    referral_storage_address = None

    if network.show_active() == "development":
        allow_revert = True
        pool_admin = accounts[0]
        admin = accounts[1]
        publisher = accounts.add()
        publisher_pk = publisher.private_key()
        keeper = accounts[3]

    if network.show_active() == "arbitrum-test-nitro":
        allow_revert = True
        pool_admin = accounts.add(os.environ["POOL_PK"])
        admin = accounts.add(os.environ["BFR_PK"])
        publisher = "0x32A49a15F8eE598C1EeDc21138DEb23b391f425b"
        publisher_pk = (
            "258bc07202e69bd79af9af8380e77a0142175b17f5401a6efd8f734c4e11d63c"
        )
        keeper = accounts.add(os.environ["BFR_PK"])
        user = accounts.add(publisher_pk)

    token_contract_address = "0xf6EDB295c08c59fea88d770cd3202BF4912667dC"
    pool_address = "0x50B25Bf6f1a7e7edd16ae8841F34b221E31b5409"
    router_contract_address = "0x233Da126e42037e6996F6243bd988568fb57B547"
    # options_address = "0x1297A832701E7ae7925b196080eA99242DF53C5d"  # EUR-BUSD
    # options_address = "0x430FA5C50BDd956a1242b4CA1265875bE00e9cA6"  # ETH-BTC
    # options_address = "0xd5d01849e028f5c7B69c9653D9EA01cB88A3B154"  # BTC-BUSD
    options_address = "0x59A2D66B13168A52965a257007B1DFD7CA89cCA3"  # ETH-BUSD

    print(pool_admin, admin)
    print(pool_admin.balance() / 1e18, admin.balance() / 1e18)

    ########### Get TokenX ###########

    token_contract = USDC.at(token_contract_address)
    pool = BufferBinaryPool.at(pool_address)
    router_contract = BufferRouter.at(router_contract_address)
    options = BufferBinaryOptions.at(options_address)

    router_contract.setKeeper(
        admin,
        True,
        {"from": admin},
    )
    params = []
    for id in range(0, 5):
        option_data = options.options(id)
        close_params = (
            option_data[5],
            options.address,
            option_data[1] + 1e8,
        )
        params.append(
            (
                id,
                *close_params,
                get_signature(
                    *close_params,
                    publisher_pk,
                ),
            )
        )

    txn = router_contract.unlockOptions(
        params,
        {"from": keeper},
    )
    print(txn.info())
