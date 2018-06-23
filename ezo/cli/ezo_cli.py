VERSION = '0.0.1'
BANNER = '''
ezo - easy Ethereum oracle builder v%s
(c) 2018 - Robin A. Gist - All Rights Reserved
released under the MIT license
use at your own risk
''' % VERSION

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from core.lib import Contract, EZO
from core.helpers import get_contract_path, red, green, cyan, yellow, blue, bright, reset
from core.utils import create_ethereum_account, Source
from core.views import get_contracts, view_contracts, get_deploys, view_deploys
import os


class EZOBaseController(CementBaseController):
    '''
    base controller for ezo
    '''
    class Meta:
        label = 'base'
        description = 'ezo - easy Ethereum oracles'
        arguments = [
            (['-t', '--target'],
             dict(action='store', help='deployment target node set in configuration')),
            (['--overwrite'],
             dict(action='store_true', help="force overwriting of existing record (contract, deployment)")),
            (['-p', '--password'],
             dict(action='store', help='password to unlock local node account')),
            (['extra_args'],
             dict(action='store', nargs='*'))
        ]

    @expose(help="compile smart contracts")
    def compile(self):
        ezo = self.app.ezo
        log = self.app.log

        for filename in self.app.pargs.extra_args:
            log.info(cyan("compiling contracts in {}".format(filename)))

            filename = get_contract_path(self.app.config["ezo"], filename)
            contracts_source, err = Contract.load(filename)
            if err:
                log.error(red("error loading contracts file: {}".format(err)))
                return err

            contracts, err = Contract.compile(contracts_source, ezo)
            if err:
                log.error(red("error compiling contracts source: {}".format(err)))
                return err

            # persist the compiled contract
            for contract in contracts:
                contract.source = contracts_source
                iid, err = contract.save(overwrite=self.app.pargs.overwrite)
                if err:
                    log.error(red("error while persisting Contract to datastore: {}".format(err)))
                    return err
                else:
                    log.info(cyan("contract saved: {}".format(iid)))
                    print("pytest>>CONTRACT_SAVED")
            return

    @expose(help="deploy smart contracts")
    def deploy(self):

        ezo = self.app.ezo
        log = self.app.log
        args = self.app.pargs

        # inject password into the environment
        if args.password:
            os.environ["EZO_PASSWORD"] = args.password

        log.debug("deploying...")

        if not args.target:
            log.error(red("target must be set with the -t option before deploying"))
            return

        ezo.target = args.target

        _, err = ezo.dial()
        if err:
            log.error(red("unable to dial node"))
            log.error(red("error: {}".format(err)))
            return

        for h in args.extra_args:
            log.info(cyan("deploying contract {} to {}".format(h, ezo.target)))

            # get the compiled contract by it's Contract Name
            c, err = Contract.get(h, ezo)
            if err:
                log.error(red("error loading contract from storage: {}".format(err)))
                return
            if not c:
                log.error(red("contract '{}' not found -- has it been compiled?").format((h)))
                return

            # deploy the contract
            addr, err = c.deploy(overwrite=self.app.pargs.overwrite)
            if err:
                log.error(red("error deploying contract {} to {}".format(c.hash, ezo.target)))
                log.error(red("message: {}".format(err)))
                return
            print("pytest>>DEPLOYED CONTRACT")
            log.info(cyan("successfully deployed contract {} named {} to stage '{}' at address {}".format(c.hash, c.name, ezo.target, addr)))

        return


    @expose(help="delete contracts or deployments")
    def delete(self):
        self.app.log.info("delete contracts/deployments")


    @expose(help="start ezo")
    def start(self):

        log = self.app.log
        ezo = self.app.ezo
        args = self.app.pargs

        # inject password into the environment
        if args.password:
            os.environ["EZO_PASSWORD"] = args.password


        log.debug("starting ezo")
        if not args.target:
            log.error("target must be set with the -t option before deploying")
            return
        ezo.target = args.target
        _, err = ezo.dial()
        if err:
            log.error(red("error with node: {}".format(err)))
            return err

        if not args.extra_args:
            log.error(red("error: missing contract name"))
            return

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

        # set the Source template directory from config
        Source.templates_dir = ezo.config["templates-dir"]

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
        return


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
             dict(action='store', nargs="?"))
        ]

    @expose(help="view contracts")
    def contracts(self):

        ezo = self.app.ezo
        log = self.app.log
        res, err = get_contracts(self.app.pargs.term, ezo)
        if err:
            log.error(red("error viewing contracts"))
            log.error(red(err))
            return err

        v = view_contracts(res)
        print()
        print(bright(blue("+-------+")))
        for vs in v:
            print(yellow(vs))
        print(blue("+------------+"))
        print(yellow("ezo contracts: {}".format(len(res))))
        print(reset(""))
        return

    @expose(help="view deploys")
    def deploys(self):
        ezo = self.app.ezo
        log = self.app.log
        res, err = get_deploys(self.app.pargs.term, ezo)
        if err:
            log.error(red("error viewing deployments"))
            log.error(red(err))
            return err
        v = view_deploys(res)
        print()
        print(bright(blue("+-------+")))
        for vs in v:
            print(yellow(vs))
        print(blue("+--------------+"))
        print(yellow("ezo deployments: {}".format(bright(len(res)))))
        print(reset(""))
        return len(res)


