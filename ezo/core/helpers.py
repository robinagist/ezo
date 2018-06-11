import xxhash


# returns the url for the stage
def get_url(config, target):
    cfg = config["target"][target]
    return cfg["url"]


# returns the account address for the stage
def get_account(config, target):
    cfg = config["target"][target]
    return cfg["account"]


# returns the database file location
def get_db_url(config):
    return config["database"]["url"]


# returns the base directory for contacts
def get_contract_path(config, filename=None):
    if filename:
        return "{}/{}".format(config["ezo"]["contract-dir"], filename)
    return config["ezo"]["contract-dir"]

# returns a full path to the handler directory
def get_handler_path(config, contract_name=None):
    if contract_name:
        return "{}/{}".format(config["handlers-dir"], contract_name)
    return config["ezo"]["handlers-dir"]


# returns an xxhash of the passed string
def get_hash(str):
    bs = bytes(str, 'utf-8')
    return xxhash.xxh64(bs).hexdigest()

# returns the sha3 topic for the event method
'''
 {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "name": "rtemp",
        "type": "uint256"
      }
    ],
    "name": "FilledRequest",
    "type": "event"
  }
'''
def get_topic_sha3(event_block):
    '''
    takes an event block and returns a signature for sha3 hashing
    :param event_block:
    :return:
    '''

    sig = ""
    sig += event_block["name"]
    sig += "("

    for input in event_block["inputs"]:
        sig += input["type"]
        sig += ","
    sig = sig[:-1]
    sig += ")"

    return sig


def display_deployment_rows(rows):
    for row in rows:
        print("{} - {} - {} - {} - {}".format(row["contact-name"], row["hash"], row["address"], row["target"], row["timestamp"]))
    print("total deployments: {}".format(len(rows)))


def display_contract_rows(rows):
    for row in rows:
        print("{} - {} - {}".format(row['name'], row['hash'], row['timestamp']))
    print("total contracts: {}".format(len(rows)))


### text tools

def red(str):
    return("{}{}{}".format('\033[31m', str, '\033[39m'))

def green(str):
    return("{}{}{}".format('\033[32m', str, '\033[39m'))

def yellow(str):
    return("{}{}{}".format('\033[33m', str, '\033[39m'))

def blue(str):
    return("{}{}{}".format('\033[34m', str, '\033[39m'))

def magenta(str):
    return("{}{}{}".format('\033[35m', str, '\033[39m'))

def cyan(str):
    return("{}{}{}".format('\033[36m', str, '\033[39m'))

def white(str):
    return("{}{}{}".format('\033[37m', str, '\033[39m'))

def reset(str):
    return("{}{}".format('\033[0m', str))

def bright(str):
    return("{}{}".format('\033[1m', str))

def normal(str):
    return("{}{}".format('\033[1m', str))
