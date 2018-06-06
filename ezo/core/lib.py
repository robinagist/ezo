'''
library for ezo
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


from solc import compile_source
from web3 import Web3, WebsocketProvider, HTTPProvider
from core.helpers import get_url, get_hash, get_account, get_handler_path, get_topic_sha3
from core.utils import gen_event_handler_code
from datetime import datetime
from collections import OrderedDict
import plyvel, pickle, asyncio, xxhash, time, os.path, os, inflection
import importlib.util


class EZO:
    '''
    Easy Oracle (ezo) base class

    '''

    _listeners = dict()
    db = None

    def __init__(self, config, w3=False):
        self.config = config
        self.target = None
        self.w3 = None
        EZO.db = DB()
        self.event_queue = ContractEventQueue(EZO.db)
        if w3:
            self.dial()

    def dial(self, url=None):
        '''
        connects to a node

        :param url: string (optional) - resource in which to connect.
        if not provided, will use default for the stage
        :returns: provider, error
        '''
        if not url:
            url = get_url(self.config, self.target)

        try:
            if url.startswith('ws'):
                self.w3 = Web3(WebsocketProvider(url))
            elif url.startswith('http'):
                self.w3 = Web3(HTTPProvider(url))

        except Exception as e:
            return None, e

        return self.w3, None


    def view_deployments(self):
        deploys = list()


    def view_contracts(self):
        contracts = list()


    def view_source(self, hash):
        pass


    def start(self, contract_hashes):
        '''
        loads the contracts from their hashes and starts their event listeners
        :param contracts:
        :return:
        '''

        if isinstance(contract_hashes, str):
            contract_hashes = [contract_hashes]

        if not isinstance(contract_hashes, list):
            return None, "error: expecting a string, or a list of contract hashes"

        contract_listeners = []

        for hash in contract_hashes:
            c, err = Contract.create_from_hash(hash, self)
            # todo - better way to handle this?
            if err:
                return None, err

            address, err = Contract.get_address(hash, self)
            # TODO - better way to handle this?
            if err:
                return None, err
            contract_listeners.append(c.listen(address))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            asyncio.gather(*contract_listeners)
        )

class ContractEvent:

    def __init__(self, rce):
        self.timestamp = int(time.time())
        self.address = rce["address"]
        self.data = rce["data"]
        self.log_index = rce["logIndex"]
        self.tx = rce["transactionHash"]
        self.topics = rce["topics"]
        self.block_number = rce["blockNumber"]
        self.event_topic = self.topics[0]

    @classmethod
    def handler(cls, rce, contract):

        ce = ContractEvent(rce)

        # find the mappped method for the topic
        if ce.event_topic in contract.te_map:
            print("found the topic")
            handler_path = contract.te_map[ce.event_topic]
            s = importlib.util.spec_from_file_location("handlers", handler_path)
            handler_module = importlib.util.module_from_spec(s)
            s.loader.exec_module(handler_module)
            handler_module.handler(ce, contract)
    #        h.handler("in the handler")


        else:
            print("topic not in map")


class Contract:

    mq = OrderedDict()

    def __init__(self, name, ezo):
        self.name = name
        self._ezo = ezo
        self.timestamp = datetime.utcnow()
        self.hash = None
        self.abi  = None
        self.bin  = None
        self.source = None
        self.te_map = dict()
        self.contract_obj = None

    def deploy(self, overwrite=False):
        '''
        deploy this contract
        :param w3: network targeted for deployment
        :param account:  the account address to use
        :return: address, err
        '''

        # see if a deployment already exists for this contract on this target
        if not overwrite:
            if self._ezo.db.find(self._ezo.target, self.hash):
                return None, "deployment on {} already exists for contract {}".format(self._ezo.target, self.hash)

        account = get_account(self._ezo.config, self._ezo.target)

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
        d["target"] = self._ezo.target
        d["timestamp"] = datetime.utcnow()

        # save the deployment information
        try:
            _, err = self._ezo.db.save(self._ezo.target, self.hash, d, overwrite=overwrite)
            if err:
                return None, err
        except Exception as e:
            return None, e
        return address, None


    async def listen(self, address):
        '''
        starts event listener for the contract
        :return:
        '''

        print("listening to address: {}".format(address))
        interval = 1

        event_filter = self._ezo.w3.eth.filter({"address": address, "toBlock": "latest"})
        loop = asyncio.new_event_loop()
        try:
            while True:
                for event in event_filter.get_new_entries():
  #                  print("got an event: {}".format(event))

                    ContractEvent.handler(event, self)

 #               print("in event loop")
                await asyncio.sleep(interval)
        except Exception as e:
            return None, e

        finally:
            loop.close()

    def response(self, response_data):
        '''
        called by the event handler with the result data
        :param response_data: result data
        :return:
        '''

        if "address" not in response_data:
            return None, "address missing from response_data payload"
        if "function" not in response_data:
            return None, "method missing from response_data payload"
        if "params" not in response_data:
            return None, "params missing from response_data payload"

        tx_dict = dict()
        tx_dict["gas"] = 50000
        address = response_data["address"]
        tx_dict["account"] = get_account(self._ezo.config, self._ezo.target)
        self._ezo.w3.eth.defaultAccount = tx_dict['account']

        if not self.contract_obj:
            self.contract_obj = self._ezo.w3.eth.contract(address=address, abi=self.abi)

        method = response_data["function"]
        params = response_data["params"]
        contract_func = self.contract_obj.functions[method]
        try:
            tx_hash = contract_func(*params).transact()
            ks = self._ezo.w3.eth.waitForTransactionReceipt(tx_hash)
        except Exception as e:
            print("error: {}".format(e))
            return None, e

        return tx_hash, None

    def save(self, overwrite=False):

        c = dict()
        c["name"] = self.name
        c["abi"] = self.abi
        c["bin"] = self.bin
        c["source"] = self.source
        c["hash"] = get_hash(self.source)
        c["timestamp"] = self.timestamp
        c["te-map"] = self.te_map

        ks, err =  self._ezo.db.save("contracts", c["hash"], c, overwrite=overwrite)
        if err:
            return None, err
        return ks, None

    def generate_event_handlers(self, overwrite=False):

        # get the contract name, events from the abi
        contract_name = inflection.underscore(self.name.replace('<stdin>:', ''))
        errors = list()

        events = [x for x in self.abi if x["type"] == "event"]
        for event in events:
            #     get the topic sha3
            topic = Web3.sha3(text=get_topic_sha3(event))

            #     build full path to new event handler
            hp = get_handler_path(self._ezo.config, contract_name)
            if not os.path.isdir(hp):
                os.mkdir(hp)
            event_name = inflection.underscore(event['name'])
            eh = "{}/{}_{}".format(hp, event_name, "handler.py")

            #     check to see if it exists
            #     if not, or if overwrite option is on
            if not os.path.exists(eh) or overwrite:

                # create event handler scaffold in python
                try:
                    with open(eh, "w+") as f:
                        f.write(gen_event_handler_code())

                except Exception as e:
                    print("gen error: {}".format(e))
                    errors.append(e)

            #  map the topic to the handler
            self.te_map[topic] = eh

        self.save(overwrite=True)
        return None, errors

    @staticmethod
    def create_from_hash(hash, ezo):
        '''
        given the hash of a contract, returns a contract  from the data store
        :param hash: (string) hash of the contract source code
        :param ezo: ezo instance
        :return: contract instance, error
        '''

        cp, err = ezo.db.find("contracts", hash)
        if err:
            return None, err

        # create a new Contract
        c = Contract(cp["name"], ezo)
        c.abi = cp["abi"]
        c.bin = cp["bin"]
        c.hash = cp["hash"]
        c.source = cp["source"]
        c.timestamp = cp["timestamp"]
        c.te_map = cp['te-map']

        return c, None



    @staticmethod
    def load(filepath):
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


    @staticmethod
    def compile(source, ezo):
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

    @staticmethod
    def get_address(hash, ezo):
        '''
        fetches the contract address of deployment

        :param hash: the contract file hash
        :return: (string) address of the contract
                 error, if any
        '''
        target = ezo.target
        address, err = ezo.db.find(target, hash)
        if err:
            return None, err
        return address['address'].lower(), None


class DB:
    '''
    data storage abstraction layer for LevelDB

    '''

    db = None

    def __init__(self, dbpath=None):
        if not dbpath:
            #TODO - put in configuration
            #TODO - prefix per project
            dbpath = '/tmp/ezodba/'
        DB.db = plyvel.DB(dbpath, create_if_missing=True)

    def save(self, storage_type, key, value, overwrite=False, serialize=True):
        if not isinstance(storage_type, str):
            return None, "storage_type must be a string"
        if not isinstance(key, str):
            return None, "key must be a string"

        if not overwrite:
            a, err = self.find(storage_type, key)
            if err:
                return None, err
            if a:
                return None, "entry for {} in {} already exists ".format(key, storage_type)

        if serialize:
            value = pickle.dumps(value)
        try:
            DB.db.put(DB.pkey(storage_type, key), value)
        except Exception as e:
            return None, e
        return key, None

    def delete(self, storage_type, key):
        pass

    def find(self, storage_type, key, deserialize=True):
        try:
            pkey = DB.pkey(storage_type, key)
            val = DB.db.get(pkey)
            if not val:
                return None, None
            if deserialize:
                obj = pickle.loads(val)
            else:
                obj = val

        except Exception as e:
            return None, e
        return obj, None

    def close(self):
        DB.db.close()

    @staticmethod
    def pkey(storage_type, key):
        return bytes("{}__{}".format(storage_type, key), 'utf-8')





class ContractEventQueue:
    '''
    queue for managing received ethereum contract events

    '''
    _eqpfx = "event_queue"
    _eq_date = "event_date"


    def __init__(self, db):
        self._eq = dict()
        self.db = db

    # if starting, load freshest events into queue - default age limit is one hour
    def load(self, aged=3600):

        pass

    def add(self, contract_event):
        sc = pickle.dumps(contract_event)
        chash = xxhash.xxh64(sc).hexdigest()
        res, err = self.db.save(ContractEventQueue._eqpfx, chash, contract_event)
        if err:
            return None, err
        res, err = self.db.save(ContractEventQueue._eq_date, chash, contract_event.timestamp)
        if err:
            return None, err
        self._eq[chash] = contract_event
        return chash, None

    def prune(self):
        pass

    def find(self):
        pass

    def list(self):
        for key, value in self._eq:
            print("contract: {}  event: {}".format(key, value))





