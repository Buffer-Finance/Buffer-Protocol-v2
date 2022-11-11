def save_flat(container, name):
    code = container.get_verification_info()["flattened_source"]
    filename = f"flat_files/{name}Flat.sol"
    with open(filename, "w") as outfile:
        outfile.write(code)


def deploy_contract(_from, network, contract, args):
    publish_source = False
    deployed_contract = None

    deployed_contract = _from.deploy(
        contract,
        *args,
        allow_revert=True,
        publish_source=publish_source,
        gas_limit=10000000,
    )

    return deployed_contract
