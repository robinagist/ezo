# ezo -- easily create Ethereum oracles

`ezo` makes Ethereum oracle development a snap.  Developed in Python, `ezo` permits compiling and deploying contracts, and generating handler scaffolding that allows the fast development of off-chain data sources which respond to contract events.

Inspired by AWS toolsets, `ezo` allows for multiple deployment targets.  Start out testing with Ganache on your local machine, later move to the test net and then the mainnet, by simply specifying the target at deployment time.

`ezo` is built using `Python 3.6`, the `Cement CLI Framework` and `Web3.py`. Contract and deployment state is maintained in `LevelDB`.

## v 0.2a Features (scheduled for release in mid-June 2018)
+ build oracles from the command line.  removes the tedium from developing oracles and other off-chain contract event responders for Ethereum
+ compile and deploy to multiple networks
+ generates handlers in Python, for easy customization
+ Web3 1.0 compliant using Web3.py
+ soon: local and node-hosted keys
+ compiles Solidity and (soon) Vyper contracts
+ choose between WebSockets or HTTPS
+ built-in Ethereum test client.  Start ezo and bring up a second terminal to run contracts that kick off events.

#### update (June 05 2018) - create an oracle with a contract and a few commands, including generating handlers for contract events.  On schedule for 0.2alpha release in mid June


### Install (coming mid June 2018)

0.  Install dependencies:  `Python 3.6` and `LevelDB`.  `Virtualenv` is also highly recommended for `ezo`.
1.  (pip install coming soon)
2.  


### Quick Start

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


### View Contracts

To view contracts after compilation:

`ezo view contracts`

Look for a contract by name or partial name:

`ezo view contracts Weather`
`ezo view contracts WeatherOracle`


### View Deployments

To see current deployments

`ezo view deploys`


### Start ezo
Start ezo by typing

`ezo start <contract name>` -t <target>
  
 ezo will begin listening for events.  The handlers will print the output of events as received.  


### Run contracts to trigger events with the built-in test client

No more having to wrestle with Javascript to test your event responders.  Start ezo, and open another terminal window, and tse the ezo command line to send a test transaction.  For example, run:

`ezo send tx WeatherOracle request [] -t test`

To send a transaction with no parameters to the contract's `request` method on the test network.  This emits an event that the WeatherOracle running under ezo will pick up, and respond. 

![ezo built in test client makes event testing easy](https://user-images.githubusercontent.com/1685659/41264445-9b445b80-6da1-11e8-80f6-2e64fbc4e69f.png)

To call a method, without changing the state of the chain, use the `send call` command
`ezo send call WeatherOracle fill [55] -t test`

Useful for checking values after transactions.
