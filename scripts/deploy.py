import os
import time

import brownie
from brownie import (
    BFR,
    USDC,
    BufferBinaryOptions,
    BufferBinaryPool,
    BufferRouter,
    Faucet,
    OptionReader,
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
    faucet_address = None
    option_reader_address = None
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

    if network.show_active() == "arb-goerli":
        allow_revert = True
        pool_admin = accounts.add(os.environ["POOL_PK"])
        admin = accounts.add(os.environ["BFR_PK"])
        publisher = "0x2156972c36088AA94fAeF84359C75FB4Bb83c745"
        open_keeper = "0xc5A774124960281307428FbeE0452D324911258B"
        close_keeper = "0xC5bbb4FC79f6c778F74F0af40991777C7204e16E"
        sfd = "0x32A49a15F8eE598C1EeDc21138DEb23b391f425b"
        asset_pair = "EURCHF"
        asset_category = 0

        token_contract_address = "0x49932a64C16E8369d73EA9342a97912Cb90e75C2"
        pool_address = "0xb2685B520Eb93769755b0B2c96dca1D10459F378"
        router_contract_address = "0x96a897A1bedF11BE69610DE73941c50d47b5106e"
        referral_storage_address = "0x5681334C57d4CC11A0D0A72c49766eAD85bA6a4f"
        option_reader_address = "0x249a8144B0fb7a6f718a191863F4a1884ec05b35"
        faucet_address = "0x9D26cf2f6914c93e4c72E2554b2036dbF77D6b5c"

        # options_address = "0xB05A6327b13047B79Cb4008063062e4f7fFb52E6"  # ETH-BTC
        # options_address = ""  # BTC-USD
        # options_address = "0xDa8D5Fe04567Eb02Cf2bE5aD7c084cAA3893F9aF"  # ETH-USD
        # options_address = ""  # EUR-USD

    print(pool_admin, admin)
    print(pool_admin.balance() / 1e18, admin.balance() / 1e18)

    ########### Get TokenX ###########
    if not token_contract_address:
        token_contract = deploy_contract(
            admin,
            network,
            BFR,
            [],
        )
        token_contract_address = token_contract.address
    token_contract = BFR.at(token_contract_address)

    ########### Router ###########

    if not router_contract_address:
        router_contract = deploy_contract(
            admin,
            network,
            BufferRouter,
            [publisher],
        )
        router_contract_address = router_contract.address
        router_contract.setKeeper(
            open_keeper,
            True,
            {"from": admin},
        )
        router_contract.setKeeper(
            close_keeper,
            True,
            {"from": admin},
        )

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
            [token_contract_address, 600],
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
        if asset_category == 0:
            market_times = [
                (17, 0, 23, 59),
                (0, 0, 23, 59),
                (0, 0, 23, 59),
                (0, 0, 23, 59),
                (0, 0, 23, 59),
                (0, 0, 15, 59),
                (0, 0, 0, 0),
            ]
            option_config.setMarketTime(market_times, {"from": admin})

        assert option_config.pool() == pool

    ########### Deploy referral storage ###########

    if referral_storage_address:
        referral_storage = ReferralStorage.at(referral_storage_address)
    else:

        referral_storage = deploy_contract(admin, network, ReferralStorage, [])
        referral_storage_address = referral_storage.address
        referral_storage.configure([1, 2, 3], [25e3, 50e3, 75e3], {"from": admin})

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
    ########### Deploy Option Reader ###########
    if not option_reader_address:
        deploy_contract(
            admin,
            network,
            OptionReader,
            [pool_address],
        )

    ########### Deploy Faucet ###########
    if not faucet_address:
        faucet = deploy_contract(
            admin,
            network,
            Faucet,
            [
                token_contract_address,
                keeper,
            ],
        )
        token_contract.transfer(faucet, 100000e18, {"from": admin})

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
    print(options.address)
