# ezo
# easily create Ethereum oracles

ezo makes Ethereum oracle development a snap.  Developed in Python, ezo permits compiling and deploying contracts, and generating handler scaffolding that allows the fast development of off-chain data sources which respond to contract events.

ezo allows for multiple deployment stages (or targets).  Start out testing with Ganache on your local machine, later move to the test net and then the mainnet, by simply specifying the stage at deployment time.

Compiled contract and deployment state is currently maintained in Mongo.

# this repo is in-progress - check back daily for updates and refactors ###

Initial Installation
`ezo create` 

Compile Contract
`ezo compile <contract file>`

Deploy Contract
`ezo deploy <contract hash> -s <stage>`

Generate Handler Scaffold
`ezo gen <contract hash>`

View Contracts
`ezo view contracts`

View Deployments
`ezo view deployments`

Start ezo
`ezo start`
