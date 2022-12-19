from time import sleep

from brownie import accounts, network, web3
from colorama import Fore, Style
from web3 import Web3

BOLD = "\033[1m"


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
                publish_source=False,
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

    contract = web3.eth.contract(abi=abi, address=contract_address)
    attempts = 0
    max_attempts = 10
    delay = 2
    gasPrice = int(0.1e9)
    while attempts < max_attempts:
        try:
            nonce = web3.eth.getTransactionCount(sender.address)
            tx = getattr(contract.functions, method)(*args)
            tx = tx.buildTransaction(
                {
                    "from": sender.address,
                    "gasPrice": gasPrice,
                    "nonce": nonce,
                }
            )

            signed_txn = web3.eth.account.sign_transaction(
                tx, private_key=sender.private_key
            )
            tx = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            # If the transaction fails, wait for a short delay before retrying
            print(f"{Fore.RED}{e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Retry attempt {attempts}...{Style.RESET_ALL}")
            sleep(delay)
            attempts += 1
        else:
            txn_hash = web3.toHex(Web3.keccak(signed_txn.rawTransaction))
            web3.eth.wait_for_transaction_receipt(txn_hash)
            receipt = web3.eth.get_transaction_receipt(txn_hash)
            print(
                f"Transaction sent: {Fore.BLUE}{BOLD}{txn_hash}{Style.RESET_ALL}",
            )
            print(
                f"  Gas price: {Fore.BLUE}{BOLD}{gasPrice/1e9}{Style.RESET_ALL} gwei  Nonce: {Fore.BLUE}{BOLD}{nonce}{Style.RESET_ALL}"
            )
            print(
                f"  {method} confirmed   Block: {Fore.BLUE}{BOLD}{receipt.blockNumber}{Style.RESET_ALL}   Gas used: {Fore.BLUE}{BOLD}{receipt.gasUsed}{Style.RESET_ALL}"
            )
            print(" ")
            return txn_hash

    raise Exception("Transaction failed after {} attempts".format(max_attempts))
