import json, argparse

class EZOCommandProcessor():

    argv = None
    args = None

    def __init__(self, argv):
        self.argv = argv
        self._setup()

    def _setup(self):
        # parse the command line
        parser = argparse.ArgumentParser(self.argv)

        parser.add_argument('command', nargs='*', metavar='create|compile|deploy|gen|view|delete|start',
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

        self.args = parser.parse_args()
        return self.args


# sets up the current directory for an ezoracle project
def initialize():
    # copy the config.json template to the current directory
    # load the config.json template
    # create the default directories
    pass


# load configuration file
def load_configuration(configfile):
    try:
        with open(configfile) as config:
            cfg = json.load(config)
            config.close()
            return cfg, None
    except Exception as e:
        return None, e




