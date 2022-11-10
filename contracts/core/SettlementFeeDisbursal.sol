// SPDX-License-Identifier: BUSL-1.1

pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../interfaces/Interfaces.sol";

/**
 * @author Heisenberg
 * @title Settlement Fee Disbursal Contract (SFD)
 * @notice Distributes settlement fees to the registered addresses
 */
contract SettlementFeeDisbursal {
    ERC20 public tokenX;
    IOptionsConfig public config;
    IBufferBinaryOptions public optionsContract;
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
        IOptionsConfig _config,
        IBufferBinaryOptions _optionsContract,
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
                config.treasuryPercentage()) / 1e4;
            uint256 blpStakingAmount = (stakingAmount *
                config.blpStakingPercentage()) / 1e4;
            uint256 bfrStakingAmount = (stakingAmount *
                config.bfrStakingPercentage()) / 1e4;
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
