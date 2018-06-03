VERSION = '0.0.1'
BANNER = '''
ezo - easy Ethereum oracle builder v%s
(c) 2018 - Robin A. Gist - All Rights Reserved
released under the MIT license
use at your own risk
''' % VERSION

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from core.helpers import display_contract_rows, display_deployment_rows
from core.lib import Contract
from core.helpers import get_contract_path
from core.utils import create_ethereum_account


class EZOBaseController(CementBaseController):
    '''
    base controller for ezo
    '''
    class Meta:
        label = 'base'
        description = 'ezo - easy Ethereum oracles'
        arguments = [
            (['-t', '--target'],
             dict(action='store', help='deployment target node (set in configuration')),
            (['--overwrite'],
             dict(action='store_true', help="force overwriting of existing record (contract, deployment)")),
            (['extra_args'],
             dict(action='store', nargs='*'))
        ]

    @expose(help="create a new ezo project in the current director")
    def create(self):
        self.app.log.info("initalizing new project")

    @expose(help="compile smart contracts")
    def compile(self):
        ezo = self.app.ezo
        log = self.app.log

        log.info("compiling")

        for filename in self.app.pargs.extra_args:
            log.info("compiling contracts")

            filename = get_contract_path(self.app.config, filename)
            contracts_source, err = Contract.load(filename)
            if err:
                log.error("error loading contracts file: {}".format(err))
                exit(1)

            contracts, err = Contract.compile(contracts_source, ezo)
            if err:
                log.error("error compiling contracts source: {}".format(err))
                exit(1)

            # persist the compiled contract
            for contract in contracts:
                contract.source = contracts_source
                iid, err = contract.save()
                if err:
                    log.error("error while persisting Contract to datastore: {}".format(err))
                    exit(2)
                else:
                    log.info("id saved: {}".format(iid))
            exit(0)

    @expose(help="deploy smart contracts")
    def deploy(self):

        ezo = self.app.ezo
        log = self.app.log

        log.debug("deploying")

        if not self.app.pargs.target:
            log.error("target must be set with the -t option before deploying")
            exit(1)

        ezo.target = self.app.pargs.target

        _, err = ezo.dial()
        if err:
            log.error("unable to dial web node")
            log.error("error: {}".format(err))
            exit(2)

        for h in self.app.pargs.extra_args:
            log.info("deploying contract {} to {}".format(h, ezo.target))

            # get the compiled contract proxy by it's source hash
            c, err = Contract.create_from_hash(h, ezo)
            if err:
                log.error("error loading contract from storage: {}".format(err))
                exit(2)

            # deploy the contract
            addr, err = c.deploy(overwrite=self.app.pargs.overwrite)
            if err:
                log.error("error deploying contract {} to {}".format(c.hash, ezo.target))
                log.error("message: {}".format(err))
                exit(2)

            log.info("successfully deployed contract {} named {} to stage '{}' at address {}".format(c.hash, c.name, ezo.target, addr))

        exit(0)

    @expose(help="view contracts and deployments")
    def view(self):

        ezo = self.app.ezo
        log = self.app.log

        args = self.app.pargs.extra_args
        if len(args) < 1:
            log.error("missing parameter <deploys|contracts|source>")
            exit(1)

        cmd = args.pop() if args else None
        param = args.pop() if args else "all"
        if cmd == "deploys":
            rows, err = ezo.view_deployments(param)
            if err:
                log.error("view deploys: {}".format(err))
                exit(2)
            display_deployment_rows(rows)

        elif cmd == "contracts":
            rows, err = ezo.view_contracts(param)
            if err:
                log.error("view contracts: {}".format(err))
            display_contract_rows(rows)

        elif cmd == "source":
            ezo.view_source(param)
        else:
            print("follow command with one of <deploys|contracts|source>")
            exit(1)

    @expose(help="delete contracts or deployments")
    def delete(self):
        self.app.log.info("delete contracts/deployments")


    @expose(help="start ezo")
    def start(self):

        log = self.app.log
        ezo = self.app.ezo

        log.debug("starting ezo")
        if not self.app.pargs.target:
            log.error("target must be set with the -t option before deploying")
            exit(2)
        ezo.target = self.app.pargs.target
        _, err = ezo.dial()
        if err:
            log.error("error with web3 node: {}".format(err))
            exit(1)

        if not self.app.pargs.extra_args:
            log.error("missing contract hash.")
            log.error("correct syntax is: start <contract_hash1>, [contract_hash2]...[contract_hash_n]")
            exit(1)

        res, err = ezo.start(self.app.pargs.extra_args)
        if err:
            print("error: {}".format(err))
        else:
            print("result: {}".format(res))


class EZOGeneratorController(CementBaseController):
    '''
    parent controller for all things to be generated, such as accounts and code
    '''
    class Meta:
        label = "gen"
        stacked_on = "base"
        stacked_type = "nested"
        description = "generator controller for handler and accounts"
        arguments = []

    @expose(help="gen", hide=True)
    def default(self):
        print("hey")


class EZOAccountController(CementBaseController):
    '''
    controller to generate and manage accounts
    '''
    class Meta:
        label = "account"
        stacked_on = "gen"
        stacked_type = "nested"
        arguments = []

    @expose(help="generate a new local Ethereum account")
    def default(self):
        create_ethereum_account()


class EZOHandlerController(CementBaseController):
    '''
    controller to generate event handler code
    '''
    class Meta:
        label = "handlers"
        stacked_on = "gen"
        stacked_type = "nested"
        arguments = []

    @expose(help="generate handlers and callback methods")
    def default(self):
        print("handlers")


class EZOApp(CementApp):
    ezo = None
    class Meta:
        label = "ezo"
        base_controller = "base"
        extensions = ['json_configobj']
        config_handler = 'json_configobj'
        config_files = ['~/PycharmProjects/ezo/config.json']
        handlers = [
                    EZOBaseController,
                    EZOGeneratorController,
                    EZOAccountController,
                    EZOHandlerController
                    ]
