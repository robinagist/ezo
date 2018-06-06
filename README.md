# ezo
# easily create Ethereum oracles

`ezo` makes Ethereum oracle development a snap.  Developed in Python, `ezo` permits compiling and deploying contracts, and generating handler scaffolding that allows the fast development of off-chain data sources which respond to contract events.

Inspired by AWS toolsets, `ezo` allows for multiple deployment targets.  Start out testing with Ganache on your local machine, later move to the test net and then the mainnet, by simply specifying the target at deployment time.

`ezo` is built using Python 3.6, the Cement CLI Framework and Web3.py. Contract and deployment state is maintained in LevelDB.

# this repo is in-progress 

### update (June 05 2018) - now have a minimal application.  We can now create an oracle with a contract and a few commands, including generating handlers for contract events.  Now for some refactoring, creating an installer and writing some documentation.  



## Quick Start example project

### Create the project 
`ezo` creates the initial project directory and starter configuration.

`ezo create <project_name>` 

### Compile the source file
place contract files in the <project_name>/contracts and run

`ezo compile <contract file>`

`ezo` will return a hash of the source file, which will be used as a reference to the compiled source.  If the source changes, then the hash will change.  `ezo` uses this system to keep track of compilations and deployments, so that eth is not wasted on deploying the same contract more than once.  This behavior can be overridden with the `--overwrite` option.

### Deploy Contract
After successfully compiling the contracts, deploy the contract to the network using the source hash from the compile step:

`ezo deploy <contract hash> -t <target>`

The targets are set up in the config.json file.  Out of the box, `test-http` is configured for the Ganache GUI HTTP, `test-ws` is configured for Ganache GUI WebSockets.  As many target nodes can be configured as needed.  Once a contract has been debugged and tested on the test network, it can be deployed by simply changing the deployment target on the command line.

### Generate Handler Scaffold

`ezo gen <contract hash>`

View Contracts

`ezo view contracts`

View Deployments

`ezo view deployments`

Start ezo

`ezo start`
