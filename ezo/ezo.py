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

parser.add_argument('command', metavar='create|compile|deploy|view|start',
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

# initialize a new project and exit
if args.command == 'create':
    initialize()
    print("new ezo project initialized")
    exit()

# load the configuration
config = load_configuration(args.configfile)
ezo = EZO(config, args.stage)

_, err = ezo.dial()
if err:
    print("dial error: {}".format(err))
    exit(1)

_, err = ezo.connect()
if err:
    print("db connect error: {}".format(err))
    exit(1)

# if deploy is set, compile and deploy the contract
#if args.command == 'deploy':

