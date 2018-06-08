
from core.lib import Contract, EZO, DB
from core.helpers import cyan, red, yellow



def get_contracts(term, ezo):
    # build prefix
    st = DB.pkey([EZO.CONTRACT, term]) if term else DB.pkey([EZO.CONTRACT])
    res, err = ezo.db.find(st)
    if err:
        return None, err
    return res, None


def view_contracts(results):
    l = list()
    for res in results:
        for key, value in res.items():
            key = key.replace(EZO.CONTRACT, "")
            l.append("contract: {} - compiled: {}".format(cyan(key), yellow(value["timestamp"])))
    return l


def get_deploys(term, ezo):
    st = DB.pkey([EZO.DEPLOYED, term]) if term else DB.pkey([EZO.DEPLOYED])
    res, err = ezo.db.find(st)
    if err:
        return None, err
    return res, None


def view_deploys(results):
    l = list()
    for res in results:
        for key, value in res.items():
            key = key.replace(EZO.DEPLOYED, "")
            l.append("contract: {} - deployed: {}".format(cyan(key), yellow(value["timestamp"])))
    return l




