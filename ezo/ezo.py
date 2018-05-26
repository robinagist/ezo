'''
ezo - easy Ethereum oracle builder
(c) 2018 - Robin A. Gist - All Rights Reserved
This code is released under the MIT License

USE AT YOUR OWN RISK

'''
import argparse
from helpers import get_contract_path, display_deployment_rows, display_contract_rows
from utils import initialize, EZOCommandProcessor
from lib import EZO, Contract
import sys

### TODO - REFACTOR THIS ENTIRE SCRIPT after settling on MVP release functionality


def main():
    args = EZOCommandProcessor(sys.argv).args

    ### initialize a new project ###
    if args.command[0] == 'create':
        initialize()
        print("new ezo project initialized")
        exit()

    # start ezo
    ezo = EZO(args.configfile)

    # connect to mongo
    _, err = ezo.connect()
    if err:
        print("db connect error: {}".format(err))
        exit(1)

    ### compile ###
    if args.command[0] == 'compile':
        # single file in contracts directory
        print("compiling contracts")
        if args.command[1]:
            filename = get_contract_path(ezo.config, args.command[1])
            contracts_source, err = Contract.load(filename)
            if err:
                print("error loading contracts file: {}".format(err))

            contracts, err = Contract.compile(contracts_source, ezo)
            if err:
                print("error compiling contracts source: {}".format(err))

            # persist the compiled contract
            for contract in contracts:
                contract.source = contracts_source
                iid, err = contract.save()
                if err:
                    print("error while persisting Contract to datastore: {}".format(err))
                else:
                    print("id saved: {}".format(iid))

            exit(0)

        else:
            print("please supply a source file")
            exit(2)

    ### deploy ###
    if args.command[0] == "deploy":
        # stage must be set before deploying
        if not args.stage:
            print("target stage must be set with the -s option before deploying")
            exit(2)

        print("deploying contract {} to {}".format(args.command[1], args.stage))
        ezo.stage = args.stage

        _, err = ezo.dial()
        if err:
            print("dial error: {}".format(err))
            exit(1)

        # get the compiled contract proxy by it's source hash
        c, err = Contract.create_from_hash(args.command[1], ezo)
        if err:
            print("error loading contract from storage: {}".format(err))
            exit(1)

        # deploy the contract
        addr, err = c.deploy()
        if err:
            print("error deploying contract {} to {}".format(c.hash, ezo.stage))
            print("message: {}".format(err))
            exit(1)
        print("deployed contract {} named {} to stage '{}' at address {}".format(c.hash, c.name, ezo.stage, addr ))
        exit(0)

    ### view ###
    if args.command[0] == "view":
        if args.command[1] == "deploys":
            rows, err = ezo.view_deployments(args.command[2])
            if err:
                print("error: view deploys: {}".format(err))
            display_deployment_rows(rows)

        elif args.command[1] == "contracts":
            rows, err = ezo.view_contracts(args.command[2])
            if err:
                print("error: view contracts: {}".format(err))
            display_contract_rows(rows)

        elif args.command[1] == "source":
            ezo.view_source(args.command[2])
        else:
            print("view command requires more specifics.  follow command with one of <deploys|contracts|source>")
            exit(1)


    ### generate ###
    ### scaffold <filehash> - generate handler scaffolding for the compiled contract
    ### account <network> - create a new account for the target network
    if args.command[0] == "gen":

        # get the abi of the contract from it's hash
        if not len(args.command) > 1:
            print("missing hash name")
            exit(1)

        c = Contract.create_from_hash(args.command[1], ezo)[0]
        abi = c.abi
        # print(json.dumps(abi, indent=2))
        for el in abi:
            if el["type"] == "event":
                inputs = el["inputs"]
                name = inputs["name"]
                type = inputs["type"]


    ### start oracle ###
    if args.command[0] == "start":
        if not args.stage:
            print("target stage not set")
        ezo.stage = args.stage
        # pop off 'start'
        print("starting")
        args.command.pop(0)
        if not args.command:
            print("missing contract hash.")
            print("correct syntax is: start <contract_hash1>, [contract_hash2]...[contract_hash_n]")
            exit(1)

        _, err = ezo.dial()
        if err:
            print("dial error: {}".format(err))
            exit(1)

        res, err = ezo.start(args.command)
        if err:
            print("error: {}".format(err))
        else:
            print("result: {}".format(res))

main()