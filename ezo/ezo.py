'''
EZOracle
(c) 2018 - Robin A. Gist - All Rights Reserved
This code is released under the MIT License

USE AT YOUR OWN RISK

'''
import argparse
from utils import initialize, get_contract_path, get_account
from lib import EZO, Contract


# parse the command line
parser = argparse.ArgumentParser()

parser.add_argument('command', nargs='*', metavar='create|compile|deploy|gen|view|start',
                    help="use: 'create' to create initial project, "
                         "'compile' contract <--all|--file|--address>"
                         "'deploy' to compile and deploy contracts, 'start' to start")

parser.add_argument("-c", "--config",
                    metavar='<configfile>',
                    dest="configfile",
                    help="specify configuration file (defaults to config.json)", default="config.json")

parser.add_argument("-s", '--stage',
                    metavar="<stage>",
                    dest="stage",
                    help="run all actions on <STAGE> (e.g. dev, prod)")

parser.add_argument("-a", "--account",
                    metavar='<account_address>',
                    dest="account",
                    help="account address - overrides the target stage default account address")


args = parser.parse_args()

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
            '''
            ezo.stage = args.stage
            print("deploying")
            _, err = ezo.dial()
            if err:
                print("dial error: {}".format(err))
                exit(1)
            _, err = contract.deploy()
            if err:
                print("error: {}".format(err))
                exit(1)
            '''
            iid, err = contract.save()
            if err:
                print("error while persisting Contract to datastore: {}".format(err))
            else:
                print("id saved: {}".format(iid))

        exit(0)

    else:
        print("currently only supports compiling a single source file")
        exit(2)

### deploy ###
if args.command[0] == "deploy":
    # stage must be set before deploying
    if not args.stage:
        print("target stage must be set with the -s option before deploying")
        exit(2)

    print("deploying...")
    ezo.stage = args.stage

    _, err = ezo.dial()
    if err:
        print("dial error: {}".format(err))
        exit(1)

    # get the compiled contract proxy by it's source hash
    c, err = Contract.load_from_hash(args.command[1], ezo)
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


