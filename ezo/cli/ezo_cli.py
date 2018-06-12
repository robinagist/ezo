VERSION = '0.0.1'
BANNER = '''
ezo - easy Ethereum oracle builder v%s
(c) 2018 - Robin A. Gist - All Rights Reserved
released under the MIT license
use at your own risk
''' % VERSION

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from core.lib import Contract
from core.helpers import get_contract_path, red, green, cyan, yellow, blue
from core.utils import create_ethereum_account, create_blank_config_obj
from core.views import get_contracts, view_contracts, get_deploys, view_deploys
import json


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

    @expose(help="compile smart contracts")
    def compile(self):
        ezo = self.app.ezo
        log = self.app.log

        for filename in self.app.pargs.extra_args:
            log.info(cyan("compiling contracts in {}".format(filename)))

            filename = get_contract_path(self.app.config, filename)
            contracts_source, err = Contract.load(filename)
            if err:
                log.error(red("error loading contracts file: {}".format(err)))
                exit(1)

            contracts, err = Contract.compile(contracts_source, ezo)
            if err:
                log.error(red("error compiling contracts source: {}".format(err)))
                exit(1)

            # persist the compiled contract
            for contract in contracts:
                contract.source = contracts_source
                iid, err = contract.save(overwrite=self.app.pargs.overwrite)
                if err:
                    log.error(red("error while persisting Contract to datastore: {}".format(err)))
                    exit(2)
                else:
                    log.info(cyan("contract saved: {}".format(iid)))
            exit(0)

    @expose(help="deploy smart contracts")
    def deploy(self):

        ezo = self.app.ezo
        log = self.app.log
        args = self.app.pargs

        log.debug("deploying")

        if not args.target:
            log.error(red("target must be set with the -t option before deploying"))
            exit(1)

        ezo.target = args.target

        _, err = ezo.dial()
        if err:
            log.error(red("unable to dial node"))
            log.error(red("error: {}".format(err)))
            exit(2)

        for h in args.extra_args:
            log.info(cyan("deploying contract {} to {}".format(h, ezo.target)))

            # get the compiled contract by it's Contract Name
            c, err = Contract.get(h, ezo)
            if err:
                log.error(red("error loading contract from storage: {}".format(err)))
                exit(2)
            if not c:
                log.error(red("contract '{}' not found -- has it been compiled?").format((h)))
                exit(1)

            # deploy the contract
            addr, err = c.deploy(overwrite=self.app.pargs.overwrite)
            if err:
                log.error(red("error deploying contract {} to {}".format(c.hash, ezo.target)))
                log.error(red("message: {}".format(err)))
                exit(2)


            log.info(cyan("successfully deployed contract {} named {} to stage '{}' at address {}".format(c.hash, c.name, ezo.target, addr)))

        exit(0)


    @expose(help="delete contracts or deployments")
    def delete(self):
        self.app.log.info("delete contracts/deployments")


    @expose(help="start ezo")
    def start(self):

        log = self.app.log
        ezo = self.app.ezo
        args = self.app.pargs

        log.debug("starting ezo")
        if not args.target:
            log.error("target must be set with the -t option before deploying")
            exit(2)
        ezo.target = args.target
        _, err = ezo.dial()
        if err:
            log.error(red("error with node: {}".format(err)))
            exit(1)

        if not args.extra_args:
            log.error(red("error: missing contract name"))
            exit(1)

        res, err = ezo.start(args.extra_args)
        if err:
            log.error(red("error: {}".format(err)))
        else:
            log.info(cyan("result: {}".format(res)))


