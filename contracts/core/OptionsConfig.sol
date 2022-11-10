pragma solidity 0.8.4;

// SPDX-License-Identifier: BUSL-1.1

import "./BufferBinaryPool.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @author Heisenberg
 * @title Buffer Options Config
 * @notice Maintains all the configurations for the options contracts
 */
contract OptionsConfig is Ownable, IOptionsConfig {
    BufferBinaryPool public pool;

    address public override settlementFeeDisbursalContract;
    address public override traderNFTContract;
    uint16 public override assetUtilizationLimit = 10e2;
    uint16 public override overallPoolUtilizationLimit = 64e2;
    uint32 public override maxPeriod = 24 hours;
    uint16 public override optionFeePerTxnLimitPercent = 5e2;
    uint16 public override minFee = 1;

    mapping(uint16 => Window) public override marketTimes;

    constructor(BufferBinaryPool _pool) {
        pool = _pool;
    }

    function settraderNFTContract(address value) external onlyOwner {
        traderNFTContract = value;
        emit UpdatetraderNFTContract(value);
    }

    function setMinFee(uint16 value) external onlyOwner {
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

    function setOptionFeePerTxnLimitPercent(uint16 value) external onlyOwner {
        optionFeePerTxnLimitPercent = value;
        emit UpdateOptionFeePerTxnLimitPercent(value);
    }

    function setOverallPoolUtilizationLimit(uint16 value) external onlyOwner {
        require(value <= 100e2, "Utilization value too high");
        overallPoolUtilizationLimit = value;
        emit UpdateOverallPoolUtilizationLimit(value);
    }

    function setAssetUtilizationLimit(uint16 value) external onlyOwner {
        require(value <= 100e2, "Utilization value too high");
        assetUtilizationLimit = value;
        emit UpdateAssetUtilizationLimit(value);
    }

    function setMaxPeriod(uint32 value) external onlyOwner {
        require(
            value >= 5 minutes,
            "MaxPeriod needs to be greater than 5 minutes"
        );
        maxPeriod = value;
        emit UpdateMaxPeriod(value);
    }

    function setMarketTime(Window[] memory windows) external onlyOwner {
        for (uint16 index = 0; index < windows.length; index++) {
            marketTimes[index] = windows[index];
        }
        emit UpdateMarketTime();
    }
}
