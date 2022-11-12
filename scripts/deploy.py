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


def get_signature(timestamp, token, price, publisher):
    web3 = brownie.network.web3
    key = publisher.private_key
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

    assetUtilizationLimit = 10e2
    overallPoolUtilizationLimit = 64e2
    optionFeePerTxnLimitPercent = 5e2

    if network.show_active() == "development":
        allow_revert = True
        pool_admin = accounts[0]
        admin = accounts[1]
        publisher = accounts.add()
        keeper = accounts[3]
        sfd = accounts[4]
        asset_pair = "ETH-BTC"
        asset_category = 1

    if network.show_active() == "arbitrum-test-nitro":
        allow_revert = True
        pool_admin = accounts.add(os.environ["POOL_PK"])
        admin = accounts.add(os.environ["BFR_PK"])
        publisher = "0x32A49a15F8eE598C1EeDc21138DEb23b391f425b"
        keeper = accounts.add(os.environ["BFR_PK"])
        sfd = "0x32A49a15F8eE598C1EeDc21138DEb23b391f425b"
        asset_pair = "ETH-BUSD"
        asset_category = 1

        token_contract_address = "0x1d4242278c05b73B89E9483B87741Db2Ee866d54"
        pool_address = "0x81905a9c020d9b395AbE71B9E22D5f3246D29045"
        router_contract_address = "0x767173fd3DD0A12df0f17D90A9810020d1c22A33"
        referral_storage_address = "0xB2AD3f7079b5E4DB460506C7d45F09BC10D60E13"

    if network.show_active() == "arbitrum-main":
        allow_revert = True
        pool_admin = accounts.add(os.environ["POOL_PK"])
        admin = accounts.add(os.environ["BFR_PK"])
        publisher = ""

        token_contract_address = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
        pool_address = "0x37Cdbe3063002383B2018240bdAFE05127d36c3C"
        router_contract_address = "0xfAF5872850E720da9F7816fbD6589A846a885B83"

    print(pool_admin, admin)
    print(pool_admin.balance() / 1e18, admin.balance() / 1e18)

    ########### Get TokenX ###########

    if not token_contract_address:
        token_contract = deploy_contract(
            admin,
            network,
            USDC,
            [],
        )
        token_contract_address = token_contract.address
    elif network.show_active() == "development":
        token_contract = USDC.at(token_contract_address)

    ########### Router ###########

    if not router_contract_address:
        router_contract = deploy_contract(
            admin,
            network,
            BufferRouter,
            [publisher],
        )
        router_contract_address = router_contract.address

    else:
        router_contract = BufferRouter.at(router_contract_address)

    ########### Get pool ###########

    if pool_address:
        pool = BufferBinaryPool.at(pool_address)
    else:
        pool = deploy_contract(
            pool_admin,
            network,
            BufferBinaryPool,
            [token_contract_address],
        )
        pool_address = pool.address

        assert pool.tokenX() == token_contract_address
        assert pool.owner() == pool_admin

    ########### Get Options Config ###########

    if option_config_address:
        option_config = OptionsConfig.at(option_config_address)
    else:

        option_config = deploy_contract(
            admin,
            network,
            OptionsConfig,
            [
                pool_address,
            ],
        )
        option_config.setSettlementFeeDisbursalContract(sfd, {"from": admin})
        option_config_address = option_config.address

        assert option_config.pool() == pool

    ########### Deploy referral storage ###########

    if referral_storage_address:
        referral_storage = ReferralStorage.at(referral_storage_address)
    else:

        referral_storage = deploy_contract(admin, network, ReferralStorage, [])
        referral_storage_address = referral_storage.address

    ########### Deploy Options ###########
    if options_address:
        options = BufferBinaryOptions.at(options_address)

    else:
        options = deploy_contract(
            admin,
            network,
            BufferBinaryOptions,
            [
                token_contract_address,
                pool_address,
                option_config.address,
                referral_storage_address,
                asset_category,
                asset_pair,
            ],
        )
        assert options.tokenX() == token_contract_address

    ########### Grant Roles ###########

    OPTION_ISSUER_ROLE = pool.OPTION_ISSUER_ROLE()
    pool.grantRole(
        OPTION_ISSUER_ROLE,
        options.address,
        {"from": pool_admin, "allow_revert": allow_revert},
    )
    ROUTER_ROLE = options.ROUTER_ROLE()

    options.grantRole(
        ROUTER_ROLE,
        router_contract_address,
        {"from": admin},
    )

    router_contract.setContractRegistry(
        options.address,
        True,
        {"from": admin},
    )
    router_contract.setKeeper(
        keeper,
        True,
        {"from": admin},
    )
    ########### Approve the max amount ###########

    options.approvePoolToTransferTokenX(
        {"from": admin, "allow_revert": allow_revert},
    )

    ########### Setting configs ###########
    options.configure(15e2, 15e2, [0, 1, 2, 3], {"from": admin})

    option_config.setOptionFeePerTxnLimitPercent(
        optionFeePerTxnLimitPercent,
        {"from": admin, "allow_revert": allow_revert},
    )
    option_config.setOverallPoolUtilizationLimit(
        overallPoolUtilizationLimit,
        {"from": admin, "allow_revert": allow_revert},
    )
    option_config.setAssetUtilizationLimit(
        assetUtilizationLimit,
        {"from": admin, "allow_revert": allow_revert},
    )

    ########### Flat Files ###########

    save_flat(BufferBinaryOptions, "BufferBinaryOptions")
    save_flat(BufferRouter, "BufferRouter")
    save_flat(BufferBinaryPool, "BufferBinaryPool")
