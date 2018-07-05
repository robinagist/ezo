from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose


class ABCIBaseController(CementBaseController):
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

    @expose(help="")
    def default(self):
        pass

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



class ABCIApp(CementApp):
    ezo = None

    class Meta:
        label = "ezo"
        base_controller = "base"
        extensions = ['json_configobj', 'mustache']
        config_handler = 'json_configobj'
        config_files = ['ezo.conf']

        handlers = [
            ABCIBaseController
        ]
        output_handler = 'mustache'