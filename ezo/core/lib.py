'''
library for ezo
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


from solc import compile_source
from web3 import Web3, WebsocketProvider, HTTPProvider
from core.helpers import get_url, get_hash, get_account, get_handler_path, get_topic_sha3
from core.generators import gen_event_handler_code, create_blank_config_obj, \
    create_sample_contracts_1, create_sample_contracts_2
from core.helpers import cyan, red, yellow, blue, bright, magenta, reset, HexJsonEncoder
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

    def __init__(self, config):
        if not config:
            return
        self.config = config
#        self.target = None
        self.w3 = None
        EZO.db = DB(config["project-name"], config["leveldb"] )

    def dial(self, target):
        '''
        connects to a node

        :param url: string (optional) - resource in which to connect.
        if not provided, will use default for the stage
        :returns: provider, error
        '''

        if not target:
            return None, "target network must be specified with -t or --target"

        url = get_url(self.config, target)

        try:
            if url.startswith('ws'):
                self.w3 = Web3(WebsocketProvider(url))
            elif url.startswith('http'):
                self.w3 = Web3(HTTPProvider(url))
            elif url.endswith('ipc'):
                if url == 'ipc':
                    url = None
                self.w3 = Web3(Web3.IPCProvider(url))
            else:
                return None, "Invalid Provider URL: {}".format(url)

        except Exception as e:
            return None, e

        return self.w3, None

    def start(self, contract_names, target):
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

            address, err = Contract.get_address(name, c.hash, self.db, target=target)

            if err:
                EZO.log.error(red("error obtaining address for contract {}").format(name))
                EZO.log.error(red(err))
                continue
            if not address:
                EZO.log.error(red("no address for contract {}".format(name)))
                continue

            contract_listeners.append(c.listen(address, target))

        if contract_listeners:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                asyncio.gather(*contract_listeners)
            )
        else:
            return None, "unable to start contract listeners"


    @staticmethod
    def create_project(name, include_examples=True):
        '''
        creates the initial project skeleton and files
        :param name: the project name
        :return:
        '''

        # from the start directory, create a project directory with the project name
        path = "{}/{}".format(os.getcwd(), name)
        if os.path.exists(path):
            return None, "path {} already exists".format(path)

        print(bright("creating new ezo project '{}".format(name)))

        # make project directory
        os.mkdir(path)
        print(bright("created project directory: '{}".format(path)))

        # create an empty contracts directory
        contracts_dir = "{}/{}".format(path, "contracts")
        os.mkdir(contracts_dir)
        print(bright("created contract directory: '{}".format(contracts_dir)))

        if include_examples:
            c = [(create_sample_contracts_1(), 'contract1.sol'), (create_sample_contracts_2(), 'contract2.sol')]
            for s in c:
                c, fn = s
                file_path = "{}/{}".format(contracts_dir, fn)
                try:
                    with open(file_path, "w+") as outfile:
                        outfile.write(c)
                except Exception as e:
                    print(bright("problem creating sample file: '{}".format(path)))
                    return None, e
                print(bright("created sample contract: '{}".format(fn)))

        # create the handlers directory
        handlers_dir = "{}/{}".format(path, "handlers")
        os.mkdir(handlers_dir)
        print(bright("created handlers directory: '{}".format(handlers_dir)))

        # leveldb directory (created by level)
        leveldb = "{}/{}".format(path, "ezodb")

        # create the initial config.json file
        cfg = create_blank_config_obj()

        cfg["ezo"]["contract-dir"] = contracts_dir
        cfg["ezo"]["handlers-dir"] = handlers_dir
        cfg["ezo"]["project-name"] = name
        cfg["ezo"]["leveldb"] = leveldb
        print(bright("creating configuration: '{}".format(path)))

        # write the file to the root project dir
        config_file_path = "{}/{}".format(path, "ezo.conf")
        try:
            with open(config_file_path, "w+") as outfile:
                json.dump(cfg, outfile, indent=2)
        except Exception as e:
            print(bright("problem creating configuration file: '{}".format(path)))
            return None, e

        return None, None


class ContractEvent:

    def __init__(self, rce, target):
        self.timestamp = int(time.time())
        self.address = rce["address"]
        self.data = rce["data"]
        self.log_index = rce["logIndex"]
        self.tx = rce["transactionHash"]
        self.topics = rce["topics"]
        self.block_number = rce["blockNumber"]
        self.event_topic = self.topics[0]
        self.target = target

    @staticmethod
    def handler(rce, contract, target):

        ce = ContractEvent(rce, target)

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

    def deploy(self, target, overwrite=False):
        '''
        deploy this contract
        :param target:
        :param account:  the account address to use
        :return: address, err
        '''

        name = self.name.replace('<stdin>:', "")
        key = DB.pkey([EZO.DEPLOYED, name, target, self.hash])

        if not target:
            return None, "target network must be set with -t or --target"

        password = os.environ['EZO_PASSWORD'] if 'EZO_PASSWORD' in os.environ else None

        # see if a deployment already exists for this contract on this target
        if not overwrite:
            res, err = self._ezo.db.get(key)
            if err:
                return None, "ERROR: Contract.deployment() {}".format(err)
            if res:
                return None, "deployment on {} already exists for contract {} use '--overwrite' to force".format(target, self.hash)

        account = self._ezo.w3.toChecksumAddress(get_account(self._ezo.config, target))
        self._ezo.w3.eth.accounts[0] = account

        try:
            u_state = self._ezo.w3.personal.unlockAccount(account, password)
        except Exception as e:
            return None, "unable to unlock account for {} using password".format(account)

        try:
            ct = self._ezo.w3.eth.contract(abi=self.abi, bytecode=self.bin)
            gas_estimate = ct.constructor().estimateGas()
            h = {'from': account, 'gas': gas_estimate + 1000}
            tx_hash = ct.constructor().transact(h)
            tx_receipt = self._ezo.w3.eth.waitForTransactionReceipt(tx_hash)
            address = tx_receipt['contractAddress']

        except Exception as e:
            return None, e
#        finally:
#            self._ezo.w3.personal.lockAccount(account)

        d = dict()
        d["contract-name"] = self.name
        d["hash"] = self.hash
        d["tx-hash"] = tx_hash
        d["address"] = address
        d["gas-used"] = tx_receipt["gasUsed"]
        d["target"] = target
        d["timestamp"] = datetime.utcnow()

        # save the deployment information
        try:
            _, err = self._ezo.db.save(key, d, overwrite=overwrite)
            if err:
                return None, err
        except Exception as e:
            return None, e

        return address, None

    async def listen(self, address, target):
        '''
        starts event listener for the contract
        :return:
        '''

        if not address:
            return None, "listening address not provided"

        EZO.log.info(bright("hello ezo::listening to address: {}".format(blue(address))))
        interval = self._ezo.config["poll-interval"]

        event_filter = self._ezo.w3.eth.filter({"address": address, "toBlock": "latest"})
        loop = asyncio.new_event_loop()
        try:
            while True:
                for event in event_filter.get_new_entries():
                    if EZO.log:
                        EZO.log.debug(bright("event received: {}".format(event)))
                    ContractEvent.handler(event, self, target)
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
        if "target" not in response_data:
            return None, "target missing from response_data payload"


        address = self._ezo.w3.toChecksumAddress(response_data["address"])
        account = self._ezo.w3.toChecksumAddress(get_account(self._ezo.config, response_data["target"]))

        self._ezo.w3.eth.accounts[0] = account

        tx_dict = dict()
        tx_dict["account"] = account
        tx_dict["from"] = account

        password = os.environ['EZO_PASSWORD'] if 'EZO_PASSWORD' in os.environ else None

        u_state = self._ezo.w3.personal.unlockAccount(account, password)

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
                tx_dict["gas"] = contract_func().estimateGas() + 1000
                tx_hash = contract_func().transact(tx_dict)
            else:
                tx_dict["gas"] = contract_func(*params).estimateGas() + 1000
                tx_hash = contract_func(*params).transact(tx_dict)

            receipt = self._ezo.w3.eth.waitForTransactionReceipt(tx_hash)
        except Exception as e:
            return None, "error executing transaction: {}".format(e)
  #      finally:
#            self._ezo.w3.personal.lockAccount(account)

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
                code, err = gen_event_handler_code(event_name)
                if err:
                    print(red("gen error: {}".format(err)))
                try:
                    with open(eh, "w+") as f:
                        f.write(code)

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

        '''

        v = ast.literal_eval(data)
        if not v:
            return None
        return v


    @staticmethod
    def send(ezo, name, method, data, target):
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

        address, err = Contract.get_address(name, c.hash, ezo.db, target)
        if err:
            return None, err

        d = dict()
        d["address"] = address
        d["function"] = method
        d["params"] = c.paramsForMethod(method, data)
        d["target"] = target


        resp, err = c.response(d)
        if err:
            return None, err

        return resp, None

    @staticmethod
    def call(ezo, name, method, data, target):
        '''
        calls a method with data and returns a result without changing the chain state
        :param ezo:  ezo instance
        :param name:  name of the Contract
        :param method:  name of the contract method
        :param data: formatted data to send to the contract method
        :param target: the target network
        :return:
        '''

        # load the contract by name
        c, err = Contract.get(name, ezo)
        if err:
            return None, err

        address, err = Contract.get_address(name, c.hash, ezo.db, target)
        if err:
            return None, err

        params = c.paramsForMethod(method, data)

        address = ezo.w3.toChecksumAddress(address)
        ezo.w3.eth.defaultAccount = ezo.w3.toChecksumAddress(get_account(ezo.config, target))

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
    def get_address(name, hash, db, target=None):
        '''
        fetches the contract address of deployment

        :param hash: the contract file hash
        :return: (string) address of the contract
                 error, if any
        '''

        key = DB.pkey([EZO.DEPLOYED, name, target, hash])

        d, err = db.get(key)
        if err:
            return None, err
        if not d:
            return None, None
        return d['address'].lower(), None


