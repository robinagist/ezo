'''
EZOracle
(c) 2018 - Robin A. Gist - All Rights Reserved
This code is released under the MIT License

USE AT YOUR OWN RISK

'''
import optparse
from utils import initialize, load_configuration

# parse the command line
usage = "usage: %prog [options] arg"
parser = optparse.OptionParser(usage=usage)

parser.add_option('--init', '--initialize',
                  action='store_true', dest="init",
                  help="initialize an ezo project")

parser.add_option("-c", "--config",
                  metavar='CONFIGFILE',
                  dest="configfile",
                  help="specify configuration file (defaults to config.json)", default="config.json")

parser.add_option("-d", '--deploy',
                  metavar="STAGE",
                  dest="stage",
                  help="compile and deploy contracts for <STAGE> (e.g. dev, prod)")

parser.add_option("--noexample", "--noexamples",
                  action="store_true", dest="noexamples",
                  help="creates initial project without example code"
                  )

options, args = parser.parse_args()

# initialize a new project and exit
if options.init:
    initialize(options.noexamples)
    print("new ezo project initialized")
    exit()

# load the configuration
config = load_configuration(options.configfile)

print("config: {}".format(config))
