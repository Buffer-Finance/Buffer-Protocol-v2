// SPDX-License-Identifier: BUSL-1.1

pragma solidity 0.8.4;

import "./OptionConfigBinaryV2.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "./BufferBinaryOptions.sol";

/**
 * @author Heisenberg
 * @title Settlement Fee Disbursal Contract (SFD)
 * @notice Distributes settlement fees to the registered addresses
 */
contract SettlementFeeDisbursal {
    ERC20 public tokenX;
    OptionConfigBinaryV2 public config;
    BufferBinaryOptions public optionsContract;
    address treasury;
    address blpStaking;
    address bfrStaking;
    address insuranceFund;
    event DistributeSettlementFee(
        uint256 treasuryFee,
        uint256 blpStakingFee,
        uint256 bfrStakingFee,
        uint256 insuranceFee
    );

    constructor(
        ERC20 _tokenX,
        OptionConfigBinaryV2 _config,
        BufferBinaryOptions _optionsContract,
        address _treasury,
        address _blpStaking,
        address _bfrStaking,
        address _insuranceFund
    ) {
        tokenX = _tokenX;
        config = _config;
        optionsContract = _optionsContract;
        treasury = _treasury;
        blpStaking = _blpStaking;
        bfrStaking = _bfrStaking;
        insuranceFund = _insuranceFund;
    }

    function distributeSettlementFee(uint256 settlementFee)
        external
        returns (uint256 stakingAmount)
    {
        stakingAmount = settlementFee;

        // Incase the stakingAmount is 0
        if (stakingAmount > 0) {
            uint256 treasuryAmount = (stakingAmount *
                config.treasuryPercentage()) / 100;
            uint256 blpStakingAmount = (stakingAmount *
                config.blpStakingPercentage()) / 100;
            uint256 bfrStakingAmount = (stakingAmount *
                config.bfrStakingPercentage()) / 100;
            uint256 insuranceAmount = stakingAmount -
                treasuryAmount -
                blpStakingAmount -
                bfrStakingAmount;

            tokenX.transferFrom(
                address(optionsContract),
                address(treasury),
                treasuryAmount
            );
            tokenX.transferFrom(
                address(optionsContract),
                address(bfrStaking),
                bfrStakingAmount
            );
            tokenX.transferFrom(
                address(optionsContract),
                address(blpStaking),
                blpStakingAmount
            );
            tokenX.transferFrom(
                address(optionsContract),
                address(insuranceFund),
                insuranceAmount
            );
            emit DistributeSettlementFee(
                treasuryAmount,
                blpStakingAmount,
                bfrStakingAmount,
                insuranceAmount
            );
        }
    }
}
