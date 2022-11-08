pragma solidity 0.8.4;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

interface IKeeperPayment {
    function distributeForOpen(
        uint256 queueId,
        uint256 size,
        address keeper
    ) external;

    function distributeForClose(
        uint256 optionId,
        uint256 size,
        address keeper
    ) external;

    event DistriuteRewardForOpen(uint256 queueId, uint256 size, address keeper);
    event DistriuteRewardForClose(
        uint256 optionId,
        uint256 size,
        address keeper
    );
    event UpdateOpenRewardPercent(uint256 value);
    event UpdateReward(uint256 value);
}

interface IOptionRouter {
    struct QueuedTrade {
        uint256 queueId;
        uint256 userQueueIndex;
        address user;
        uint256 totalFee;
        uint256 period;
        bool isAbove;
        address targetContract;
        uint256 expectedStrike;
        uint256 slippage;
        bool allowPartialFill;
        uint256 queuedTime;
        uint256 cancellationTime;
        bool isQueued;
        string referralCode;
    }
    struct Trade {
        uint256 queueId;
        uint256 price;
    }
    struct OpenTradeParams {
        uint256 queueId;
        uint256 timestamp;
        address asset;
        uint256 price;
        bytes signature;
    }
    struct CloseTradeParams {
        uint256 optionId;
        uint256 expiryTimestamp;
        address asset;
        uint256 priceAtExpiry;
        bytes signature;
    }
    event OpenTrade(uint256 queueId, address user);
    event CancelTrade(uint256 queueId, address user, string reason);
    event FailUnlock(uint256 optionId, string reason);
    event FailResolve(uint256 queueId, string reason);
    event InitiateTrade(uint256 queueId, address user, uint256 queuedTime);
}

interface IBufferBinaryOptions {
    event Create(
        uint256 indexed id,
        address indexed account,
        uint256 settlementFee,
        uint256 totalFee
    );

    event Exercise(
        uint256 indexed id,
        uint256 profit,
        uint256 priceAtExpiration
    );
    event Expire(
        uint256 indexed id,
        uint256 premium,
        uint256 priceAtExpiration
    );
    event Pause(bool isPaused);

    function createFromRouter(
        address user,
        uint256 totalFee,
        uint256 period,
        bool isAbove,
        uint256 strike,
        uint256 amount,
        string memory referralCode
    ) external returns (uint256 optionID);

    function checkParams(
        uint256 totalFee,
        bool allowPartialFill,
        string memory referralCode,
        address user,
        uint256 period,
        bool isAbove
    ) external returns (uint256 amount, uint256 revisedFee);

    function runInitialChecks(
        uint256 slippage,
        uint256 period,
        uint256 totalFee
    ) external view;

    function isStrikeValid(
        uint256 slippage,
        uint256 strike,
        uint256 expectedStrike
    ) external view returns (bool);

    function tokenX() external view returns (ERC20);

    enum State {
        Inactive,
        Active,
        Exercised,
        Expired
    }

    enum AssetCategory {
        Forex,
        Crypto,
        Commodities
    }
    struct OptionExpiryData {
        uint256 optionId;
        uint256 priceAtExpiration;
    }

    struct Option {
        State state;
        uint256 strike;
        uint256 amount;
        uint256 lockedAmount;
        uint256 premium;
        uint256 expiration;
        bool isAbove;
        uint256 totalFee;
        uint256 createdAt;
    }

    function options(uint256 optionId)
        external
        view
        returns (
            State state,
            uint256 strike,
            uint256 amount,
            uint256 lockedAmount,
            uint256 premium,
            uint256 expiration,
            bool isAbove,
            uint256 totalFee,
            uint256 createdAt
        );

    function unlock(uint256 optionID, uint256 priceAtExpiration) external;
}

interface ILiquidityPool {
    struct LockedLiquidity {
        uint256 amount;
        uint256 premium;
        bool locked;
    }
    event Profit(uint256 indexed id, uint256 amount);
    event Loss(uint256 indexed id, uint256 amount);
    event Provide(address indexed account, uint256 amount, uint256 writeAmount);
    event UpdateMaxLiquidity(uint256 indexed maxLiquidity);
    event Withdraw(
        address indexed account,
        uint256 amount,
        uint256 writeAmount
    );

    function unlock(uint256 id) external;

    function totalTokenXBalance() external view returns (uint256 amount);

    function availableBalance() external view returns (uint256 balance);

    function send(
        uint256 id,
        address account,
        uint256 amount
    ) external;

    function lock(
        uint256 id,
        uint256 tokenXAmount,
        uint256 premium
    ) external;
}

interface IOptionsConfig {
    struct Window {
        uint256 startHour;
        uint256 startMinute;
        uint256 endHour;
        uint256 endMinute;
    }

    event UpdateStakingFeePercentage(
        uint256 treasuryPercentage,
        uint256 blpStakingPercentage,
        uint256 bfrStakingPercentage,
        uint256 insuranceFundPercentage
    );
    event UpdateMarketTime();
    event UpdateMaxPeriod(uint256 value);
    event UpdateOptionFeePerTxnLimitPercent(uint256 value);
    event UpdateOverallPoolUtilizationLimit(uint256 value);
    event UpdateSettlementFeeDisbursalContract(address value);
    event UpdatetraderNFTContract(address value);
    event UpdateAssetUtilizationLimit(uint256 value);
    event UpdateMinFee(uint256 value);
}

interface ISettlementFeeDisbursal {
    function distributeSettlementFee(uint256 settlementFee)
        external
        returns (uint256 stakingAmount);
}

interface ITraderNFT {
    function userToTier(address user) external view returns (uint256 tier);
}

interface IReferralStorage {
    function codeOwners(string memory _code) external view returns (address);

    function traderReferralCodes(address) external view returns (string memory);

    function getTraderReferralInfo(address _account)
        external
        view
        returns (string memory, address);

    function setTraderReferralCode(address _account, string memory _code)
        external;

    function setReferrerTier(address _referrer, uint256 _tierId) external;

    function ReferrerTierToStep(uint256 referralTier)
        external
        view
        returns (uint256 step);

    function ReferrerTierToDiscount(uint256 referralTier)
        external
        view
        returns (uint256 discount);

    function ReferrerToTier(address referrer)
        external
        view
        returns (uint256 tier);

    function setUserReferralData(
        address user,
        uint256 totalFee,
        uint256 rebate,
        string memory referralCode
    ) external;

    function setReferrerReferralData(
        address referrer,
        uint256 totalFee,
        uint256 discount
    ) external;

    struct ReferrerData {
        uint256 tradeVolume;
        uint256 rebate;
        uint256 trades;
    }

    struct ReferreeData {
        uint256 tradeVolume;
        uint256 rebate;
    }

    struct ReferralData {
        ReferrerData referrerData;
        ReferreeData referreeData;
    }
}
