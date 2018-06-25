
from cli.ezo_cli import EZOApp
from core.lib import EZO
import pytest

'''
Ezo full integration test
'''

class EZOTestApp(EZOApp):
    class Meta:
        argv = []
        config_files = []


### compiles and deploys

def test_01_ezo_compile_contract(capsys):
    with EZOTestApp(argv=['compile', 'time_oracle.sol', '--overwrite'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'CONTRACT' in err

def test_01a_ezo_compile_contract_no_overwrite_with_error(capsys):
    with EZOTestApp(argv=['compile', 'time_oracle.sol'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'already exists' in err
        assert 'error while persisting Contract to datastore' in err


def test_01a_ezo_compile_contract_no_contract_by_filename_with_error(capsys):
    with EZOTestApp(argv=['compile', 'throatwobbler_mangrove.sol'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'No such file or directory' in err


def test_02_ezo_deploy_contract_no_overwrite_with_error(capsys):
    with EZOTestApp(argv=['deploy', 'TimestampRequestOracle', '-t', 'test'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'deployment on test already exists for contract ' in err


def test_02a_ezo_deploy_bad_contract_name_with_error(capsys):
    with EZOTestApp(argv=['deploy', 'BadContractNameLtd', '-t', 'test'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'not found -- has it been compiled' in err


def test_02b_ezo_deploy_contract_missing_target_with_error(capsys):
    with EZOTestApp(argv=['deploy', 'BadContractNameLtd'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'target must be set with the -t option before deploying' in err


def test_02c_ezo_deploy_contract_missing_target_with_error(capsys):
    with EZOTestApp(argv=['deploy', 'BadContractNameLtd', '-t', 'test'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'not found -- has it been compiled?' in err


@pytest.mark.skip
def test_02c_ezo_deploy_contract_bad_target_name_with_error(capsys):
    with EZOTestApp(argv=['deploy', 'BadContractNameLtd', '-t', 'veryNaughtTargetName'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert '' in err



### views and files

def test_f_ezo_deploy(capsys):
    with EZOTestApp(argv=['view', 'deploys'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'deploy' in out


def test_g_ezo_view_contracts(capsys):
    with EZOTestApp(argv=['view', 'contracts'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'contract' in out


### missing commands tests

def test_g_ezo_view_missing_command(capsys):
    with EZOTestApp(argv=['view'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'Ezo needs more words to work' in out


def test_g_ezo_create_missing_command(capsys):
    with EZOTestApp(argv=['create'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'Ezo needs more words to work' in out


def test_g_ezo_create_gibberish_command(capsys):
    with EZOTestApp(argv=['create', 'bigdufus'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'Ezo needs more words to work' in out


def test_g_ezo_send_missing_command(capsys):
    with EZOTestApp(argv=['send'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'Ezo needs more words to work' in out


def test_g_ezo_send_tx_missing_target_and_missing_params(capsys):
    with EZOTestApp(argv=['send', 'tx'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'target must be set with the -t option before deploying' in err


def test_g_ezo_send_tx_missing_params(capsys):
    with EZOTestApp(argv=['send', 'tx', '-t', 'test'], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'missing parameters for send tx' in err


def test_g_ezo_missing_command(capsys):
    with EZOTestApp(argv=[], config_files=['testezo.conf']) as app:
        app.ezo = EZO(app.config["ezo"])
        app.run()
        out, err = capsys.readouterr()
        assert 'Ezo needs more words to work' in out

