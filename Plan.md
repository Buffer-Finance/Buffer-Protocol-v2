## Nervos API integration


## NFT Feature


## BNB Pool and Fee ==> Any asset is allowed


## BUSD Pool and Fee ==> Any asset is allowed

Make a factory contract which deploys all these contracts
- Later this contract can be expanded to deploy various configurations of these option contracts 

Create will take amount in BUSD
the fee will be calculated in BUSD
the Pool will receive the amount in BUSD
the stakingPool will receive amount in BUSD ==> This will need to be BNB

On exercise the user will get the BUSD

<!-- ## BUSD Pool and ERC20 Fee
Create will take amount in X ==> convert it for BUSD 
the fee will be calculated in BUSD
the Pool will receive the amount in BUSD
the stakingPool will receive amount in BUSD ==> This will need to be BNB

On exercise the user will get the BUSD -->

## ERC20 Pool and ERC20 Fee ==> Asset will also that same ERC20 
Create will take amount in X
the fee will be calculated in X
the Pool will receive the amount in X
the stakingPool will receive amount in X ==> This will need to be BNB

On exercise the user will get the X

### Modification
- Use the new Black Sholes -- 2 days
- Add a performance fee on the Liquidity Pool
- Weekly options clearing out
    - In a period from day 1 to day 7 when a user buys an option on day x they get the expiry as day 7
    - Strike is also fixed
    - Fixing the strike, expiry for options
