'''
EZOracle
(c) 2018 - Robin A. Gist - All Rights Reserved
This code is released under the MIT License

USE AT YOUR OWN RISK

'''
import argparse
from utils import initialize, load_configuration, get_account, get_url
from web3 import Web3, WebsocketProvider

# parse the command line
parser = argparse.ArgumentParser()

parser.add_argument('command', metavar='init|deploy|start',
                    help="use: 'init' to create initial project, "
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
if args.command == 'init':
    initialize()
    print("new ezo project initialized")
    exit()

# load the configuration
config = load_configuration(args.configfile)

print("stage: {}".format(args.stage))
# open connection to websocket provider
url = get_url(config, args.stage)
print("url: {}".format(url))
w3 = Web3(WebsocketProvider(url))

# if deploy is set, compile and deploy the contract
# if args.command == 'deploy':

