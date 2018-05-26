'''
library for ezo
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


from solc import compile_source
from web3 import Web3, WebsocketProvider, HTTPProvider
from helpers import get_url, get_hash, get_account
from utils import load_configuration
import pymongo
from datetime import datetime
import asyncio
from multiprocessing import Process



async def event_loop(event_filter, interval=1):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(interval)


def handle_event(event):
    print("event: {}".format(event))


class EZO:
    '''
    Easy Oracle (ezo) base class

    '''

    w3 = None
    db = None
    client = None
    config = None
    stage = None

    _listeners = dict()

    def __init__(self, configfile):
        self.config, err = load_configuration(configfile)
        if err:
            print("error loading configuration: {}".format(err))
            exit(1)

    def dial(self, url=None):
        '''
        connects to a node

        :param url: string (optional) - resource in which to connect.
        if not provided, will use default for the stage
        :returns: provider, error
        '''
        if not url:
            url = get_url(self.config, self.stage)

        try:
            if url.startswith('ws'):
                self.w3 = Web3(WebsocketProvider(url))
            elif url.startswith('http'):
                self.w3 = Web3(HTTPProvider(url))

        except Exception as e:
            return None, e

        return self.w3, None

    def connect(self, url=None):
        '''
        connects to MongoDB instance

        :param url: (string) full URL for the mongo instance
        :return: database handle, error
        '''

        if not url:
            url = self.config["database"]["url"]
        name = self.config["database"]["name"]

        try:
            self.client = pymongo.MongoClient(url)
            self.db = self.client[name]
        except Exception as e:
            return None, e
        return self.db, None


    def view_deployments(self, terms=None):
        deploys = list()
        try:
            for deploy in self.db.deployments.find({}).sort('timestamp', pymongo.DESCENDING):
                deploys.append(deploy)
        except Exception as e:
            return None, e
        return deploys, None

    def view_contracts(self, terms):
        contracts = list()
        try:
            for contract in self.db.contracts.find({}).sort('timestamp', pymongo.DESCENDING):
                contracts.append(contract)
        except Exception as e:
            return None, e
        return contracts, None

    def view_source(self, hash):
        pass


    def close(self):
        '''
        close mongo and web3 connections
        :return: None
        '''
        self.client.close()


    def start(self, contract_hashes):
        '''
        loads the contracts from their hashes and starts their event listeners
        :param contracts:
        :return:
        '''

        print("ezo start - hashes: {}".format(contract_hashes))
        if isinstance(contract_hashes, str):
            contract_hashes = [contract_hashes]

        if not isinstance(contract_hashes, list):
            return None, "error: expecting a string, or a list of contract hashes"

        jobs = []
        for hash in contract_hashes:
            print("hash: {}".format(hash))
            c, err = Contract.create_from_hash(hash, self)
            if err:
                return None, err

            address = Contract.get_address(hash, self)
            if not address:
                return None, "error: no deployment address for {} on target stage {}".format(hash, self.stage)

            p = Process(target=c.listen, args=())
            p.daemon = True
            jobs.append(p)
            p.start()

        for pr in jobs:
            pr.join()

class Contract:

    abi = None
    bin = None
    name = None
    source = None
    hash = None
    timestamp = None
    _ezo = None
    event_filter = None
    handler_dir = None
    deployments = None

    def __init__(self, name, ezo):
        self.name = name
        self._ezo = ezo
        self.timestamp = datetime.utcnow()
        self.handler_dir = self._ezo.config["handler-dir"]


    def deploy(self):
        '''
        deploy this contract
        :param w3: network targeted for deployment
        :param account:  the account address to use
        :return: address, err
        '''

        account = get_account(self._ezo.config, self._ezo.stage)
        try:
            deployments = self._ezo.db["deployments"]
        except Exception as e:
            return None, e

        try:
            ct = self._ezo.w3.eth.contract(abi=self.abi, bytecode=self.bin)
            #TODO - proper gas calculation

            tx_hash = ct.deploy(transaction={'from': account, 'gas': 405000})
            tx_receipt = self._ezo.w3.eth.waitForTransactionReceipt(tx_hash)
            address = tx_receipt['contractAddress']

        except Exception as e:
            return None, e

        d = dict()
        d["contract-name"] = self.name
        d["hash"] = self.hash
        d["tx-hash"] = tx_hash
        d["address"] = address
        d["stage"] = self._ezo.stage
        d["timestamp"] = datetime.utcnow()

        # save the deployment information
        try:
            iid = deployments.insert(d)

        except Exception as e:
            return None, e
        return address, None


    def listen(self, address):
        '''
        starts event listener for the contract
        :return:
        '''

        self.event_filter = self._ezo.w3.eth.filter({"address": address})

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(asyncio.gather(event_loop(self.event_filter)))
        except Exception as e:
            return None, e

        finally:
            loop.close()



    # saves the compiled contract essentials to mongo
    def save(self):
        try:
            contract_collection = self._ezo.db["contracts"]
        except Exception as e:
            return None, e

        c = dict()
        c["name"] = self.name
        c["abi"] = self.abi
        c["bin"] = self.bin
        c["source"] = self.source
        c["hash"] = get_hash(self.source)
        c["timestamp"] = self.timestamp

        try:
            iid = contract_collection.insert(c)
        except Exception as e:
            return None, e
        return iid, None

    @classmethod
    def create_from_hash(cls, hash, ezo):
        '''
        given the hash of a contract, returns a contract  from the data store
        :param hash: (string) hash of the contract source code
        :param ezo: ezo instance
        :return: contract instance, error
        '''
        try:
            cp = ezo.db.contracts.find_one({"hash": hash})
        except Exception as e:
            return None, e

        # create a new Contract
        c = Contract(cp["name"], ezo)
        c.abi = cp["abi"]
        c.bin = cp["bin"]
        c.hash = cp["hash"]
        c.source = cp["source"]
        c.timestamp = cp["timestamp"]

        return c, None



    @classmethod
    def load(cls, filepath):
        '''
        loads a contract file

        :param filepath: (string) - contract filename
        :return: source, err
        '''

        try:
            with open(filepath, "r") as fh:
                source = fh.read()
        except Exception as e:
            return None, e
        return source, None


    @classmethod
    def compile(cls, source, ezo):
        '''
        compiles the source code

        :param source: (string) - contract source code
        :param ezo: - ezo reference for Contract object creation
        :return: (list) compiled source
        '''
        try:
            compiled = compile_source(source)
            compiled_list = []
            for name in compiled:
                c = Contract(name, ezo)
                interface = compiled[name]
                c.abi = interface['abi']
                c.bin = interface['bin']
                compiled_list.append(c)

        except Exception as e:
            return None, e
        return compiled_list, None

    @classmethod
    def get_address(cls, hash, ezo):
        '''
        fetches the contract address of deployment

        :param hash: the contract file hash
        :return: (string) address of the contract
        '''
        stage = ezo.stage
        try:
            address = ezo.db.deployments.find_one({"hash": hash, "stage": stage})
        except Exception as e:
            return None, e
        return address["address"] if "address" in address else None










