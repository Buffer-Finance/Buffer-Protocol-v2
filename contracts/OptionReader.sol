pragma solidity 0.8.4;

// SPDX-License-Identifier: BUSL-1.1

import "./interfaces/Interfaces.sol";

contract OptionReader {
    ILiquidityPool public pool;

    constructor(ILiquidityPool _pool) {
        pool = _pool;
    }

    function calculateMaxAmount(
        address optionsContract,
        uint256 traderNFTId,
        string calldata referralCode,
        address user
    )
        external
        view
        returns (uint256 maxFeeForIsAbove, uint256 maxFeeForIsBelow)
    {
        IBufferBinaryOptions options = IBufferBinaryOptions(optionsContract);
        IOptionsConfig config = IOptionsConfig(options.config());

        // Calculate the max fee due to the max txn limit
        uint256 maxPerTxnFee = ((pool.availableBalance() *
            config.optionFeePerTxnLimitPercent()) / 100e2);

        // Calculate the max fee based on pool's utilization
        (
            uint256 maxPoolBasedFeeForAbove,
            uint256 maxPoolBasedFeeForIsBelow
        ) = getPoolBasedMaxAmount(
                optionsContract,
                traderNFTId,
                referralCode,
                user
            );
        maxFeeForIsAbove = min(maxPoolBasedFeeForAbove, maxPerTxnFee);
        maxFeeForIsBelow = min(maxPoolBasedFeeForIsBelow, maxPerTxnFee);
    }

    function getPoolBasedMaxAmount(
        address optionsContract,
        uint256 traderNFTId,
        string calldata referralCode,
        address user
    )
        public
        view
        returns (
            uint256 maxPoolBasedFeeForAbove,
            uint256 maxPoolBasedFeeForIsBelow
        )
    {
        IBufferBinaryOptions options = IBufferBinaryOptions(optionsContract);

        uint256 maxAmount;
        try options.getMaxUtilization() returns (uint256 _maxAmount) {
            maxAmount = _maxAmount;
        } catch Error(string memory) {
            return (0, 0);
        }

        (maxPoolBasedFeeForAbove, , ) = options.fees(
            maxAmount,
            user,
            true,
            referralCode,
            traderNFTId
        );
        (maxPoolBasedFeeForIsBelow, , ) = options.fees(
            maxAmount,
            user,
            false,
            referralCode,
            traderNFTId
        );
    }

    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}
