from time import sleep

from brownie import accounts, network, web3
from colorama import Fore, Style
from web3 import Web3


def save_flat(container, name):
    code = container.get_verification_info()["flattened_source"]
    filename = f"flat_files/{name}Flat.sol"
    with open(filename, "w") as outfile:
        outfile.write(code)


def deploy_contract(_from, network, contract, args):

    deployed_contract = None
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            # Attempt to execute the transaction
            deployed_contract = _from.deploy(
                contract,
                *args,
                allow_revert=True,
                publish_source=True,
                gas_limit=1000000000,
            )
        except Exception as e:
            # If the transaction fails, wait for a short delay before retrying
            print(e)
            sleep(delay)
            attempts += 1
        else:
            # If the transaction succeeds, return the result
            return deployed_contract

    # If the transaction has failed after the maximum number of attempts, raise an error
    raise Exception("Transaction failed after {} attempts".format(max_attempts))


def transact(
    contract_address, abi, method, *args, sender, gas=None, gas_price=None, value=None
):
    """
    This is a wrapper function to send transactions to a contract.

    Parameters:
    contract (Contract): The contract to send the transaction to.
    function (str): The name of the function to be called.
    *args (args): The arguments for the function.
    gas (int): Gas limit for the transaction.
    gas_price (int): Gas price for the transaction.
    value (int): Value to be sent with the transaction.

    Returns:
    tx_hash (str): The transaction hash associated with the transaction.
    """
    contract = web3.eth.contract(abi=abi, address=contract_address)
    attempts = 0
    max_attempts = 5
    delay = 2
    while attempts < max_attempts:
        try:
            tx = getattr(contract.functions, method)(*args)
            tx = tx.buildTransaction(
                {
                    "from": sender.address,
                    "gasPrice": int(0.1e9),
                    "nonce": web3.eth.getTransactionCount(sender.address),
                }
            )

            signed_txn = web3.eth.account.sign_transaction(
                tx, private_key=sender.private_key
            )
            web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            # If the transaction fails, wait for a short delay before retrying
            print(e)
            sleep(delay)
            attempts += 1
        else:
            txn_hash = web3.toHex(Web3.keccak(signed_txn.rawTransaction))
            print(
                f"{Fore.BLUE} {method.capitalize()} transaction sent at {Style.RESET_ALL}",
                txn_hash,
            )

            return txn_hash

    raise Exception("Transaction failed after {} attempts".format(max_attempts))
