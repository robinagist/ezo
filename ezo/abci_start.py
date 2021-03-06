from cement.core.exc import FrameworkError, CaughtSignal
from cli.abci_cli import ABCIApp
from core.helpers import reset

# starts the Ezo ABCI server which talks to Tendermint


def main():
    with ABCIApp() as app:
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
            # reset terminal
            print(reset(""))

            # Maybe we want to see a full-stack trace for the above
            # exceptions, but only if --debug was passed?
            if app.debug:
                import traceback
                traceback.print_exc()


if __name__ == '__main__':
    main()



