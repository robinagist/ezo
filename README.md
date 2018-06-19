# ezo 

## Quickly Build Oracles and Event Responders on Ethereum using Python!
### (13 June 2018) - now in alpha!

![image](https://user-images.githubusercontent.com/1685659/41576787-2a0667cc-733e-11e8-96dd-da56d99e3af3.png)

`ezo` (pronounced `eh-zoh`) makes Ethereum oracle development a snap.  Developed in Python, `ezo` permits compiling and deploying contracts, and generating handler scaffolding that allows the fast development of off-chain data sources which respond to contract events.

Inspired by AWS toolsets, such as Serverless and Gordon, `ezo` allows for multiple deployment targets.  Start out testing with Ganache on your local machine, later move to the test net and then the mainnet, by simply specifying the target at deployment time.

## v 0.1a Features 
+ build oracles from the command line.  removes the tedium from developing oracles and other off-chain contract event responders for Ethereum
+ compile and deploy to multiple networks
+ generates handlers in Python, for easy customization
+ listen for, and respond to multiple events on multiple contracts
+ Web3 1.0 using Web3.py
+ compiles Solidity and (soon) Vyper contracts
+ choose between IPC, WebSockets or HTTPS
+ built-in Ethereum test client.  Start ezo and bring up a second terminal to run contracts that kick off events. 
+ asychronous, single-threaded.  no multiprocess witchcraft to deal with.

![ezo in action](https://user-images.githubusercontent.com/1685659/41318471-44f8a1f8-6e4d-11e8-8707-441c58d78987.png)
##### ezo test client running against another instance of ezo in oracle mode


#### NOTE:  Account management and transaction signing in the next alpha release.  The Web3.py middleware layer for signing transactions transparently is still in testing.  In the meantime, use your account addresses with your local node keys, or Ganache keys.  

### Install and Make A Project!!!

[Build an Ethereum Oracle in 10 Minutes with Ezo and Python](https://medium.com/@robinagist/build-an-ethereum-oracle-in-10-minutes-using-ezo-and-python-80627c3909a7)

To get up fast, the ezo comes preconfigured for running on Ganache GUI.  Use it, and you won't have to mess with configuration right now.  Just use the `test` target (more on that later).

#### ezo -- the first five minutes
0.  Install dependencies:  
    + `Python 3.6`
    + `LevelDB`.  
    + `Virtualenv`
    + `solc` Solidity compiler
1. create Virtualenv and start
2. Install ezo with 

   `pip install ezo`

3. create the ezo project with 

   `ezo create project <project name>`
   
   Put in any name you like.  We'll use `MyEzo`:
   
   `ezo create project MyEzo`

   Then `cd` into the project directory.

4. now, compile one of the test Solidity contracts (contract1.sol and contract2.sol): 

   `ezo compile contract1.sol`

5. The name of the sample contract is `TemperatureOracle`.  
   We'll create the handlers for it, and register to events: 
   
   `ezo gen handlers TemperatureOracle`
   
   (if you look in the `handlers` subdirectory, you'll see a `temperature_oracle` directory, containing two Python handlers that
   are ready for code.)
   
6. Back in the project directory, we want to see our contract.  

   `ezo view contracts` 
   
   will show us our compiled contract.

7. With Ganache GUI running on port 7545, we'll deploy our contract.  In `ezo.conf`, Ganache is already configured as
   the `test` target with a default Ganache account, using HTTPS, so we're ready to go.
   
   `ezo deploy TemperatureOracle --target=test`

8. Let's look at our deployed contract with 

   `ezo view deploys`.  
   
   We should see our contract there.

9. ezo is ready to start listening for the two events on the TemperatureOracle:  

   `ezo start TemperatureOracle --target=test`


#### Now, ezo's built-in test client

1. With ezo running, open another terminal window and navigate to the project's base directory

2. start up Virtualenv

3. We're going to send a transaction to the TemperatureOracle's `request` method.  It has no parameters, so we'll just pass an empty list.  Sending the transaction fires an event that will show up as received in the ezo oracle terminal:  
   
   `ezo send tx TemperatureOracle request [] --target=test`

4. You should see an event show up in the other terminal display, while the test client screen should fill up with transaction data (see image above).

Now, you can customize the oracle with Python code in just the handler.  There is code to help you quickly wire up event responses.

---
Check out the Wiki for more information

#### thank you
`ezo` is built using `Python 3.6`, the `Cement CLI Framework` and `Web3.py`, for use on any `Ethereum` blockchain network. Contract and deployment state is maintained in `LevelDB`.  It makes use of `solc`, the Solidity compiler, and soon the Vyper compiler.  To the folks that built those tools, and to the others who both necessitated the need for things such as `ezo`, and who also provided the pieces of the puzzle that made the project happen:  thank you.  `ezo` is dedicated to you, the open source community.  You move the world forward.


