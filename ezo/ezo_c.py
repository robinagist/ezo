from cement.core.foundation import CementApp
from cement.core import backend
from cement.core.controller import CementBaseController, expose
from lib import Contract, EZO
from helpers import get_contract_path

VERSION = '0.0.1'
BANNER = '''
ezo - easy Ethereum oracle builder v%s
(c) 2018 - Robin A. Gist - All Rights Reserved
released under the MIT license
use at your own risk
''' % VERSION


class EZOBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'ezo - easy Ethereum oracles'
        arguments = [
            (['-t', '--target'],
             dict(action='store', help='deployment target node (set in configuration')),
            (['-c', '--config'],
             dict(action='store', help='optional full path to ezo configuration file', default='config.json')),
            (['extra_args'],
             dict(action='store', nargs='*')),

        ]
        # create|compile|deploy|gen|view|delete|start


    @expose(help="create a new ezo project in the current director")
    def create(self):
        self.app.log.info("initalizing new project")

    @expose(help="compile smart contracts")
    def compile(self):
        ezo = EZO(self.app.config["ezo"])

        self.app.log.info("compiling")

        for filename in self.app.pargs.extra_args:
            print("compiling contracts")

            filename = get_contract_path(self.app.config, filename)
            contracts_source, err = Contract.load(filename)
            if err:
                print("error loading contracts file: {}".format(err))
                exit(1)

            contracts, err = Contract.compile(contracts_source, ezo)
            if err:
                print("error compiling contracts source: {}".format(err))
                exit(1)

            # persist the compiled contract
            for contract in contracts:
                contract.source = contracts_source
                iid, err = contract.save()
                if err:
                    print("error while persisting Contract to datastore: {}".format(err))
                    exit(2)
                else:
                    print("id saved: {}".format(iid))

            exit(0)



    @expose(help="deploy smart contracts")
    def deploy(self):
        ezo = EZO(self.app.config["ezo"])
        self.app.log.info("deploying")

        if not self.app.pargs.target:
            print("target stage must be set with the -t option before deploying")
            exit(2)
        ezo.target = self.app.pargs.target
        _, err = ezo.dial()
        if err:
            exit("error with web3 node: {}".format(err))
        for h in self.app.pargs.extra_args:

            print("deploying contract {} to {}".format(h, ezo.target))

            _, err = ezo.dial()
            if err:
                print("dial error: {}".format(err))
                exit(1)

            # get the compiled contract proxy by it's source hash
            c, err = Contract.create_from_hash(h, ezo)
            if err:
                print("error loading contract from storage: {}".format(err))
                exit(1)

            # deploy the contract
            addr, err = c.deploy()
            if err:
                print("error deploying contract {} to {}".format(c.hash, ezo.target))
                print("message: {}".format(err))
                exit(1)
            print("deployed contract {} named {} to stage '{}' at address {}".format(c.hash, c.name, ezo.target, addr))
            exit(0)


    @expose(help="view contracts and deployments")
    def view(self):
        self.app.log.info("view contracts/deployments")

    @expose(help="delete contracts or deployments")
    def delete(self):
        self.app.log.info("delete contracts/deployments")

    @expose(help="start oracle")
    def start(self):
        self.app.log.info("starting ezo")
        ezo = EZO(self.app.config["ezo"])
        if not self.app.pargs.target:
            print("target must be set with the -t option before deploying")
            exit(2)
        ezo.target = self.app.pargs.target
        _, err = ezo.dial()
        if err:
            print("error with web3 node: {}".format(err))
            exit(1)

        if not self.app.pargs.extra_args:
            print("missing contract hash.")
            print("correct syntax is: start <contract_hash1>, [contract_hash2]...[contract_hash_n]")
            exit(1)

        res, err = ezo.start(self.app.pargs.extra_args)
        if err:
            print("error: {}".format(err))
        else:
            print("result: {}".format(res))


class EZOApp(CementApp):
    class Meta:
        label = "ezo"
        base_controller = "base"
        extensions = ['json_configobj']
        config_handler = 'json_configobj'
        config_files = ['~/PycharmProjects/ezo/config.json']
        handlers = [EZOBaseController]

with EZOApp() as app:
    app.run()
