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


# returns an xxhash of the passed string
def get_hash(str):
    bs = bytes(str, 'utf-8')
    return xxhash.xxh64(bs).hexdigest()


def display_deployment_rows(rows):
    for row in rows:
        print("{} - {} - {} - {} - {}".format(row["contact-name"], row["hash"], row["address"], row["target"], row["timestamp"]))
    print("total deployments: {}".format(len(rows)))


def display_contract_rows(rows):
    for row in rows:
        print("{} - {} - {}".format(row['name'], row['hash'], row['timestamp']))
    print("total contracts: {}".format(len(rows)))