'''
library for ezo
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


from solc import compile_source
from web3 import Web3, WebsocketProvider, HTTPProvider
from core.helpers import get_url, get_hash, get_account, get_handler_path, get_topic_sha3
from core.utils import gen_event_handler_code, create_blank_config_obj
from core.helpers import cyan, red, yellow, blue, HexJsonEncoder
from datetime import datetime
import plyvel, pickle, asyncio, time, os.path, os, inflection, json, ast
import importlib.util


class EZO:
    '''
    Easy Oracle (ezo) base class

    '''

    _listeners = dict()
    db = None
    log = None

    # prefix keys for leveldb
    CONTRACT = "CONTRACT"
    COMPILED = "COMPILED"
    DEPLOYED = "DEPLOYED"

    def __init__(self, config, w3=False):
        self.config = config
        self.target = None
        self.w3 = None
        EZO.db = DB(config["project-name"], config["leveldb"] )
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

    def start(self, contract_names):
        '''
        loads the contracts -- starts their event listeners
        :param contract_names:
        :return:
        '''

        if isinstance(contract_names, str):
            contract_names = [contract_names]

        if not isinstance(contract_names, list):
            return None, "error: expecting a string, or a list of contract names"

        contract_listeners = []

        for name in contract_names:
            c, err = Contract.get(name, self)
            if err:
                EZO.log.error(red("error loading contract {}".format(name)))
                EZO.log.error(red(err))
                continue
            if not c:
                EZO.log.warn(blue("contract {} not found".format(name)))
                continue

            address, err = Contract.get_address(name, c.hash, self)

            if err:
                EZO.log.error(red("error obtaining address for contract {}").format(name))
                EZO.log.error(red(err))
                continue
            if not address:
                EZO.log.error(red("no address for contract {}".format(name)))
                continue

            contract_listeners.append(c.listen(address))

        if contract_listeners:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.gather(*contract_listeners)
            )

    @staticmethod
    def create_project(name):
        '''
        creates the initial project skeleton and files
        :param name: the project name
        :return:
        '''

        # from the start directory, create a project directory with the project name
        path = "{}/{}".format(os.getcwd(), name)
        if os.path.exists(path):
            return None, "path {} already exists".format(path)

        # make project directory
        os.makedev(path)

        # create an empty contracts directory
        contracts_dir = "{}/{}".format(path, "contracts")
        os.makedev(contracts_dir)

        # TODO if --include_examples switch, copy example scripts

        # create the handlers directory
        handlers_dir = "{}/{}".format(path, "handlers")
        os.makedev(handlers_dir)

        # create the initial config.json file
        cfg = create_blank_config_obj()
        cfg["contract-dir"] = contracts_dir
        cfg["handlers-dir"] = handlers_dir
        cfg["project-name"] = name

        # write the file to the root project dir
        config_file_path = "{}/{}".format(path, "config.json")
        try:
            with open(config_file_path, "w+") as outfile:
                json.dump(cfg, outfile)
        except Exception as e:
            return None, e
        return None, None


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

    @staticmethod
    def handler(rce, contract):

        ce = ContractEvent(rce)

        # find the mappped method for the topic
        if ce.event_topic in contract.te_map:
            handler_path = contract.te_map[ce.event_topic]
            s = importlib.util.spec_from_file_location("handlers", handler_path)
            handler_module = importlib.util.module_from_spec(s)
            s.loader.exec_module(handler_module)
            handler_module.handler(ce, contract)

        else:
            EZO.log.warn(blue("topic {} not in map".format(ce.event_topic)))


class Contract:

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

        name = self.name.replace('<stdin>:', "")
        key = DB.pkey([EZO.DEPLOYED, name, self._ezo.target, self.hash])

        # see if a deployment already exists for this contract on this target
        if not overwrite:
            _, err = self._ezo.db.get(key)
            if err:
                return None, "deployment on {} already exists for contract {}".format(self._ezo.target, self.hash)

        account = get_account(self._ezo.config, self._ezo.target)

        try:
            ct = self._ezo.w3.eth.contract(abi=self.abi, bytecode=self.bin)
            #TODO - proper gas calculation
            h = {'from': account, 'gas': 4050000}
            tx_hash = ct.constructor().transact(h)
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
            _, err = self._ezo.db.save(key, d, overwrite=overwrite)
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

        print(cyan("listening to address: {}".format(address)))
        interval = self._ezo.config["poll-interval"]

        event_filter = self._ezo.w3.eth.filter({"address": address, "toBlock": "latest"})
        loop = asyncio.new_event_loop()
        try:
            while True:
                for event in event_filter.get_new_entries():
                    if EZO.log:
                        EZO.log.debug(yellow("event received: {}".format(event)))
                    ContractEvent.handler(event, self)
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
        address = self._ezo.w3.toChecksumAddress(response_data["address"])
        tx_dict["account"] = get_account(self._ezo.config, self._ezo.target)
        self._ezo.w3.eth.defaultAccount = tx_dict['account']

        if not self.contract_obj:
            try:
                self.contract_obj = self._ezo.w3.eth.contract(address=address, abi=self.abi)
            except Exception as e:
                return None, e

        method = response_data["function"]
        params = response_data["params"]
        contract_func = self.contract_obj.functions[method]
        try:
            if not params:
                tx_hash = contract_func().transact()
            else:
                tx_hash = contract_func(*params).transact()

            receipt = self._ezo.w3.eth.waitForTransactionReceipt(tx_hash)
        except Exception as e:
            return None, "error executing transaction: {}".format(e)

        return receipt, None

    def save(self, overwrite=False):

        c = dict()
        c["name"] = self.name
        c["abi"] = self.abi
        c["bin"] = self.bin
        c["source"] = self.source
        c["hash"] = get_hash(self.source)
        c["timestamp"] = self.timestamp
        c["te-map"] = self.te_map


        # save to compiled contract
        name = self.name.replace('<stdin>:',"")

        key = DB.pkey([EZO.COMPILED, name, c["hash"]])
        ks, err =  self._ezo.db.save(key, c, overwrite=overwrite)
        if err:
            return None, err

        # save to contract
        key = DB.pkey([EZO.CONTRACT, name])
        ks, err = self._ezo.db.save(key, c, overwrite=True)
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
                    print(red("gen error: {}".format(e)))
                    errors.append(e)
                    continue

            #  map the topic to the handler
            self.te_map[topic] = eh

        _, err = self.save(overwrite=True)
        if err:
            return None, err
        return None, errors


    def paramsForMethod(self, method, data):
        '''
        marshals contract method parameters (in a list) to the format the contract is expecting.  this method
        is used by the SEND and CALL commands, so that method parameters can be typed in easily from the
        command line.  it uses the contract ABI for reference

        :param method: the contract method to call (case sensitive)
        :param data: STRING - an ordered list of method parameters enclosed in quotes (e.g. "['bob',27]")
        matching the signature of the contract method

        :return: a list of properly formatted data elements
        '''

        v = ast.literal_eval(data)
        if not v:
            return None
        return v


    @classmethod
    def send(cls, ezo, name, method, data):
        '''
        runs a transaction on a contract method
        :param ezo:  ezo instance
        :param name:  name of the Contract
        :param method:  name of the contract method
        :param data: formatted data to send to the contract method
        :return:
        '''

        # load the contract by name
        c, err = Contract.get(name, ezo)
        if err:
            return None, err

        address, err = Contract.get_address(name, c.hash, ezo)
        if err:
            return None, err

        d = dict()
        d["address"] = address
        d["function"] = method
        d["params"] = c.paramsForMethod(method, data)


        resp, err = c.response(d)
        if err:
            return None, err

        return resp, None

    @staticmethod
    def call(ezo, name, method, data):
        '''
        calls a method with data and returns a result without changing the chain state
        :param ezo:  ezo instance
        :param name:  name of the Contract
        :param method:  name of the contract method
        :param data: formatted data to send to the contract method
        :return:
        '''

        # load the contract by name
        c, err = Contract.get(name, ezo)
        if err:
            return None, err

        address, err = Contract.get_address(name, c.hash, ezo)
        if err:
            return None, err

        params = c.paramsForMethod(method, data)

        address = ezo.w3.toChecksumAddress(address)
        ezo.w3.eth.defaultAccount = get_account(ezo.config, ezo.target)

        if not c.contract_obj:
            try:
                c.contract_obj = ezo.w3.eth.contract(address=address, abi=c.abi)
            except Exception as e:
                return None, e

        contract_func = c.contract_obj.functions[method]
        try:
            if not params:
                result = contract_func().call()
            else:
                result = contract_func(*params).call()

        except Exception as e:
            return None, "error executing call: {}".format(e)

        return result, None


    @staticmethod
    def get(name, ezo):
        '''
        get the latest compiled contract instance by contract name
        :param name:
        :param ezo:
        :return:
        '''

        key = DB.pkey([EZO.CONTRACT, name])
        cp, err = ezo.db.get(key)
        if err:
            return None, err

        if not cp:
            return None, None

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
    def create_from_hash(hash, ezo):
        '''
        given the hash of a contract, returns a contract  from the data store
        :param hash: (string) hash of the contract source code
        :param ezo: ezo instance
        :return: contract instance, error
        '''

        cp, err = ezo.db.get("contracts", hash)
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
    def get_address(name, hash, ezo):
        '''
        fetches the contract address of deployment

        :param hash: the contract file hash
        :return: (string) address of the contract
                 error, if any
        '''

        key = DB.pkey([EZO.DEPLOYED, name, ezo.target, hash])

        d, err = ezo.db.get(key)
        if err:
            return None, err
        if not d:
            return None, None
        return d['address'].lower(), None


class Catalog:
    '''
    a filesystem catalog for ABIs

    motivation:  LevelDB is a single user DB.  Which means when the test client is executed againt a contact
    while ezo is running as an oracle, it cannot get access to contract ABI information it needs to make
    a contract call without having to recompile the contract itself.  When ezo compiles a contract, it will save
    the ABI to this filesystem catalog, so that the test client can access them while ezo runs as an oracle
    in another process.
    '''

    path = None

    @staticmethod
    def put(contract_name, abi):
        '''
        save the contract's ABI

        :param contract_name: string - name of the contract
        :param abi: the contract's abi JSON file
        :return: None, None if saved okay
                 None, error is an error
        '''

        if not Catalog.path:
            return None, "path to catalog must be set before saving to it"
        if not contract_name:
            return None, "contract name must be provided before saving"
        if not abi:
            return None, "contract ABI missing"

        abi_file = "{}/{}.abi".format(Catalog.path, contract_name)

        try:
            with open(abi_file, "w+") as file:
                file.write(abi)
        except Exception as e:
            return None, "Catalog.put error: {}".format(e)
        return None, None


    @staticmethod
    def get(contract_name):
        '''
        return the contract's ABI, marshaled into python dict
        :param contract_name: string - name of the contract to load
        :return: ABI, None - if successful
                 None, error - if error
        '''

        if not Catalog.path:
            return None, "path to catalog must be set before searching it"
        if not contract_name:
            return None, "contract name missing"

        abi_file = "{}/{}.abi".format(Catalog.path, contract_name)

        try:
            with open(abi_file, "r") as file:
                abi = file.read()
        except Exception as e:
            return None, "Catalog.get error: {}".format(e)
        return abi, None


class DB:
    '''
    data storage abstraction layer for LevelDB

    note:  the db is opened and closed on demand.  this allows multiple applications to use the same
    DB at the same time.  a pseudo lock-wait mechanism is implemented in open.

    '''

    db = None
    project = None
    dbpath = None

    def __init__(self, project, dbpath=None):

        DB.dbpath = dbpath if dbpath else '/tmp/ezodb/'
        DB.project = project if project else 'ezo_project_default'

    def open(self):
        '''
        attempts to open the database.  if it gets a locked message, it will wait one second and try
        again.  if it is still locked, it will return an error
        :return: None, None if successful
                 None, error if error
        '''
        cycle = 2
        count = 0

        while(True):
            try:
                DB.db = plyvel.DB(DB.dbpath, create_if_missing=True).prefixed_db(bytes(DB.project, 'utf-8'))
                if DB.db:
                    break
            except Exception as e:
                # wait for other program to unlock the db
                count+=1
                time.sleep(1)
                if count >= cycle:
                    return None, "DB error: {}".format(e)
        return None, None

    def save(self, key, value, overwrite=False, serialize=True):

        if isinstance(key, str):
            key = bytes(key, 'utf=8')


        _, err = self.open()
        if err:
            return None, err

        if not overwrite:
            a, err = self.get(key)
            if err:
                return None, err
            if a:
                return None, "{} already exists ".format(key)

        if serialize:
            value = pickle.dumps(value)
        try:
            DB.db.put(key, value)
        except Exception as e:
            return None, e
        self.close()

        return key, None

    def delete(self, key):
        pass

    def get(self, key, deserialize=True):

        _, err = self.open()
        if err:
            return None, "DB.get error: {}".format(err)

        try:
            val = DB.db.get(key)
            if not val:
                return None, None
            if deserialize:
                obj = pickle.loads(val)
            else:
                obj = val

        except Exception as e:
            return None, e
        self.close()

        return obj, None

    def find(self, keypart):

        _, err = self.open()
        if err:
            return None, err

        if isinstance(keypart, str):
            keypart = bytes(keypart)
        elif not isinstance(keypart, bytes):
            return None, "keypart must be a byte string"

        res = list()
        try:
            it = DB.db.iterator(prefix=keypart)
            for key, value in it:
               res.append({key.decode('utf-8'): pickle.loads(value)})
        except Exception as e:
            return None, e

        self.close()

        return res, None

    def close(self):
        DB.db.db.close()
        DB.db = None

    @staticmethod
    def pkey(elems):
        key = ""
        for e in elems:
            key += e
            key += ":"
        return bytes(key, 'utf=8')





