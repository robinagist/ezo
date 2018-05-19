import json, os

# sets up the current directory for an ezoracle project
def initialize(noexamples):
    # copy the config.json template to the current directory
    # load the config.json template
    # create the default directories
    pass

# load configuration file
def load_configuration(configfile):
    # if not a pathname
#    if "/" not in configfile:
#        configfile = "{}/{}".format(os.getcwd(), configfile)
    print("CONFIG {}".format(configfile))
    try:
        with open(configfile) as config:
            cfg = json.load(config)
            config.close()
            return cfg
    except Exception as err:
        print("exception: {}".format(err))