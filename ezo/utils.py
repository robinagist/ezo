import json, os


# sets up the current directory for an ezoracle project
def initialize():
    # copy the config.json template to the current directory
    # load the config.json template
    # create the default directories
    pass


# load configuration file
def load_configuration(configfile):
    print("CONFIG {}".format(configfile))
    try:
        with open(configfile) as config:
            cfg = json.load(config)
            config.close()
            return cfg
    except Exception as err:
        print("exception: {}".format(err))


# returns the url for the stage
def get_url(config, stage):
    cfg = config["stage"][stage]
    return cfg["url"]


# returns the account address for the stage
def get_account(config, stage):
    cfg = config["stage"][stage]
    return cfg["account"]