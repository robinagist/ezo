'''
library for Easy Oracle
(c) 2018 - Robin A. Gist - All Rights Reserved
'''

import web3
from solc import compile_source
from web3 import Web3, WebsocketProvider


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
    compiled = None
    abi = None
    bin = None
    name = None
    address = None
    filepath = None
    source = None
    tx_hash = None
    config = None

    def __init__(self, config):
        self.config = config

    # loads the contract from file
    def load(self, filepath):
        self.filepath = filepath
        try:
            with open(self.filepath, "r") as fh:
                self.source = fh.read()
        except Exception as e:
            print("error: ".format(e))

    # compiles the contract
    def compile(self):
        self.compiled = compile_source(self.source)

    # deploys the contract
    def deploy(self, w3 , account, name):
        self.name = ":{}".format(name)
        interface = self.compiled[self.name]

        self.abi = interface['abi']
        self.bin = interface['bin']

        contract = w3.eth.contract(abi=self.abi, bytecode=self.bin)
        self.tx_hash = contract.deploy(transaction={'from': account, 'gas': 40000})
        tx_receipt = w3.eth.getTransactionReceipt(self.tx_hash)
        self.address = tx_receipt['contractAddress']

    # saves the compiled contract essentials to leveldb
    def save(self):
        pass



class Event:
    name = None

    def __init__(self, name):
        pass

