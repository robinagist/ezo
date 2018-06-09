VERSION = '0.0.1'
BANNER = '''
ezo - easy Ethereum oracle builder v%s
(c) 2018 - Robin A. Gist - All Rights Reserved
released under the MIT license
use at your own risk
''' % VERSION


from cement.core.exc import FrameworkError, CaughtSignal
from core.lib import EZO
from cli.ezo_cli import EZOApp


def main():
    with EZOApp() as app:
        app.ezo = EZO(app.config["ezo"])
        EZO.log = app.log
        try:
            app.run()

        except CaughtSignal as e:
            # determine what the signal is, and do something with it?
            from signal import SIGINT, SIGABRT

            if e.signum == SIGINT:
                # do something... maybe change the exit code?
                print("exiting...1")
                app.exit_code = 110
            elif e.signum == SIGABRT:
                # do something else...
                print("exiting...")
                app.exit_code = 111

        except FrameworkError as e:
            # do something when a framework error happens
            print("FrameworkError => %s" % e)

            # and maybe set the exit code to something unique as well
            app.exit_code = 300

        finally:
            # Maybe we want to see a full-stack trace for the above
            # exceptions, but only if --debug was passed?
            if app.debug:
                import traceback
                traceback.print_exc()


if __name__ == '__main__':
    main()
