// SPDX-License-Identifier: BUSL-1.1

pragma solidity ^0.8.4;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "../Interfaces/InterfacesBinary.sol";

/**
 * @author Heisenberg
 * @title Buffer Keeper Payment
 * @notice Rewards the keepers for opening or closing the options.
 */
contract KeeperPayment is Ownable, IKeeperPayment, AccessControl {
    ERC20 public rewardToken;
    uint256 public openRewardPercent = 50e2;
    uint256 public reward = 1;
    bytes32 public constant ROUTER_ROLE = keccak256("ROUTER_ROLE");

    constructor(ERC20 _rewardToken) {
        rewardToken = _rewardToken;
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    /**
     * @notice Used for adjusting the reward percent for opening the trade
     */
    function setOpenRewardPercent(uint256 value) external onlyOwner {
        openRewardPercent = value;
        emit UpdateOpenRewardPercent(value);
    }

    /**
     * @notice Used for adjusting the reward
     */
    function setReward(uint256 value) external onlyOwner {
        reward = value;
        emit UpdateReward(value);
    }

    /**
     * @notice Sends reward token to the caller for opening a trade
     */
    function distributeForOpen(
        uint256 queueId,
        uint256 size,
        address keeper
    ) external override onlyRole(ROUTER_ROLE) {
        uint256 openReward = (reward *
            (10**rewardToken.decimals()) *
            openRewardPercent) / 1e4;
        rewardToken.transfer(keeper, openReward);
        emit DistriuteRewardForOpen(queueId, size, keeper);
    }

    /**
     * @notice Sends reward token to the caller for closing a trade
     */
    function distributeForClose(
        uint256 optionId,
        uint256 size,
        address keeper
    ) external override onlyRole(ROUTER_ROLE) {
        uint256 closeReward = (reward *
            (10**rewardToken.decimals()) *
            (100e2 - openRewardPercent)) / 1e4;
        rewardToken.transfer(keeper, closeReward);
        emit DistriuteRewardForClose(optionId, size, keeper);
    }

    /**
     * @notice Emergency withdraw in case wrong number of reward tokens are sent to the contract
     */
    function withdraw() external onlyOwner {
        rewardToken.transfer(owner(), rewardToken.balanceOf(address(this)));
    }
}
