
from cli.ezo_cli import EZOApp
from core.lib import EZO
from io import StringIO
import pytest, time


class EZOTestApp(EZOApp):
    class Meta:
        argv = []
        config_files = []


# @pytest.mark.skip
def test_b_ezo_deploy():
    import sys

    with EZOTestApp(argv=['view', 'deploys'], config_files=['testezo.conf']) as app:
        old_stdout = sys.stdout
        app.ezo = EZO(app.config["ezo"])
        result = StringIO()
        sys.stdout = result
        app.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        assert 'deploy' in output


# @pytest.mark.skip
def test_c_ezo_view_contracts():
    import sys

    with EZOTestApp(argv=['view', 'contracts'], config_files=['testezo.conf']) as app:
        old_stdout = sys.stdout
        app.ezo = EZO(app.config["ezo"])
        result = StringIO()
        sys.stdout = result
        app.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        assert 'contract' in output

# @pytest.mark.skip
def test_d_ezo_compile_contract():
    import sys
    with EZOTestApp(argv=['compile', 'time_oracle.sol', '--overwrite'], config_files=['testezo.conf']) as app:
        old_stdout = sys.stdout
        app.ezo = EZO(app.config["ezo"])
        result = StringIO()
        sys.stdout = result
        app.run()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        assert 'CONTRACT' in output


@pytest.mark.skip
def test_e_ezo_deploy_contract():
    import sys

    with EZOTestApp(argv=['deploy', 'TimestampRequestOracle', '-t', 'test', "--overwrite"], config_files=['testezo.conf']) as app:
        old_stdout = sys.stdout
        app.ezo = EZO(app.config["ezo"])
        result = StringIO()
        sys.stdout = result
        app.run()

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        assert 'CONTRACT' in output


