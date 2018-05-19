'''
library for Easy Oracle
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


# sets up the current directory for an ezoracle project
def initialize(config_template):
    # copy the config.json template to the current directory
    # load the config.json template
    # create the default directories
    pass


# main oracle class
class Oracle:
    # event callback dict
    ecb = dict()
    # account address
    address = None

    def __init__(self, config=None):
        # initialize config

        # open connection to WebSockets provider

        pass

    def add_event_and_callback(self, event, callback):
        self.ecb[event] = callback

    async def start(self):
        pass

    async def stop(self):
        pass


class Contract:
    hex = bin = abi = name = address = None

    def __init__(self):
        pass

    # loads the contract from file
    def load(self):
        pass

    # compiles the contract
    def compile(self):
        pass

    # deploys the contract
    def deploy(self):
        pass


class Event:
    name = None

    def __init__(self, name):
        pass

