## Installation

[Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html), if you haven't already.

## Compiling

To build and compile:

Replace the openzepplin path in the remappings in the [`config`](brownie-config.yaml) with your path and then run the following command

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
    -   ReferralStorage
-   All the custom functions written by Buffer Finance have a coverage above 90%. However, since our contracts use Openzepplin and our testcases haven't covered its functions, the resulting coverage across the project is low.
