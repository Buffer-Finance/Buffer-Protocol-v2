// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../Interfaces/InterfacesBinary.sol";

contract ReferralStorage is IReferralStorage, AccessControl {
    struct Tier {
        uint256 totalRebate; // e.g. 2400 for 24%
        uint256 discountShare; // 5000 for 50%/50%, 7000 for 30% rebates/70% discount
    }

    uint256 public constant BASIS_POINTS = 10000;

    mapping(address => uint256) public referrerTiers; // link between user <> tier
    mapping(uint256 => Tier) public tiers;
    mapping(uint256 => uint256) public override ReferrerTierToStep;
    mapping(uint256 => uint256) public override ReferrerTierToDiscount;
    mapping(address => uint256) public override ReferrerToTier;
    mapping(string => address) public override codeOwners;
    mapping(address => string) public userCode;
    mapping(address => string) public override traderReferralCodes;
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant OPTION_ISSUER_ROLE =
        keccak256("OPTION_ISSUER_ROLE");

    event SetTraderReferralCode(address account, string code);
    event SetReferrerTier(address referrer, uint256 tierId);
    event RegisterCode(address account, string code);
    event SetCodeOwner(address account, address newAccount, string code);
    mapping(address => ReferralData) public UserReferralData;

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function initialize() external {
        ReferrerTierToStep[0] = 1;
        ReferrerTierToStep[1] = 2;
        ReferrerTierToStep[2] = 3;
        ReferrerTierToDiscount[0] = 25; // 0.25%
        ReferrerTierToDiscount[1] = 50; // 0.50%
        ReferrerTierToDiscount[2] = 75; // 0.75%
        _setupRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @notice Call this to set referrer's tier
     */
    function setReferrerToTier(address referrer, uint256 tier)
        external
        onlyRole(ADMIN_ROLE)
    {
        ReferrerToTier[referrer] = tier;
    }

    function setReferrerTier(address _referrer, uint256 _tierId)
        external
        override
        onlyRole(ADMIN_ROLE)
    {
        referrerTiers[_referrer] = _tierId;
        emit SetReferrerTier(_referrer, _tierId);
    }

    function setUserReferralData(
        address user,
        uint256 totalFee,
        uint256 rebate,
        string memory referralCode
    ) external override onlyRole(OPTION_ISSUER_ROLE) {
        if (bytes(traderReferralCodes[user]).length == 0) {
            traderReferralCodes[user] = referralCode;
        }

        ReferralData storage referralDataOfUser = UserReferralData[user];
        referralDataOfUser.referreeData.tradeVolume += totalFee;
        referralDataOfUser.referreeData.rebate += rebate;
    }

    function setReferrerReferralData(
        address referrer,
        uint256 totalFee,
        uint256 discount
    ) external override onlyRole(OPTION_ISSUER_ROLE) {
        ReferralData storage referralDataOfReferrer = UserReferralData[
            referrer
        ];
        referralDataOfReferrer.referrerData.trades += 1;
        referralDataOfReferrer.referrerData.tradeVolume += totalFee;
        referralDataOfReferrer.referrerData.rebate += discount;
    }

    function setTraderReferralCode(address _account, string memory _code)
        external
        override
        onlyRole(ADMIN_ROLE)
    {
        _setTraderReferralCode(_account, _code);
    }

    function setTraderReferralCodeByUser(string memory _code) external {
        _setTraderReferralCode(msg.sender, _code);
    }

    function registerCode(string memory _code) external {
        require(bytes(_code).length != 0, "ReferralStorage: invalid _code");
        require(
            codeOwners[_code] == address(0),
            "ReferralStorage: code already exists"
        );

        codeOwners[_code] = msg.sender;
        userCode[msg.sender] = _code;
        emit RegisterCode(msg.sender, _code);
    }

    function setCodeOwner(string memory _code, address _newAccount) external {
        require(bytes(_code).length != 0, "ReferralStorage: invalid _code");

        address account = codeOwners[_code];
        require(msg.sender == account, "ReferralStorage: forbidden");

        codeOwners[_code] = _newAccount;
        emit SetCodeOwner(msg.sender, _newAccount, _code);
    }

    function getTraderReferralInfo(address _account)
        external
        view
        override
        returns (string memory code, address referrer)
    {
        code = traderReferralCodes[_account];
        if (bytes(code).length != 0) {
            referrer = codeOwners[code];
        }
        return (code, referrer);
    }

    function _setTraderReferralCode(address _account, string memory _code)
        private
    {
        traderReferralCodes[_account] = _code;
        emit SetTraderReferralCode(_account, _code);
    }
}
