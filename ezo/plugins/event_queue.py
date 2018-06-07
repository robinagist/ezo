from cement.core.controller import CementBaseController, expose

class EZOEventQueuePluginController(CementBaseController):
    class Meta:
        label = "event_queue"
        description = "the default event queue plugin for ezo"
        stacked_on = "base"

        config_defaults = dict(

        )

        arguments = [
            (['--flush'],
             dict(action='store_true', help='flushes all events persisted in the queue'))
        ]

        @expose(help="default")
        def default(self):
            pass



def load(app):
    app.handler.register(EZOEventQueuePluginController)