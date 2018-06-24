import json
from eth_account import Account
from xkcdpass import xkcd_password as xp
from core.helpers import red, cyan, yellow, magenta, blue
import pystache



class Source():
    '''
    Source is a simple source code templating engine.  It uses simple Python
    string formatting methods.

    Set the template directory before using.

    the generate method takes a template file and option data dictionary.
    format will insert the elements in data that match the elements in the template
    '''

    templates_dir = None

    @classmethod
    def generate(cls, template_name, data=None):

        if not cls.templates_dir:
            return None, "Source.templates_dir must be set before generating source"

        template_path = "{}/{}".format(cls.templates_dir, template_name)
        try:
            with open(template_path, "r") as file:
                ks = file.read()
        except FileNotFoundError as e:
            return None, e

        if data:
            try:
                return ks.format(**data), None
            except Exception as e:
                return None, e
        return ks, None

    @classmethod
    def save(cls, file_str, file_path):

        try:
            with open(file_path, "w+") as file:
                file.write(file_str)
        except Exception as e:
            return None, e

        return None, None


def create_ethereum_account():
    ac = Account.create()
    wf = xp.locate_wordfile()
    words= xp.generate_wordlist(wordfile=wf, min_length=5, max_length=8)

    password_str = xp.generate_xkcdpassword(words)
    print(cyan("password string to decrypt private key -- please store in safe location:"))
    print()
    print(yellow(password_str))
    print()
    print(cyan("address:"))
    print(yellow(ac.address))

    ks = json.dumps(Account.encrypt(ac.privateKey, password_str), indent=2)
    print(red(ks))


def gen_event_handler_code(event_name):

    d = dict()
    d["event_name"] = event_name
    ks, err = Source.generate("event_handler.m", d)
    if err:
        return None, err
    return ks, None


def create_blank_config_obj():

    ks, err = Source.generate("ezoconf.m")
    if err:
        return None, err
    return ks, None


def create_sample_contracts_1():

    # WeatherOracle

    ks, err = Source.generate("sample_contract_01.m")
    if err:
        return None, err
    return ks, None


def create_sample_contracts_2():

    #TimestampOracle

    ks, err = Source.generate("sample_contract_02.m")
    if err:
        return None, err
    return ks, None