class EZOGeneratorController(CementBaseController):
    '''
    parent controller for all things to be generated, such as accounts and code
    '''
    class Meta:
        label = "gen"
        stacked_on = "base"
        stacked_type = "nested"
        description = "generate handler scaffolding"
        arguments = [
            (['--overwrite'],
             dict(action='store_true', help="force overwriting of existing record (contract, deployment)")),
            (['extra_args'],
             dict(action='store', nargs='*'))
        ]

    @expose(help="gen", hide=True)
    def default(self):
        self.app.log.error(red("command must be followed by  'handlers"))

    @expose(help="generate event handlers")
    def handlers(self):
        log = self.app.log
        ezo = self.app.ezo
        args = self.app.pargs

        # go through each contract hash and create handlers
        for h in args.extra_args:
            log.info(cyan("generating any missing event handlers for contract: {}".format(h)))
            c, err = Contract.get(h, ezo)
            if err:
                log.error(red("error getting contract: {}".format(err)))
                continue
            if not c:
                log.error(red("no contract was found for {} - was it compiled?".format(h)))
                continue
            _, err = c.generate_event_handlers(overwrite=args.overwrite)
            if err:
                log.error(red("error generating handlers for {}: {}".format(h, err)))
                continue
            log.info(cyan("handlers for contract {} generated".format(h)))
        exit(0)


class EZOViewController(CementBaseController):
    '''
    parent controller for all things to be generated, such as accounts and code
    '''
    class Meta:
        label = "view"
        stacked_on = "base"
        stacked_type = "nested"
        description = "view contracts and deployments"
        arguments = [
            (['term'],
             dict(action='store', nargs='*'))
        ]

    @expose(help="view contracts")
    def contracts(self):

        ezo = self.app.ezo
        log = self.app.log
        res, err = get_contracts(self.app.pargs.term, ezo)
        if err:
            log.error(red("error viewing contracts"))
            log.error(red(err))
            exit(1)

        v = view_contracts(res)
        print()
        for vs in v:
            print(yellow(vs))
        print()
        print(yellow("ezo contracts: {}".format(len(res))))
        exit(0)

    @expose(help="view deploys")
    def deploys(self):
        ezo = self.app.ezo
        log = self.app.log
        res, err = get_deploys(self.app.pargs.term, ezo)
        if err:
            log.error(red("error viewing deployments"))
            log.error(red(err))
            exit(1)
        v = view_deploys(res)
        print()
        for vs in v:
            print(yellow(vs))
        print()
        print(yellow("ezo deployments: {}".format(len(res))))
        exit(0)


class EZOCreateController(CementBaseController):
    '''
    parent controller for all things to be created, such as accounts and projects
    '''
    class Meta:
        label = "create"
        stacked_on = "base"
        stacked_type = "nested"
        description = "create projects or accounts"
        arguments = [
            (['term'],
             dict(action='store', nargs='*'))
        ]

    @expose(help="generate a new local Ethereum account")
    def account(self):
        create_ethereum_account()


class EZOTestClientController(CementBaseController):
    '''
    a contract test client used to simulate contract users
    '''
    class Meta:
        label = "send"
        stacked_on = "base"
        stacked_type = "nested"
        description = "create projects or accounts"
        arguments = [
            (['c_args'],
             dict(action='store', nargs='*', help="contract arguments to send")),
            (['-t', '--target'],
             dict(action='store', help='deployment target node (set in configuration'))
        ]

    @expose(help="run a transaction (state change) on the named Contract method")
    def tx(self):
        params = self.app.pargs.c_args
        ezo = self.app.ezo
        args = self.app.pargs
        log = self.app.log

        if not args.target:
            log.error("target must be set with the -t option before deploying")
            exit(2)
        ezo.target = args.target

        _, err = ezo.dial()
        if err:
            log.error(red("error with node: {}".format(err)))
            exit(1)

        if len(params) != 3:
            self.app.log.error(red("missing parameters for send tx - 3 required"))
            exit(1)



        name = params[0]
        method = params[1]
        data = params[2]

        resp, err = Contract.send(ezo, name, method, data)

        if err:
            self.app.log.error(red("tx error: {}".format(err)))
        self.app.log.info(blue("=============="))
        for k, v in resp.items():
            self.app.log.info("{}: {}".format(yellow(k), cyan(v)))
        self.app.log.info(blue("=============="))


    @expose(help="call a method on the local node without changing the blockchain state")
    def call(self):
        pass



class EZOApp(CementApp):
    ezo = None
    class Meta:
        label = "ezo"
        base_controller = "base"
        extensions = ['json_configobj']
        config_handler = 'json_configobj'
        config_files = ['ezo.conf']
        handlers = [
                    EZOBaseController,
                    EZOGeneratorController,
                    EZOViewController,
                    EZOCreateController,
                    EZOTestClientController
                    ]
