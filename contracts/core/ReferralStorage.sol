// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../interfaces/Interfaces.sol";

contract ReferralStorage is IReferralStorage, AccessControl {
    mapping(address => uint8) public override referrerTier; // link between user <> tier
    mapping(uint8 => Tier) public tiers;
    mapping(uint8 => uint8) public override referrerTierStep;
    mapping(uint8 => uint32) public override referrerTierDiscount;
    mapping(string => address) public override codeOwner;
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

    function configure(
        uint8[3] calldata _referrerTierStep,
        uint32[3] calldata _referrerTierDiscount // Factor of 1e5
    ) external {
        for (uint8 i = 0; i < 3; i++) {
            referrerTierStep[i] = _referrerTierStep[i];
        }

        for (uint8 i = 0; i < 3; i++) {
            referrerTierDiscount[i] = _referrerTierDiscount[i];
        }
    }

    /**
     * @notice Call this to set referrer's tier
     */
    function setReferrerTier(address _referrer, uint8 tier)
        external
        override
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        referrerTier[_referrer] = tier;
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
            codeOwner[_code] == address(0),
            "ReferralStorage: code already exists"
        );

        codeOwner[_code] = msg.sender;
        userCode[msg.sender] = _code;
        emit RegisterCode(msg.sender, _code);
    }

    function setCodeOwner(string memory _code, address _newUser) external {
        require(bytes(_code).length != 0, "ReferralStorage: invalid _code");

        require(msg.sender == codeOwner[_code], "ReferralStorage: forbidden");

        codeOwner[_code] = _newUser;
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
            referrer = codeOwner[code];
        }
    }

    function _setTraderReferralCode(address user, string memory _code) private {
        traderReferralCodes[user] = _code;
        emit UpdateTraderReferralCode(user, _code);
    }
}