class EZOCreateController(CementBaseController):
    '''
    parent controller for all things to be created, such as accounts and projects
    '''
    class Meta:
        label = "create"
        stacked_on = "base"
        stacked_type = "nested"
        description = "create projects"
        arguments = [
            (['term'],
             dict(action='store', nargs='?'))
        ]

    @expose(help="generate a new local Ethereum account")
    def account(self):
        create_ethereum_account()


    @expose(help="the first step in every ezo project")
    def project(self):
        ezo = self.app.ezo
        # set the Source template directory from config
        Source.templates_dir = ezo.config["templates-dir"]
        res, err = EZO.create_project(self.app.pargs.term)
        if err:
            print(err)
            return err
        print(bright(blue("new ezo project '{}' created".format(self.app.pargs.term))))
        print(reset(""))
        return


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
             dict(action='store', help='deployment target node (set in configuration')),
            (['-p', '--password'],
             dict(action='store', help='password to unlock local node account'))
        ]

    @expose(help="run a transaction (state change) on the named Contract method")
    def tx(self):
        params = self.app.pargs.c_args
        ezo = self.app.ezo
        args = self.app.pargs
        log = self.app.log

        # inject password into the environment
        if args.password:
            os.environ["EZO_PASSWORD"] = args.password

        if not args.target:
            log.error("target must be set with the -t option before deploying")
            return
        ezo.target = args.target

        _, err = ezo.dial()
        if err:
            log.error(red("error with node: {}".format(err)))
            return err

        if len(params) != 3:
            self.app.log.error(red("missing parameters for send tx - 3 required"))
            return


        name = params[0]
        method = params[1]
        data = params[2]

        resp, err = Contract.send(ezo, name, method, data)
        if err:
            self.app.log.error(red("tx error: {}".format(err)))
            return err

        self.app.log.info(bright(blue("==============")))
        for k, v in resp.items():
            self.app.log.info("{}: {}".format(yellow(k), cyan(v)))
        self.app.log.info(blue("=============="))
        self.app.log.info(reset(""))


    @expose(help="call a method on the local node without changing the blockchain state")
    def call(self):
        params = self.app.pargs.c_args
        ezo = self.app.ezo
        args = self.app.pargs
        log = self.app.log

        if not args.target:
            log.error("target must be set with the -t option before deploying")
            return
        ezo.target = args.target

        _, err = ezo.dial()
        if err:
            log.error(red("error with node: {}".format(err)))
            return

        if len(params) != 3:
            self.app.log.error(red("missing parameters for send tx - 3 required"))
            return

        name = params[0]
        method = params[1]
        data = params[2]

        resp, err = Contract.call(ezo, name, method, data)

        if err:
            self.app.log.error(red("call error: {}".format(err)))
            return

        self.app.log.info(blue("call response: {}".format(yellow(resp))))
        return



class EZOApp(CementApp):
    ezo = None
    class Meta:
        label = "ezo"
        base_controller = "base"
        extensions = ['json_configobj', 'mustache']
        config_handler = 'json_configobj'
        config_files = ['ezo.conf']
        template_module = 'ezo.templates'

        handlers = [
                    EZOBaseController,
                    EZOGeneratorController,
                    EZOViewController,
                    EZOCreateController,
                    EZOTestClientController
                    ]
        output_handler = 'mustache'
