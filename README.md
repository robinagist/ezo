# ezo 

## the easy oracle development toolset for Python

### now in alpha!

`ezo` makes Ethereum oracle development a snap.  Developed in Python, `ezo` permits compiling and deploying contracts, and generating handler scaffolding that allows the fast development of off-chain data sources which respond to contract events.

Inspired by AWS toolsets, `ezo` allows for multiple deployment targets.  Start out testing with Ganache on your local machine, later move to the test net and then the mainnet, by simply specifying the target at deployment time.

`ezo` is built using `Python 3.6`, the `Cement CLI Framework` and `Web3.py`. Contract and deployment state is maintained in `LevelDB`.

## v 0.1a Features 
+ build oracles from the command line.  removes the tedium from developing oracles and other off-chain contract event responders for Ethereum
+ compile and deploy to multiple networks
+ generates handlers in Python, for easy customization
+ listen for, and respond to multiple events on multiple contracts
+ Web3 1.0 compliant using Web3.py
+ compiles Solidity and (soon) Vyper contracts
+ choose between WebSockets or HTTPS
+ built-in Ethereum test client.  Start ezo and bring up a second terminal to run contracts that kick off events. 
+ asychronous, single-threaded.  no multiprocess witchcraft to deal with.

`The image below shows the built-in ezo test client running against another instance of ezo in oracle mode`

![ezo in action](https://user-images.githubusercontent.com/1685659/41318471-44f8a1f8-6e4d-11e8-8707-441c58d78987.png)

#### NOTE:  Account management and transaction signing in the next alpha release.  The Web3.py middleware layer for signing transactions transparently is still in testing.  In the meantime, use your account addresses with your local node keys, or Ganache keys.  

### Install and Make A Project

To get up fast, the ezo comes preconfigured for running on Ganache GUI.  Use it, and you won't have to mess with configuration right now.  Just use the `test` target (more on that later).

#### First five minutes
0.  Install dependencies:  
    + `Python 3.6`
    + `LevelDB`.  
    + `Virtualenv`
    + `solc` Solidity compiler
1. create Virtualenv and start
2. Install ezo with `pip install ezo`
3. create the ezo project with `ezo create <project name>`.  Put in any name you like.
4. now, compile one of the test Solidity contracts: `ezo compile contract1.sol`
5. The name of the sample contract is `TemperatureOracle`.  
   We'll create the handlers for it, and register to events: `ezo gen handlers TemperatureOracle`
   (if you look in the `handlers` subdirectory, you'll see a `temperature_oracle` directory, containing two Python handlers that
   are ready for code.)
6. Back in the project directory, we want to see our contract.  `ezo view contracts` will show us our contract.
7. With Ganache GUI running on port 7545, we'll deploy our contract.  In `ezo.conf`, Ganache is already configured as
   the `test` target with a default Ganache account, using HTTPS, so we're ready to go.   
   `ezo deploy TemperatureOracle -t test`
8. Let's look at our deployed contract with `ezo view deploys`.  We should see our contract there.
9. ezo is ready to start listening for the two events on the TemperatureOracle:  `ezo start TemperatureOracle -t test`

#### Now, ezo's built-in test client
1. With ezo running, open another terminal window and navigate to the project's base directory
2. start up your Virtualenv environment
3. We're going to send a transaction to the TemperatureOracle's `request` method.  It has no parameters.  However, it fires an
   event that will show up as received by ezo in the oracle terminal:  `ezo send tx TemperatureOracle request [] -t test`
4. You should see an event show up in the other terminal display, while the test client screen should fill up with transaction data.

Now, you can customize the oracle with Python code in just the handler.  There is code to help you quickly wire up event responses.

### Commands and Stuff

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

`ezo start <contract name> -t <target>`
  
 ezo will begin listening for events.  The handlers will print the output of events as received.  


### Run contracts to trigger events with the built-in test client

No more having to wrestle with Javascript to test your event responders.  Start ezo, and open another terminal window, and tse the ezo command line to send a test transaction.  

`ezo send tx <contract name> <method name> [data, items, list] -t <target>`

Supply the contract name, method name, a list of data elements, and the deployment target.

For example, run:

`ezo send tx WeatherOracle request [] -t test`

To send a transaction with no parameters to the contract's `request` method on the test network.  This emits an event that the WeatherOracle running under ezo will pick up, and respond. 

![ezo built in test client makes event testing easy](https://user-images.githubusercontent.com/1685659/41264445-9b445b80-6da1-11e8-80f6-2e64fbc4e69f.png)

To call a method, without changing the state of the chain, use the `send call` command

`ezo send call WeatherOracle fill [55] -t test`

Useful for checking values after transactions.
