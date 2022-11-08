#!/usr/bin/python3

import time
from enum import IntEnum

import pytest

ONE_DAY = 86400


class OptionType(IntEnum):
    ALL = 0
    PUT = 1
    CALL = 2
    NONE = 3


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def contracts(
    accounts,
    USDC,
    BFR,
    BufferBinaryPool,
    BufferBinaryOptions,
    OptionConfigBinaryV2,
    OptionRouter,
    SettlementFeeDisbursal,
    TraderNFT,
    KeeperPayment,
    ReferralStorage,
):

    publisher = accounts.add()
    ibfr_contract = BFR.deploy({"from": accounts[0]})

    tokenX = USDC.deploy({"from": accounts[0]})

    binary_pool_atm = BufferBinaryPool.deploy(
        tokenX.address, {"from": accounts[0]}
    )
    OPTION_ISSUER_ROLE = binary_pool_atm.OPTION_ISSUER_ROLE()
    keeper_contract = KeeperPayment.deploy(
        ibfr_contract, {"from": accounts[0]})
    router = OptionRouter.deploy(
        publisher, keeper_contract.address, {"from": accounts[0]}
    )
    trader_nft = TraderNFT.deploy(accounts[9], {"from": accounts[0]})

    ROUTER_ROLE = keeper_contract.ROUTER_ROLE()
    BOT_ROLE = router.BOT_ROLE()
    router.grantRole(
        BOT_ROLE,
        accounts[4],
        {"from": accounts[0]},
    )
    keeper_contract.grantRole(
        ROUTER_ROLE,
        router.address,
        {"from": accounts[0]},
    )

    print("############### Binary ATM Options 1 #################")
    binary_options_config_atm = OptionConfigBinaryV2.deploy(
        binary_pool_atm.address,
        {"from": accounts[0]},
    )
    referral_contract = ReferralStorage.deploy({"from": accounts[0]})

    binary_european_options_atm = BufferBinaryOptions.deploy(
        tokenX.address,
        binary_pool_atm.address,
        binary_options_config_atm.address,
        referral_contract.address,
        1,
        {"from": accounts[0]},
    )
    referral_contract.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm.address,
        {"from": accounts[0]},
    )
    settlement_fee_disbursal = SettlementFeeDisbursal.deploy(
        tokenX.address,
        binary_options_config_atm.address,
        binary_european_options_atm.address,
        accounts[6],
        accounts[7],
        accounts[8],
        accounts[9],
        {"from": accounts[0]},
    )

    binary_options_config_atm.setSettlementFeeDisbursalContract(
        settlement_fee_disbursal.address,
        {"from": accounts[0]},
    )

    binary_european_options_atm.approveSFDContractToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_european_options_atm.approvePoolToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_pool_atm.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm.address,
        {"from": accounts[0]},
    )
    binary_european_options_atm.grantRole(
        ROUTER_ROLE,
        router.address,
        {"from": accounts[0]},
    )
    binary_european_options_atm.grantRole(
        BOT_ROLE,
        accounts[4],
        {"from": accounts[0]},
    )
    binary_options_config_atm.settraderNFTContract(trader_nft.address)
    binary_european_options_atm.initialize(15e2, 15e2, {"from": accounts[0]})

    print("############### Binary ATM Options 2 #################")
    binary_options_config_atm_2 = OptionConfigBinaryV2.deploy(
        binary_pool_atm.address,
        {"from": accounts[0]},
    )

    binary_european_options_atm_2 = BufferBinaryOptions.deploy(
        tokenX.address,
        binary_pool_atm.address,
        binary_options_config_atm_2.address,
        referral_contract.address,
        1,
        {"from": accounts[0]},
    )
    referral_contract.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm_2.address,
        {"from": accounts[0]},
    )
    settlement_fee_disbursal_2 = SettlementFeeDisbursal.deploy(
        tokenX.address,
        binary_options_config_atm_2.address,
        binary_european_options_atm_2.address,
        accounts[6],
        accounts[7],
        accounts[8],
        accounts[9],
        {"from": accounts[0]},
    )

    binary_options_config_atm_2.setSettlementFeeDisbursalContract(
        settlement_fee_disbursal_2.address,
        {"from": accounts[0]},
    )

    binary_european_options_atm_2.approveSFDContractToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_european_options_atm_2.approvePoolToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_european_options_atm_2.grantRole(
        ROUTER_ROLE,
        router.address,
        {"from": accounts[0]},
    )
    binary_european_options_atm_2.grantRole(
        BOT_ROLE,
        accounts[4],
        {"from": accounts[0]},
    )
    binary_pool_atm.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm_2.address,
        {"from": accounts[0]},
    )
    binary_options_config_atm_2.settraderNFTContract(trader_nft.address)
    binary_european_options_atm_2.initialize(15e2, 15e2, {"from": accounts[0]})

    print("############### Binary ATM Options 3 #################")
    binary_options_config_atm_3 = OptionConfigBinaryV2.deploy(
        binary_pool_atm.address,
        {"from": accounts[0]},
    )

    binary_european_options_atm_3 = BufferBinaryOptions.deploy(
        tokenX.address,
        binary_pool_atm.address,
        binary_options_config_atm_3.address,
        referral_contract.address,
        0,
        {"from": accounts[0]},
    )
    referral_contract.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm_3.address,
        {"from": accounts[0]},
    )
    settlement_fee_disbursal_3 = SettlementFeeDisbursal.deploy(
        tokenX.address,
        binary_options_config_atm_3.address,
        binary_european_options_atm_3.address,
        accounts[6],
        accounts[7],
        accounts[8],
        accounts[9],
        {"from": accounts[0]},
    )

    binary_options_config_atm_3.setSettlementFeeDisbursalContract(
        settlement_fee_disbursal_3.address,
        {"from": accounts[0]},
    )

    binary_european_options_atm_3.approveSFDContractToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_european_options_atm_3.approvePoolToTransferTokenX(
        {"from": accounts[0]},
    )
    binary_pool_atm.grantRole(
        OPTION_ISSUER_ROLE,
        binary_european_options_atm_3.address,
        {"from": accounts[0]},
    )
    binary_european_options_atm_3.grantRole(
        ROUTER_ROLE,
        router.address,
        {"from": accounts[0]},
    )

    binary_european_options_atm_3.grantRole(
        BOT_ROLE,
        accounts[4],
        {"from": accounts[0]},
    )
    binary_options_config_atm_3.settraderNFTContract(trader_nft.address)
    binary_european_options_atm_3.initialize(15e2, 15e2, {"from": accounts[0]})

    print("############### Deploying BFR pool contracts #################")

    bfr_pool_atm = BufferBinaryPool.deploy(
        ibfr_contract.address, {"from": accounts[0]}
    )

    bfr_binary_options_config_atm = OptionConfigBinaryV2.deploy(
        bfr_pool_atm.address,
        {"from": accounts[0]},
    )

    bfr_binary_european_options_atm = BufferBinaryOptions.deploy(
        ibfr_contract.address,
        bfr_pool_atm.address,
        bfr_binary_options_config_atm.address,
        referral_contract.address,
        1,
        {"from": accounts[0]},
    )
    referral_contract.grantRole(
        OPTION_ISSUER_ROLE,
        bfr_binary_european_options_atm.address,
        {"from": accounts[0]},
    )
    bfr_settlement_fee_disbursal = SettlementFeeDisbursal.deploy(
        ibfr_contract.address,
        bfr_binary_options_config_atm.address,
        bfr_binary_european_options_atm.address,
        accounts[6],
        accounts[7],
        accounts[8],
        accounts[9],
        {"from": accounts[0]},
    )

    bfr_binary_options_config_atm.setSettlementFeeDisbursalContract(
        bfr_settlement_fee_disbursal.address,
        {"from": accounts[0]},
    )

    bfr_binary_european_options_atm.approveSFDContractToTransferTokenX(
        {"from": accounts[0]},
    )
    bfr_binary_european_options_atm.approvePoolToTransferTokenX(
        {"from": accounts[0]},
    )
    OPTION_ISSUER_ROLE = bfr_pool_atm.OPTION_ISSUER_ROLE()
    bfr_pool_atm.grantRole(
        OPTION_ISSUER_ROLE,
        bfr_binary_european_options_atm.address,
        {"from": accounts[0]},
    )

    bfr_binary_european_options_atm.grantRole(
        ROUTER_ROLE,
        router.address,
        {"from": accounts[0]},
    )

    bfr_binary_european_options_atm.grantRole(
        BOT_ROLE,
        accounts[4],
        {"from": accounts[0]},
    )
    bfr_binary_options_config_atm.settraderNFTContract(trader_nft.address)
    bfr_binary_european_options_atm.initialize(
        15e2, 15e2, {"from": accounts[0]})
    referral_contract.initialize({"from": accounts[0]})

    router.setContractRegistry(bfr_binary_european_options_atm.address, True)
    router.setContractRegistry(binary_european_options_atm_2.address, True)
    router.setContractRegistry(binary_european_options_atm_3.address, True)

    return {
        "tokenX": tokenX,
        "referral_contract": referral_contract,
        "binary_pool_atm": binary_pool_atm,
        "binary_options_config_atm": binary_options_config_atm,
        "binary_european_options_atm": binary_european_options_atm,
        "binary_options_config_atm_2": binary_options_config_atm_2,
        "binary_european_options_atm_2": binary_european_options_atm_2,
        "binary_options_config_atm_3": binary_options_config_atm_3,
        "binary_european_options_atm_3": binary_european_options_atm_3,
        "router": router,
        "trader_nft_contract": trader_nft,
        "settlement_fee_disbursal": settlement_fee_disbursal,
        "ibfr_contract": ibfr_contract,
        "bfr_pool_atm": bfr_pool_atm,
        "bfr_binary_options_config_atm": bfr_binary_options_config_atm,
        "bfr_binary_european_options_atm": bfr_binary_european_options_atm,
        "bfr_settlement_fee_disbursal": bfr_settlement_fee_disbursal,
        "publisher": publisher,
        "keeper_contract": keeper_contract,
        'settlement_fee_disbursal': settlement_fee_disbursal
    }
