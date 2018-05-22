'''
library for ezo
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


from solc import compile_source
from web3 import Web3, WebsocketProvider
from utils import get_url, load_configuration
from pymongo import MongoClient
from datetime import datetime
import json


class EZO:

    w3 = None
    db = None
    client = None
    config = None
    stage = None

    def __init__(self, configfile):

        config, err = load_configuration(configfile)
        if err:
            print("error loading configuration: {}".format(err))
            exit(1)

        self.config = config

    def dial(self, url=None):
        '''
        connects to a remote WebSocket EVM provider

        :param url: string (optional) - resource in which to connect.
        if not provided, will use default for the stage
        :returns: provider, error
        '''
        if not url:
            url = get_url(self.config, self.stage)

        if not url.startswith('ws') or not url.startswith('wss'):
            return None, "URL must be WebSocket:  ws or wss"
        try:
            self.w3 = Web3(WebsocketProvider(url))
        except Exception as e:
            return None, e

        return self.w3, None

    def connect(self, url=None):
        if not url:
            url = self.config["database"]["url"]
        name = self.config["database"]["name"]

        try:
            self.client = MongoClient(url)
            self.db = self.client[name]
        except Exception as e:
            return None, e
        return self.db, None

    def close(self):
        self.client.close()


# main oracle class
class Oracle:

    # event callback dict
    _ecb = dict()

    # account address
    address = None
    config = None

    def __init__(self, config):
        # open connection to WebSockets provider

        pass

    def set_event_handler(self, event, handler):
        self._ecb[event] = handler

    async def start(self):
        pass

    async def stop(self):
        pass


class Contract:

    address = None
    abi = None
    bin = None
    name = None
    source = None
    source_md = None
    tx_hash = None
    timestamp = None
    _ezo = None

    def __init__(self, name, ezo):
        self.name = name
        self._ezo = ezo
        self.timestamp = datetime.utcnow()


    def deploy(self, w3, account):
        '''
        deploy this contract
        :param w3: network targeted for deployment
        :param account:  the account address to use
        :return: address, err
        '''

        try:
            contract = w3.eth.contract(abi=self.abi, bytecode=self.bin)
            #TODO - proper gas calculation
            self.tx_hash = contract.deploy(transaction={'from': account, 'gas': 40000})
            tx_receipt = w3.eth.getTransactionReceipt(self.tx_hash)
            self.address = tx_receipt['contractAddress']

        except Exception as e:
            return None, e

        return self.address, None

    # saves the compiled contract essentials to leveldb
    def save(self):
        try:
            contract_collection = self._ezo.db["contracts"]
        except Exception as e:
            return None, e

        c = dict()
        c["address"] = self.address
        c["name"] = self.name
        c["abi"] = self.abi
        c["bin"] = self.bin
        c["source"] = self.source
        c["source-md"] = self.source_md
        c["tx-hash"] = self.tx_hash
        c["timestamp"] = self.timestamp
        c["deployed"] = "not deployed"

        try:
            iid = contract_collection.insert(c)
        except Exception as e:
            return None, e
        return iid



    def load(self, filepath):
        '''
        loads a contract file

        :param filepath: (string) - contract filename
        :return: source, err
        '''

        try:
            with open(filepath, "r") as fh:
                self.source = fh.read()
        except Exception as e:
            return None, e
        return self.source, None


    @classmethod
    def compile(cls, source):
        '''

        :param source:
        :return:
        '''
        try:
            compiled = compile_source(source)
            compiled_list = []
            for name in compiled:
                c = Contract(name)
                interface = compiled[name]
                c.abi = interface['abi']
                c.bin = interface['bin']
                compiled_list.append(c)
        except Exception as e:
            return None, e
        return compiled_list, None

class Event:
    name = None

    def __init__(self, name):
        pass

