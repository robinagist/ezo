
import pytest
import json
from core import views
from core.lib import EZO



def config():
    with open("testezo.conf", "r") as conf:
        k = json.load(conf)
    return k["ezo"]

def test_01_get_contracts():
    ezo = EZO(config())
    ks = views.get_contracts(None, ezo)
    assert len(ks) > 0


def test_02_get_deploys():
    ezo = EZO(config())
    ks = views.get_deploys(None, ezo)
    assert len(ks) > 0

