# ezo -- easily create Ethereum oracles

`ezo` makes Ethereum oracle development a snap.  Developed in Python, `ezo` permits compiling and deploying contracts, and generating handler scaffolding that allows the fast development of off-chain data sources which respond to contract events.

Inspired by AWS toolsets, `ezo` allows for multiple deployment targets.  Start out testing with Ganache on your local machine, later move to the test net and then the mainnet, by simply specifying the target at deployment time.

`ezo` is built using `Python 3.6`, the `Cement CLI Framework` and `Web3.py`. Contract and deployment state is maintained in `LevelDB`.

## v 0.2 Features
+ build oracles from the command line.  removes the tedium from developing oracles and other off-chain contract event responders for Ethereum
+ compile and deploy to multiple networks
+ generates handlers in Python, for easy customization
+ Web3 1.0 compliant using Web3.py
+ soon: local and node-hosted keys
+ compiles Solidity and (soon) Vyper contracts
+ choose between WebSockets or HTTPS

#### this repo is in-progress 

#### update (June 05 2018) - now have a minimal application.  We can now create an oracle with a contract and a few commands, including generating handlers for contract events.  Now for some refactoring, creating an installer and writing some documentation.  


## Quick Start

### Create the project 
`ezo` creates the initial project directory and starter configuration.  There are even sample contracts that you can compile, deploy and use immediately.

`ezo create <project_name>` 

### Compile the source file
place contract files in the <project_name>/contracts, or compile one of the sample contracts

`ezo compile <contract file>`

`ezo` will compile the source file (just Solidity at the moment - Vyper coming soon), and save all of the artifacts in LevelDB.

### Generate Handler Scaffold
ezo generates handlers for each event in the contract, and attach the hashed event signatures (topics).  ezo places them in the `~/ezo/handlers` subdirectory of the project, where you can add your logic, define your response and return a reply to the contract.  

`ezo gen <contract name>`

### Deploy Contract
After successfully compiling the contracts, and generating the handlers, it's time deploy the contract to the network using the source hash from the compile step:

`ezo deploy <contract name> -t <target>`

The targets are set up in the config.json file.  Out of the box, `test-http` is configured for the Ganache GUI HTTP, `test-ws` is configured for Ganache GUI WebSockets.  As many target nodes can be configured as needed.  Once a contract has been debugged and tested on the test network, it can be deployed by simply changing the deployment target on the command line.

### Start ezo
Start ezo by typing

`ezo start <contract name>` -t <target>
  
 ezo will begin listening for events.  The handlers will print the output of events as received.  

### View Contracts

`ezo view contracts`

### View Deployments

`ezo view deployments`