class Catalog:
    '''
    a filesystem catalog for ABIs

    motivation:  LevelDB is a single user DB.  Which means when the test client is executed against a contract
    while ezo is running as an oracle, it cannot get access to contract ABI information. it needs to make
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

    the db is opened and closed on demand.  this allows multiple applications to use the same
    DB at the same time.  a pseudo lock-wait mechanism is implemented in the open method).

    a caching object is placed ahead of and behind get method reads and behind save method writes.  This keeps
    oracle mode from having to hit leveldb very often at all.

    '''

    db = None
    project = None
    dbpath = None
    cache = dict()

    def __init__(self, project, dbpath=None):

        DB.dbpath = dbpath if dbpath else '~/ezodb/'
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
            key = bytes(key, 'utf-8')

        if not overwrite:
            a, err = self.get(key)
            if err:
                return None, err
            if a:
                return None, "{} already exists ".format(key)

        _, err = self.open()
        if err:
            return None, err

        v = pickle.dumps(value) if serialize else value
        try:
            DB.db.put(key, v)

        except Exception as e:
            return None, e

        finally:
            self.close()

        DB.cache[key] = value
        return key, None

    def delete(self, key):
        pass

    def get(self, key, deserialize=True):

        if isinstance(key, str):
            key = bytes(key, 'utf-8')

        if key in DB.cache:
            return DB.cache[key], None

        _, err = self.open()
        if err:
            return None, "DB.get error: {}".format(err)

        val = DB.db.get(key)
        if not val:
            self.close()
            return None, None
        try:
            if deserialize:
                obj = pickle.loads(val)
            else:
                obj = val

        except Exception as e:
            return None, e
        finally:
            self.close()

        DB.cache[key] = obj
        return obj, None

    def find(self, keypart):

        _, err = self.open()
        if err:
            return None, err

        if isinstance(keypart, str):
            keypart = bytes(keypart, 'utf-8')

        elif not isinstance(keypart, bytes):
            return None, "keypart must be a string or byte string"

        res = list()
        try:
            it = DB.db.iterator(prefix=keypart)
            it.seek_to_start()

            for key, value in it:
               res.append({key.decode('utf-8'): pickle.loads(value)})
        except Exception as e:
            return None, e
        finally:
            self.close()

        return res, None

    def close(self):
#        DB.db.db.close()
        DB.db = None

    @staticmethod
    def pkey(elems):
        key = ""
        for e in elems:
            key += e
            key += ":"
        return bytes(key, 'utf-8')





