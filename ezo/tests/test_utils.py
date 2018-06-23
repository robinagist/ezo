
import pytest, json
from core.utils import gen_event_handler_code, \
    create_sample_contracts_1, \
    create_sample_contracts_2, \
    create_blank_config_obj, Source


def config():
    with open("testezo.conf", "r") as conf:
        k = json.load(conf)
    return k["ezo"]


def test_01_generate_event_handler_code():
    event_name = "big_old_test_event_1"
    cfg = config()
    Source.templates_dir = cfg["templates-dir"]
    ks, _ = gen_event_handler_code(event_name)
    assert event_name in ks
    assert 'def handler' in ks
    assert 'blaouasdfoi' not in ks


def test_02_create_sample_contract_1():
    ks, _ = create_sample_contracts_1()
    cfg = config()
    Source.templates_dir = cfg["templates-dir"]
    assert "event" in ks
    assert "contract" in ks
    assert "TempRequest" in ks
    assert "basdf9uadfs" not in ks


def test_03_create_sample_contract_2():
    ks, _ = create_sample_contracts_2()
    cfg = config()
    Source.templates_dir = cfg["templates-dir"]
    assert "event" in ks
    assert "contract" in ks
    assert "getTimestamp" in ks
    assert "basdf9uadfs" not in ks


def test_04_create_blank_config_obj():
    cfg = config()
    print(cfg)
    Source.templates_dir = cfg["templates-dir"]
    ks, _ = create_blank_config_obj()
    assert "ezo" in ks

