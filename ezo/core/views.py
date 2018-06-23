
from core.lib import EZO, DB
from core.helpers import cyan, red, yellow, bright, blue, magenta
from datetime import datetime



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
            key = key.replace(EZO.CONTRACT + ":", "")
            l.append(bright("contract: {:35s} hash: {:25s} timestamp: {:25s}".
                            format(cyan(key), format(blue(value["hash"])), cyan(value["timestamp"]))))
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
            key = key.replace(EZO.DEPLOYED + ":", "").split(':')
            l.append("contract: {:35s} target: {:20s} hash: {:27s} address: {:35s} timestamp: {:25s}".
                     format(cyan(key[0]), magenta(key[1]), blue(key[2]), blue(value["address"]), cyan(value["timestamp"])))
    return l


def display_deployment_rows(rows):
    for r in rows:
        row = r.value()
        print("contract= {:20s}  hash= {:20s}  addr= {:35s}  target= {:15s}  deployed: {:24s}".format(row["contact-name"], row["hash"], row["address"], row["target"], row["timestamp"]))
    print("total deployments: {}".format(len(rows)))


def display_contract_rows(rows):
    for row in rows:
        print("{0} - {1} - {2}".format(row['name'], row['hash'], row['timestamp']))
    print("total contracts: {}".format(len(rows)))


def event_output(contract, event_name, data):
    ts = datetime.utcnow()
    EZO.log.info(("event: {:25s} contract: {:35s} address {:40s} timestamp: {:25s}").
                 format(yellow(event_name), magenta(contract.name.replace("<stdin>:", "")), blue(data.address), magenta(ts)))



