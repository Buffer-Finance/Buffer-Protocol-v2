pragma solidity 0.8.4;

// SPDX-License-Identifier: BUSL-1.1

import "./BufferBinaryPool.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @author Heisenberg
 * @title Buffer Options Config
 * @notice Maintains all the configurations for the options contracts
 */
contract OptionConfigBinaryV2 is Ownable, IOptionsConfig {
    BufferBinaryPool public pool;

    address public settlementFeeDisbursalContract;
    address public traderNFTContract;
    uint256 public treasuryPercentage = 3;
    uint256 public blpStakingPercentage = 65;
    uint256 public bfrStakingPercentage = 27;
    uint256 public insuranceFundPercentage = 5;
    uint256 public assetUtilizationLimit = 10e2;
    uint256 public overallPoolUtilizationLimit = 64e2;
    uint256 public maxPeriod = 24 hours;
    uint256 public optionFeePerTxnLimitPercent = 5e2;
    uint256 public minFee = 1;

    mapping(uint256 => Window) public marketTimes;

    constructor(BufferBinaryPool _pool) {
        pool = _pool;
    }

    function settraderNFTContract(address value) external onlyOwner {
        traderNFTContract = value;
        emit UpdatetraderNFTContract(value);
    }

    function setMinFee(uint256 value) external onlyOwner {
        minFee = value;
        emit UpdateMinFee(value);
    }

    function setSettlementFeeDisbursalContract(address value)
        external
        onlyOwner
    {
        settlementFeeDisbursalContract = value;
        emit UpdateSettlementFeeDisbursalContract(value);
    }

    function setOptionFeePerTxnLimitPercent(uint256 value) external onlyOwner {
        optionFeePerTxnLimitPercent = value;
        emit UpdateOptionFeePerTxnLimitPercent(value);
    }

    function setOverallPoolUtilizationLimit(uint256 value) external onlyOwner {
        require(value <= 100e2, "Utilization value too high");
        overallPoolUtilizationLimit = value;
        emit UpdateOverallPoolUtilizationLimit(value);
    }

    function setAssetUtilizationLimit(uint256 value) external onlyOwner {
        require(value <= 100e2, "Utilization value too high");
        assetUtilizationLimit = value;
        emit UpdateAssetUtilizationLimit(value);
    }

    function setMaxPeriod(uint256 value) external onlyOwner {
        require(
            value >= 5 minutes,
            "MaxPeriod needs to be greater than 5 minutes"
        );
        maxPeriod = value;
        emit UpdateMaxPeriod(value);
    }

    function setMarketTime(Window[] memory windows) external onlyOwner {
        for (uint256 index = 0; index < windows.length; index++) {
            marketTimes[index] = windows[index];
        }
        emit UpdateMarketTime();
    }

    function setStakingFeePercentages(
        uint256 _treasuryPercentage,
        uint256 _blpStakingPercentage,
        uint256 _bfrStakingPercentage,
        uint256 _insuranceFundPercentage
    ) external onlyOwner {
        require(
            _treasuryPercentage +
                _blpStakingPercentage +
                _bfrStakingPercentage +
                _insuranceFundPercentage ==
                100,
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
}
