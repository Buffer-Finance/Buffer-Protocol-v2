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
        publisher_pk = os.environ["USER_PK"]
        keeper = accounts.add(os.environ["BFR_PK"])
        user = accounts.add(publisher_pk)

    token_contract_address = "0x1d4242278c05b73B89E9483B87741Db2Ee866d54"
    pool_address = "0x81905a9c020d9b395AbE71B9E22D5f3246D29045"
    router_contract_address = "0x767173fd3DD0A12df0f17D90A9810020d1c22A33"
    referral_storage_address = "0xB2AD3f7079b5E4DB460506C7d45F09BC10D60E13"
    options_address = "0xb5c2fAEeF541Da50448589272cd7ca2fDb06C339"  # EUR-BUSD
    # options_address = "0x39DDC21420e8c721Cb880De9a218963393022381"  # ETH-BTC
    # options_address = "0x1C1Bb44A1CF1566659B94a0615b8443fC6144368"  # BTC-BUSD
    # options_address = "0x7cf2809e96de47A5FbAF92d1274e51827e9BdC4F"  # ETH-BUSD

    print(pool_admin, admin)
    print(pool_admin.balance() / 1e18, admin.balance() / 1e18)

    ########### Get TokenX ###########

    token_contract = USDC.at(token_contract_address)
    pool = BufferBinaryPool.at(pool_address)
    router_contract = BufferRouter.at(router_contract_address)
    options = BufferBinaryOptions.at(options_address)
    config_address = options.config()
    config = OptionsConfig.at(config_address)
    print(config)
    # token_contract.approve(
    #     pool_address,
    #     10000e6,
    #     {"from": admin},
    # )
    # pool.provide(
    #     1000e6,
    #     0,
    #     {"from": admin},
    # )
    token_contract.transfer(user, 20e6, {"from": admin})
    token_contract.approve(
        router_contract_address,
        100e6,
        {"from": user},
    )

    for _ in range(10):
        expected_strike = 1.035e8
        next_queue_id = router_contract.nextQueueId()
        next_option_id = options.nextTokenId()
        option_params = [
            1e6,
            3600,
            False,
            options.address,
            expected_strike,
            100,
            True,
            "",
            0,
        ]

        router_contract.initiateTrade(
            *option_params,
            {"from": user},
        )
        queued_trade = router_contract.queuedTrades(next_queue_id)
        open_params = [
            queued_trade[10],
            options.address,
            expected_strike,
        ]
        txn = router_contract.resolveQueuedTrades(
            [(next_queue_id, *open_params, get_signature(*open_params, publisher_pk))],
            {"from": keeper},
        )
        print(options.options(next_option_id))
        print(next_queue_id, next_option_id, txn.info())

    save_flat(OptionsConfig, "OptionsConfig")
