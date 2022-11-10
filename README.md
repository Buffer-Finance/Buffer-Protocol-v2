## Documentation

Refer to this [link](https://docs.google.com/document/d/1mgnjQ1n5nbKeSUjqY5av2akqBq_hmQrVAZeD4Gh5Cao/edit)

## Solidity Metrics

![Metrics](https://github.com/bufferfinance/Buffer-Protocol-v2/blob/master/metrics.png?raw=true)

## Installation

[Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html), if you haven't already.

## Compiling

To build and compile:

```bash
brownie compile
```

## Testing

To run the tests:

```bash
brownie test
```

## Coverage

To get the coverage:

```bash
brownie test -n auto --coverage
```

While checking the coverage please note the following things:

-   The following contracts are out of the scope so their coverage shouldn't be considered
    -   TraderNFT
    -   USDC
    -   BFR
-   All the custom functions written by Buffer Finance have coverage above 90%. However, since our contracts use Openzepplin and our test cases haven't covered its functions _(marked in >>)_, the resulting coverage across the project is low.

```bash
  contract: BufferBinaryOptions - 64.7%
    AccessControl._checkRole - 100.0%
    BufferBinaryOptions._getMaxUtilization - 100.0%
    BufferBinaryOptions._getbaseSettlementFeePercentage - 100.0%
    BufferBinaryOptions.checkParams - 100.0%
    BufferBinaryOptions.initialize - 100.0%
    BufferBinaryOptions.min - 100.0%
    BufferBinaryOptions.runInitialChecks - 100.0%
    ERC721.ownerOf - 100.0%
    BufferBinaryOptions.unlock - 96.4%
    BufferBinaryOptions._getSettlementFeeDiscount - 93.8%
    BufferBinaryOptions._processReferralRebate - 93.8%
    BufferBinaryOptions.isInCreationWindow - 92.5%
    >> AccessControl._grantRole - 75.0%
    >> ERC721._mint - 75.0%
    >> AccessControl._revokeRole - 0.0%
    >> AccessControl.renounceRole - 0.0%
    >> ERC721._isApprovedOrOwner - 0.0%
    >> ERC721._safeTransfer - 0.0%
    >> ERC721._transfer - 0.0%
    >> ERC721.approve - 0.0%
    >> ERC721.balanceOf - 0.0%
    >> ERC721.getApproved - 0.0%
    >> ERC721.safeTransferFrom - 0.0%
    >> ERC721.setApprovalForAll - 0.0%
    >> ERC721.tokenURI - 0.0%
    >> ERC721.transferFrom - 0.0%

  contract: BufferBinaryPool - 83.9%
    AccessControl._checkRole - 100.0%
    BufferBinaryPool._beforeTokenTransfer - 100.0%
    BufferBinaryPool._getUnlockedLiquidity - 100.0%
    BufferBinaryPool._unlock - 100.0%
    BufferBinaryPool._validateHandler - 100.0%
    BufferBinaryPool.shareOf - 100.0%
    BufferBinaryPool.send - 95.0%
    BufferBinaryPool._provide - 91.7%
    BufferBinaryPool._withdraw - 91.7%
    BufferBinaryPool.lock - 91.7%
    BufferBinaryPool.transferFrom - 91.7%
    >> AccessControl._grantRole - 75.0%
    >> AccessControl._revokeRole - 75.0%
    >> ERC20._approve - 75.0%
    >> ERC20._burn - 75.0%
    >> ERC20._mint - 75.0%
    >> ERC20._transfer - 75.0%
    >> BufferBinaryPool.divCeil - 50.0%
    >> AccessControl.renounceRole - 0.0%
    >> ERC20.decreaseAllowance - 0.0%

  contract: KeeperPayment - 19.4%
    >> AccessControl._grantRole - 75.0%
    >> AccessControl._checkRole - 25.0%
    >> AccessControl._revokeRole - 0.0%
    >> AccessControl.renounceRole - 0.0%
    >> Ownable.transferOwnership - 0.0%

  contract: BufferRouter - 69.6%
    BufferRouter._openQueuedTrade - 100.0%
    BufferRouter._validateContract - 100.0%
    BufferRouter._validateKeeper - 100.0%
    BufferRouter.cancelQueuedTrade - 100.0%
    BufferRouter.resolveQueuedTrades - 100.0%
    BufferRouter.unlockOptions - 100.0%
    >> AccessControl._checkRole - 100.0%
    >> AccessControl._grantRole - 75.0%
    >> ECDSA.tryRecover - 37.5%
    >> ECDSA._throwError - 5.0%
    >> AccessControl._revokeRole - 0.0%
    >> AccessControl.renounceRole - 0.0%

  contract: OptionsConfig - 91.7%
    OptionsConfig.setAssetUtilizationLimit - 100.0%
    OptionsConfig.setMaxPeriod - 100.0%
    OptionsConfig.setOverallPoolUtilizationLimit - 100.0%
    OptionsConfig.setStakingFeePercentages - 100.0%
    Ownable.transferOwnership - 100.0%

  contract: ReferralStorage - 69.3%
    ReferralStorage.getTraderReferralInfo - 100.0%
    ReferralStorage.registerCode - 100.0%
    ReferralStorage.setCodeOwner - 100.0%
    ReferralStorage.setUserReferralData - 100.0%
    >> AccessControl._grantRole - 75.0%
    >> AccessControl._checkRole - 25.0%
    >> AccessControl._revokeRole - 0.0%
    >> AccessControl.renounceRole - 0.0%

```
