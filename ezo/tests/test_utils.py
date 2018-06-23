
import pytest
from core.utils import gen_event_handler_code, \
    create_sample_contracts_1, \
    create_sample_contracts_2, \
    create_blank_config_obj


def test_01_generate_event_handler_code():
    event_name = "big_old_test_event_1"
    ks = gen_event_handler_code(event_name)
    assert event_name in ks
    assert 'def handler' in ks
    assert 'blaouasdfoi' not in ks


def test_02_create_sample_contract_1():
    ks = create_sample_contracts_1()
    assert "event" in ks
    assert "contract" in ks
    assert "TempRequest" in ks
    assert "basdf9uadfs" not in ks


def test_03_create_sample_contract_2():
    ks = create_sample_contracts_2()
    assert "event" in ks
    assert "contract" in ks
    assert "getTimestamp" in ks
    assert "basdf9uadfs" not in ks


def test_04_create_blank_config_obj():
    ks = create_blank_config_obj()
    assert "ezo" in ks

