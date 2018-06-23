
from core import helpers
from core.lib import EZO
import json
import pytest



def config():
    with open("testezo.conf", "r") as conf:
        k = json.load(conf)
    return k["ezo"]

def test_01_get_url():
    target = "test"
    k = helpers.get_url(config(), target)
    assert "http" in k

def test_02_get_account():
    target = "test"
    k = helpers.get_account(config(), target)
    assert "0x" in k

@pytest.mark.skip
def test_03_get_contract_path():
    k = helpers.get_contract_patha(config())
    assert "testfile" in k

def test_04_get_handler_path():
    k = helpers.get_handler_path(config(), "event_handler.py")
    assert "event_handler.py" in k
