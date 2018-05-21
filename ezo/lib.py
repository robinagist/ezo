'''
library for ezo
(c) 2018 - Robin A. Gist - All Rights Reserved
'''


from solc import compile_source
import plyvel
from web3 import Web3, WebsocketProvider
from utils import get_url


class EZO:

    w3 = None
    db = None
    config = None
    stage = None

    def __init__(self, config, stage):
        self.stage = stage
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

    def connect(self):
        dburl = self.config.dburl


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

    abi = None
    bin = None
    name = None
    address = None
    source = None
    tx_hash = None
    _config = None

    def __init__(self, name):

        self.name = name

    def deploy(self, w3, account):
        '''
        deploy this contract
        :param w3: network targeted for deployment
        :param account:  the account address to use
        :return: address, err
        '''

        try:
            contract = w3.eth.contract(abi=self.abi, bytecode=self.bin)
            self.tx_hash = contract.deploy(transaction={'from': account, 'gas': 40000})
            tx_receipt = w3.eth.getTransactionReceipt(self.tx_hash)
            self.address = tx_receipt['contractAddress']

        except Exception as e:
            return None, e

        return self.address, None

    # saves the compiled contract essentials to leveldb
    def save(self):
        pass

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
        compiled = compile_source(source)
        compiled_list = []
        for name in compiled:
            c = Contract(name)
            interface = compiled[name]
            c.abi = interface['abi']
            c.bin = interface['bin']
            compiled_list.append(c)
        return compiled_list, None

class Event:
    name = None

    def __init__(self, name):
        pass

