// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../interfaces/Interfaces.sol";

contract ReferralStorage is IReferralStorage, AccessControl {
    struct Tier {
        uint256 totalRebate; // e.g. 2400 for 24%
        uint256 discountShare; // 5000 for 50%/50%, 7000 for 30% rebates/70% discount
    }

    uint256 public constant BASIS_POINTS = 10000;

    mapping(address => uint8) public override referrerTiers; // link between user <> tier
    mapping(uint8 => Tier) public tiers;
    mapping(uint8 => uint8) public override referrerTierToStep;
    mapping(uint8 => uint256) public override referrerTierToDiscount;
    mapping(address => uint8) public referrerToTier;
    mapping(string => address) public override codeOwners;
    mapping(address => string) public userCode;
    mapping(address => string) public override traderReferralCodes;
    bytes32 public constant OPTION_ISSUER_ROLE =
        keccak256("OPTION_ISSUER_ROLE");

    event UpdateTraderReferralCode(address account, string code);
    event UpdateReferrerTier(address referrer, uint8 tierId);
    event RegisterCode(address account, string code);
    event SetCodeOwner(address account, address newAccount, string code);
    mapping(address => ReferralData) public UserReferralData;

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function initialize() external {
        referrerTierToStep[0] = 1;
        referrerTierToStep[1] = 2;
        referrerTierToStep[2] = 3;
        referrerTierToDiscount[0] = 25000; // 0.25%
        referrerTierToDiscount[1] = 50000; // 0.50%
        referrerTierToDiscount[2] = 75000; // 0.75%
    }

    /**
     * @notice Call this to set referrer's tier
     */
    function setReferrerTier(address _referrer, uint8 tier)
        external
        override
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        referrerTiers[_referrer] = tier;
        emit UpdateReferrerTier(_referrer, tier);
    }

    function setUserReferralData(
        address user,
        uint256 totalFee,
        uint256 rebate,
        string memory referralCode
    ) external override onlyRole(OPTION_ISSUER_ROLE) {
        if (bytes(traderReferralCodes[user]).length == 0) {
            _setTraderReferralCode(user, referralCode);
        }

        ReferralData storage userReferralData = UserReferralData[user];
        userReferralData.referreeData.tradeVolume += totalFee;
        userReferralData.referreeData.rebate += rebate;
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

    function setTraderReferralCode(address user, string memory _code)
        external
        override
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        _setTraderReferralCode(user, _code);
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

    function setCodeOwner(string memory _code, address _newUser) external {
        require(bytes(_code).length != 0, "ReferralStorage: invalid _code");

        require(msg.sender == codeOwners[_code], "ReferralStorage: forbidden");

        codeOwners[_code] = _newUser;
        emit SetCodeOwner(msg.sender, _newUser, _code);
    }

    function getTraderReferralInfo(address user)
        external
        view
        override
        returns (string memory code, address referrer)
    {
        code = traderReferralCodes[user];
        if (bytes(code).length != 0) {
            referrer = codeOwners[code];
        }
    }

    function _setTraderReferralCode(address user, string memory _code) private {
        traderReferralCodes[user] = _code;
        emit UpdateTraderReferralCode(user, _code);
    }
}
