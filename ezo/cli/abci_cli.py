from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from core.tm_utils import EzoABCI
from abci import ABCIServer



class ABCIBaseController(CementBaseController):
    '''
    base controller for ezo
    '''
    class Meta:
        label = 'base'
        description = 'ezo runtime'
        '''
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
        '''

    @expose(help="")
    def default(self):
        pass

        ezo = self.app.ezo
        log = self.app.log


    @expose(help="start Ezo ABCI server")
    def start(self):

        log = self.app.log
        args = self.app.pargs

        abci_app = ABCIServer(app=EzoABCI())
        abci_app.run()



class ABCIApp(CementApp):
    ezo = None

    class Meta:
        label = "ezo"
        base_controller = "base"
        extensions = ['json_configobj']
        config_handler = 'json_configobj'
        config_files = ['ezo.conf']

        handlers = [
            ABCIBaseController
        ]
