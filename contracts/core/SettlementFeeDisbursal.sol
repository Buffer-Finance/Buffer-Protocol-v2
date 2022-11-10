// SPDX-License-Identifier: BUSL-1.1

pragma solidity 0.8.4;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/Interfaces.sol";

/**
 * @author Heisenberg
 * @title Settlement Fee Disbursal Contract (SFD)
 * @notice Distributes settlement fees to the registered addresses
 */
contract SettlementFeeDisbursal is Ownable, ISettlementFeeDisbursal {
    ERC20 public tokenX;
    IOptionsConfig public config;
    IBufferBinaryOptions public optionsContract;
    address treasury;
    address blpStaking;
    address bfrStaking;
    address insuranceFund;
    uint16 public treasuryPercentage = 3e2;
    uint16 public blpStakingPercentage = 65e2;
    uint16 public bfrStakingPercentage = 27e2;
    uint16 public insuranceFundPercentage = 5e2;

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

    function setStakingFeePercentages(
        uint16 _treasuryPercentage,
        uint16 _blpStakingPercentage,
        uint16 _bfrStakingPercentage,
        uint16 _insuranceFundPercentage
    ) external onlyOwner {
        require(
            _treasuryPercentage +
                _blpStakingPercentage +
                _bfrStakingPercentage +
                _insuranceFundPercentage ==
                1e4,
            "Wrong distribution"
        );
        treasuryPercentage = _treasuryPercentage;
        blpStakingPercentage = _blpStakingPercentage;
        bfrStakingPercentage = _bfrStakingPercentage;
        insuranceFundPercentage = _insuranceFundPercentage;

        emit UpdateStakingFeePercentage(
            treasuryPercentage,
            blpStakingPercentage,
            bfrStakingPercentage,
            insuranceFundPercentage
        );
    }

    function distributeSettlementFee(uint256 settlementFee)
        external
        returns (uint256 stakingAmount)
    {
        stakingAmount = settlementFee;

        // Incase the stakingAmount is 0
        if (stakingAmount > 0) {
            uint256 treasuryAmount = (stakingAmount * treasuryPercentage) / 1e4;
            uint256 blpStakingAmount = (stakingAmount * blpStakingPercentage) /
                1e4;
            uint256 bfrStakingAmount = (stakingAmount * bfrStakingPercentage) /
                1e4;
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
