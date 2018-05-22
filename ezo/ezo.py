'''
EZOracle
(c) 2018 - Robin A. Gist - All Rights Reserved
This code is released under the MIT License

USE AT YOUR OWN RISK

'''
import argparse
from utils import initialize, load_configuration
from lib import EZO


# parse the command line
parser = argparse.ArgumentParser()

parser.add_argument('command', nargs='*', metavar='create|compile|deploy|gen|view|start',
                    help="use: 'create' to create initial project, "
                         "'compile' contract <--all|--file|--address>"
                         "'deploy' to compile and deploy contracts, 'start' to start")

parser.add_argument("-c", "--config",
                    metavar='CONFIGFILE',
                    dest="configfile",
                    help="specify configuration file (defaults to config.json)", default="config.json")

parser.add_argument("-s", '--stage',
                    metavar="STAGE",
                    dest="stage",
                    help="run all actions on <STAGE> (e.g. dev, prod)")


args = parser.parse_args()

### initialize a new project and exit
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

### compile
if args.command[0] == 'compile':
    # single file in contracts directory

    if args.command[1]:
        filename = args.command[1]
        print(filename)
    else:
        print("currently only supports compiling a single source file")
        exit(0)

# if deploy is set, compile and deploy the contract
# stage must be set before deploying
if not args.stage:
    print("target stage must be set with the -s option before deploying")
    exit(0)
ezo.stage = args.stage

_, err = ezo.dial()
if err:
    print("dial error: {}".format(err))
    exit(1)

### deploy
if args.command == 'deploy':


