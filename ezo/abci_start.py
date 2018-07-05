
# starts the Ezo ABCI server which talks to Tendermint

from core.tm_utils import EzoABCI
from cli.abci_cli import ABCIApp
from abci import (
    ABCIServer
)

def main():
    app = ABCIServer(app=EzoABCI())
    app.run()

if __name__ == '__main__':
    main()


