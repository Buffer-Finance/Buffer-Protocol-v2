import os
import time

import brownie
from brownie import (
    BFR,
    USDC,
    BonusDistributor,
    BufferBinaryPool,
    EsBFR,
    MintableBaseToken,
    RewardDistributor,
    RewardRouterV2,
    RewardTracker,
    Token,
    Vester,
    accounts,
    network,
)
from colorama import Fore, Style

from .utility import deploy_contract, save_flat, transact


def main():
    feeBlpDistributorTokensPerInterval = 0  # USDC
    feeBfrDistributorTokensPerInterval = 0  # USDC
    stakedBfrDistributorTokensPerInterval = int(0.03e18)  # esBFR
    stakedBlpDistributorTokensPerInterval = int(0.03e18)  # esBFR
    bonusMultiplier = 10000  # 100% APR of bonus multiplier bnBFR

    vestingDuration = 365 * 24 * 60 * 60

    # Initial funds
    stakedBlpDistributorRewards = int(1_000_000e18)  # esBFR to be added

    usdc_address = None
    blp = None
    bfr = None
    esBfr = None
    bnBfr = None
    stakedBfrTracker = None
    stakedBfrDistributor = None

    bonusBfrTracker = None
    bonusBfrDistributor = None
    feeBfrTracker = None
    feeBfrDistributor = None
    feeBlpTracker = None
    feeBlpDistributor = None

    stakedBlpTracker = None
    stakedBlpDistributor = None
    bfrVester = None
    blpVester = None
    rewardRouter = None

    redeployedBFR = False
    redeployedBLP = True

    if network.show_active() == "development":
        bfr_admin = accounts[0]
        test_wallet = accounts[0]
        esbfr_minter = accounts[0]
        bnBfr_minter = accounts[0]
        governor = accounts[0]

    else:
        bfr_admin = accounts.add(os.environ["BFR_PK"])
        test_wallet = bfr_admin
        esbfr_minter = bfr_admin
        bnBfr_minter = bfr_admin
        governor = bfr_admin

        usdc_address = "0x49932a64C16E8369d73EA9342a97912Cb90e75C2"
        blp = "0xFd143dC1AC212B47F5e8916add6362B694568AEf"
        bfr = "0x89fEF05446aEA764C53a2f09bB763876FB57ea8E"
        esBfr = "0x92faca5302789730b427c04bc9A111b5733C054F"
        bnBfr = "0x8d3B227ebf5424f9b324908037bdD1db71F66521"
        stakedBfrTracker = "0xe243e72224b9E295551790b2C57638A27b8493af"
        bonusBfrTracker = "0xd9497B39399149D7572A7D740487F6e016C5D37e"
        feeBfrTracker = "0x39bcb63F0F4427CB9A21D4c3D957Bd8695f67B6d"
        stakedBfrDistributor = "0x1CBbff0d3928c35C1A41566e84AB1Efaa28f6770"
        bonusBfrDistributor = "0x349EF27A49def49D5ae9797387e0Bcc58E83BaC1"
        feeBfrDistributor = "0xAb578b4c9aEA25377357F5742Ef42bc9e9dB1CAF"
        bfrVester = "0x961F8988962a2A62ae6a189C0Af576eea40A7912"

    print(bfr_admin)
    print(bfr_admin.balance() / 1e18)

    if network.show_active() == "arbitrum-main":
        usdc_address = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
        bfr = "0x1A5B0aaF478bf1FDA7b934c76E7692D722982a6D"

    if not usdc_address:
        usdc = deploy_contract(
            bfr_admin,
            network,
            USDC,
            [],
        )
        usdc_address = usdc.address
    else:
        usdc = USDC.at(usdc_address)

    if blp:
        blp = BufferBinaryPool.at(blp)
    else:
        blp = deploy_contract(
            bfr_admin,
            network,
            BufferBinaryPool,
            [usdc_address, 600],
        )

    if bfr:
        bfr = BFR.at(bfr)
    else:
        bfr = deploy_contract(bfr_admin, network, BFR, [])
        assert bfr.balanceOf(bfr_admin) == 100 * (10**6) * (10 ** bfr.decimals())

    if esBfr:
        esBfr = EsBFR.at(esBfr)
    else:
        esBfr = deploy_contract(bfr_admin, network, EsBFR, [])
    if bnBfr:
        bnBfr = MintableBaseToken.at(bnBfr)
    else:
        bnBfr = deploy_contract(
            bfr_admin, network, MintableBaseToken, ["Bonus BFR", "bnBFR", 0]
        )

    # BFR staking
    if stakedBfrTracker:
        stakedBfrTracker = RewardTracker.at(stakedBfrTracker)
        stakedBfrDistributor = RewardDistributor.at(stakedBfrDistributor)
    else:
        stakedBfrTracker = deploy_contract(
            bfr_admin, network, RewardTracker, ["Staked BFR", "sBFR"]
        )
        stakedBfrDistributor = deploy_contract(
            bfr_admin,
            network,
            RewardDistributor,
            [esBfr.address, stakedBfrTracker.address],
        )
        transact(
            stakedBfrTracker.address,
            stakedBfrTracker.abi,
            "initialize",
            [bfr.address, esBfr.address],
            stakedBfrDistributor.address,
            sender=bfr_admin,
        )
        transact(
            stakedBfrDistributor.address,
            stakedBfrDistributor.abi,
            "updateLastDistributionTime",
            sender=bfr_admin,
        )

    if bonusBfrTracker:
        bonusBfrTracker = RewardTracker.at(bonusBfrTracker)
        bonusBfrDistributor = BonusDistributor.at(bonusBfrDistributor)
    else:
        bonusBfrTracker = deploy_contract(
            bfr_admin, network, RewardTracker, ["Staked + Bonus BFR", "sbBFR"]
        )
        bonusBfrDistributor = deploy_contract(
            bfr_admin,
            network,
            BonusDistributor,
            [bnBfr.address, bonusBfrTracker.address],
        )
        transact(
            bonusBfrTracker.address,
            bonusBfrTracker.abi,
            "initialize",
            [stakedBfrTracker.address],
            bonusBfrDistributor.address,
            sender=bfr_admin,
        )
        transact(
            bonusBfrDistributor.address,
            bonusBfrDistributor.abi,
            "updateLastDistributionTime",
            sender=bfr_admin,
        )

    if feeBfrTracker:
        feeBfrTracker = RewardTracker.at(feeBfrTracker)
        feeBfrDistributor = RewardDistributor.at(feeBfrDistributor)
    else:
        feeBfrTracker = deploy_contract(
            bfr_admin, network, RewardTracker, ["Staked + Bonus + Fee BFR", "sbfBFR"]
        )
        feeBfrDistributor = deploy_contract(
            bfr_admin, network, RewardDistributor, [usdc_address, feeBfrTracker.address]
        )
        # [contract][function](arguments, {"from": [account]})

        transact(
            feeBfrTracker.address,
            feeBfrTracker.abi,
            "initialize",
            [bonusBfrTracker.address, bnBfr.address],
            feeBfrDistributor.address,
            sender=bfr_admin,
        )
        transact(
            feeBfrDistributor.address,
            feeBfrDistributor.abi,
            "updateLastDistributionTime",
            sender=bfr_admin,
        )

    # BLP staking
    if feeBlpTracker:
        feeBlpTracker = RewardTracker.at(feeBlpTracker)
        feeBlpDistributor = RewardDistributor.at(feeBlpDistributor)
    else:
        feeBlpTracker = deploy_contract(
            bfr_admin, network, RewardTracker, ["Fee BLP", "fBLP"]
        )
        feeBlpDistributor = deploy_contract(
            bfr_admin, network, RewardDistributor, [usdc_address, feeBlpTracker.address]
        )
        transact(
            feeBlpTracker.address,
            feeBlpTracker.abi,
            "initialize",
            [blp.address],
            feeBlpDistributor.address,
            sender=bfr_admin,
        )
        transact(
            feeBlpDistributor.address,
            feeBlpDistributor.abi,
            "updateLastDistributionTime",
            sender=bfr_admin,
        )

    if stakedBlpTracker:
        stakedBlpTracker = RewardTracker.at(stakedBlpTracker)
        stakedBlpDistributor = RewardDistributor.at(stakedBlpDistributor)
    else:
        stakedBlpTracker = deploy_contract(
            bfr_admin, network, RewardTracker, ["Fee + Staked BLP", "fsBLP"]
        )
        stakedBlpDistributor = deploy_contract(
            bfr_admin,
            network,
            RewardDistributor,
            [esBfr.address, stakedBlpTracker.address],
        )
        transact(
            stakedBlpTracker.address,
            stakedBlpTracker.abi,
            "initialize",
            [feeBlpTracker.address],
            stakedBlpDistributor.address,
            sender=bfr_admin,
        )
        transact(
            stakedBlpDistributor.address,
            stakedBlpDistributor.abi,
            "updateLastDistributionTime",
            sender=bfr_admin,
        )

    if bfrVester:
        bfrVester = Vester.at(bfrVester)
    else:
        bfrVester = deploy_contract(
            bfr_admin,
            network,
            Vester,
            [
                "Vested BFR",  # _name
                "vBFR",  # _symbol
                vestingDuration,  # _vestingDuration
                esBfr.address,  # _esToken
                feeBfrTracker.address,  # _pairToken
                bfr.address,  # _claimableToken
                stakedBfrTracker.address,  # _rewardTracker
            ],
        )

    if blpVester:
        blpVester = Vester.at(blpVester)
    else:
        blpVester = deploy_contract(
            bfr_admin,
            network,
            Vester,
            [
                "Vested BLP",  # _name
                "vBLP",  # _symbol
                vestingDuration,  # _vestingDuration
                esBfr.address,  # _esToken
                stakedBlpTracker.address,  # _pairToken
                bfr.address,  # _claimableToken
                stakedBlpTracker.address,  # _rewardTracker
            ],
        )

    if rewardRouter:
        rewardRouter = RewardRouterV2.at(rewardRouter)
    else:
        rewardRouter = deploy_contract(bfr_admin, network, RewardRouterV2, [])

    contracts_json = {
        "RewardRouter": rewardRouter.address,
        "BLP": blp.address,
        "iBFR": bfr.address,
        "ES_BFR": esBfr.address,
        "BN_BFR": bnBfr.address,
        "USDC": usdc_address,
        "StakedBfrTracker": stakedBfrTracker.address,
        "BonusBfrTracker": bonusBfrTracker.address,
        "FeeBfrTracker": feeBfrTracker.address,
        "StakedBlpTracker": stakedBlpTracker.address,
        "FeeBlpTracker": feeBlpTracker.address,
        "BfrVester": bfrVester.address,
        "BlpVester": blpVester.address,
        "StakedBfrDistributor": stakedBfrDistributor.address,
        "StakedBlpDistributor": stakedBlpDistributor.address,
    }

    print(f"{Fore.GREEN}Deployed all contracts...{Style.RESET_ALL}")

    print(contracts_json)

    print(f"{Fore.GREEN}Initializing contracts..{Style.RESET_ALL}")

    transact(
        rewardRouter.address,
        rewardRouter.abi,
        "initialize",
        usdc_address,
        bfr.address,
        esBfr.address,
        bnBfr.address,
        blp.address,
        stakedBfrTracker.address,
        bonusBfrTracker.address,
        feeBfrTracker.address,
        feeBlpTracker.address,
        stakedBlpTracker.address,
        bfrVester.address,
        blpVester.address,
        sender=bfr_admin,
    )

    print(f"{Fore.GREEN}Setting private modes..{Style.RESET_ALL}")

    if redeployedBFR:
        transact(
            stakedBfrTracker.address,
            stakedBfrTracker.abi,
            "setInPrivateTransferMode",
            True,
            sender=bfr_admin,
        )
        transact(
            stakedBfrTracker.address,
            stakedBfrTracker.abi,
            "setInPrivateStakingMode",
            True,
            sender=bfr_admin,
        )
        transact(
            bonusBfrTracker.address,
            bonusBfrTracker.abi,
            "setInPrivateTransferMode",
            True,
            sender=bfr_admin,
        )
        transact(
            bonusBfrTracker.address,
            bonusBfrTracker.abi,
            "setInPrivateStakingMode",
            True,
            sender=bfr_admin,
        )
        transact(
            bonusBfrTracker.address,
            bonusBfrTracker.abi,
            "setInPrivateClaimingMode",
            True,
            sender=bfr_admin,
        )
        transact(
            feeBfrTracker.address,
            feeBfrTracker.abi,
            "setInPrivateTransferMode",
            True,
            sender=bfr_admin,
        )
        transact(
            feeBfrTracker.address,
            feeBfrTracker.abi,
            "setInPrivateStakingMode",
            True,
            sender=bfr_admin,
        )
        transact(
            esBfr.address,
            esBfr.abi,
            "setInPrivateTransferMode",
            True,
            sender=bfr_admin,
        )

    if redeployedBLP:
        transact(
            feeBlpTracker.address,
            feeBlpTracker.abi,
            "setInPrivateTransferMode",
            True,
            sender=bfr_admin,
        )
        transact(
            feeBlpTracker.address,
            feeBlpTracker.abi,
            "setInPrivateStakingMode",
            True,
            sender=bfr_admin,
        )
        transact(
            stakedBlpTracker.address,
            stakedBlpTracker.abi,
            "setInPrivateTransferMode",
            True,
            sender=bfr_admin,
        )
        transact(
            stakedBlpTracker.address,
            stakedBlpTracker.abi,
            "setInPrivateStakingMode",
            True,
            sender=bfr_admin,
        )

    print(f"{Fore.GREEN}Setting handlers..{Style.RESET_ALL}")

    if redeployedBFR:
        # allow bonusBfrTracker to stake stakedBfrTracker
        transact(
            stakedBfrTracker.address,
            stakedBfrTracker.abi,
            "setHandler",
            bonusBfrTracker.address,
            True,
            sender=bfr_admin,
        )

        # allow feeBfrTracker to stake bonusBfrTracker
        transact(
            bonusBfrTracker.address,
            bonusBfrTracker.abi,
            "setHandler",
            feeBfrTracker.address,
            True,
            sender=bfr_admin,
        )
        # allow feeBfrTracker to stake bnBfr
        transact(
            bnBfr.address,
            bnBfr.abi,
            "setHandler",
            feeBfrTracker.address,
            True,
            sender=bfr_admin,
        )
    if redeployedBLP:

        # allow stakedBlpTracker to stake feeBlpTracker
        transact(
            feeBlpTracker.address,
            feeBlpTracker.abi,
            "setHandler",
            stakedBlpTracker.address,
            True,
            sender=bfr_admin,
        )
        # allow feeBlpTracker to stake BLP
        transact(
            blp.address,
            blp.abi,
            "setHandler",
            feeBlpTracker.address,
            True,
            sender=bfr_admin,
        )
    print(f"{Fore.GREEN}Setting tokens per interval..{Style.RESET_ALL}")

    if redeployedBLP:
        transact(
            stakedBlpDistributor.address,
            stakedBlpDistributor.abi,
            "setTokensPerInterval",
            stakedBlpDistributorTokensPerInterval,
            sender=bfr_admin,
        )
        transact(
            feeBlpDistributor.address,
            feeBlpDistributor.abi,
            "setTokensPerInterval",
            feeBlpDistributorTokensPerInterval,
            sender=bfr_admin,
        )

    print(f"{Fore.GREEN}Funding distributors with rewards..{Style.RESET_ALL}")

    #  mint esBfr for distributors
    transact(
        esBfr.address,
        esBfr.abi,
        "mint",
        stakedBlpDistributor.address,
        stakedBlpDistributorRewards,
        sender=esbfr_minter,
    )
    print(f"{Fore.GREEN}Setting governance...{Style.RESET_ALL}")

    transact(
        feeBlpTracker.address,
        feeBlpTracker.abi,
        "setGov",
        governor.address,
        sender=bfr_admin,
    )
    transact(
        stakedBlpTracker.address,
        stakedBlpTracker.abi,
        "setGov",
        governor.address,
        sender=bfr_admin,
    )
    transact(
        stakedBlpDistributor.address,
        stakedBlpDistributor.abi,
        "setGov",
        governor.address,
        sender=bfr_admin,
    )
    transact(
        blpVester.address,
        blpVester.abi,
        "setGov",
        governor.address,
        sender=bfr_admin,
    )
    print(f"{Fore.GREEN}Setting handlers for router and esbfr..{Style.RESET_ALL}")

    transact(
        esBfr.address,
        esBfr.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=bfr_admin,
    )
    transact(
        esBfr.address,
        esBfr.abi,
        "setHandler",
        stakedBlpDistributor.address,
        True,
        sender=bfr_admin,
    )
    transact(
        esBfr.address,
        esBfr.abi,
        "setHandler",
        stakedBlpTracker.address,
        True,
        sender=bfr_admin,
    )
    transact(
        esBfr.address,
        esBfr.abi,
        "setHandler",
        blpVester.address,
        True,
        sender=bfr_admin,
    )

    transact(
        stakedBfrTracker.address,
        stakedBfrTracker.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        bonusBfrTracker.address,
        bonusBfrTracker.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        feeBfrTracker.address,
        feeBfrTracker.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        feeBlpTracker.address,
        feeBlpTracker.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        stakedBlpTracker.address,
        stakedBlpTracker.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        esBfr.address,
        esBfr.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )

    transact(
        bnBfr.address,
        bnBfr.abi,
        "setMinter",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        esBfr.address,
        esBfr.abi,
        "setMinter",
        blpVester.address,
        True,
        sender=governor,
    )

    transact(
        bfrVester.address,
        bfrVester.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
    transact(
        blpVester.address,
        blpVester.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )

    transact(
        stakedBlpTracker.address,
        stakedBlpTracker.abi,
        "setHandler",
        blpVester.address,
        True,
        sender=governor,
    )
    transact(
        blp.address,
        blp.abi,
        "setHandler",
        rewardRouter.address,
        True,
        sender=governor,
    )
