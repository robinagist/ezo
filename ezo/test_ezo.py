from cement.utils import test
from cli.ezo_cli import EZOApp
from core.lib import EZO
from io import StringIO
import pytest, unittest2


import cement.ext.ext_logging as logging

class EZOTestApp(EZOApp):
    class Meta:
        argv = []
        config_files = []


class EZOTestCase(unittest2.TestCase):

# class EZOTestCase(test.CementTestCase):
    app_class = EZOTestApp


    def setUp(self):
        super(EZOTestCase, self).setUp()
        self.app = EZOApp(argv=[], config_files=['testezo.conf'])


    def test_a_ezo_default(self):
        with self.app as app:
            self.app.ezo = EZO(self.app.config["ezo"])
            app.run()

    def test_b_ezo_deploy(self):
        import sys
        with EZOTestApp(argv=['view', 'deploys']) as app:
            old_stdout = sys.stdout
            app.ezo = EZO(app.config["ezo"])
            result = StringIO()
            sys.stdout = result
            app.run()
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            assert 'deploy' in output


    def test_c_ezo_view_contracts(self):
        import sys
        with EZOTestApp(argv=['view', 'contracts']) as app:
            old_stdout = sys.stdout
            app.ezo = EZO(app.config["ezo"])
            result = StringIO()
            sys.stdout = result
            app.run()
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            assert 'contract' in output


    @pytest.mark.capsys
    def test_d_ezo_compile_contract(self):
        import sys
        with EZOTestApp(argv=['compile', 'time_oracle.sol', '--overwrite'], config_files=['testezo.conf']) as app:
            out, err = capsys.readouterr()
            app.ezo = EZO(app.config["ezo"])
            result = StringIO()
            sys.stderr = result
            app.run()
            output = sys.stderr.getvalue()
 #           sys.stderr = old_stdout
 #           assert 'contract' in output



    def test_e_ezo_deploy_contract(self):
        import sys
        with EZOTestApp(argv=['deploy', 'TimestampRequestOracle', '-t', 'test', "--overwrite"], config_files=['testezo.conf']) as app:
            old_stdout = sys.stderr
            app.ezo = EZO(app.config["ezo"])
            result = StringIO()
            sys.stderr = result
            app.run()
            output = sys.stderr.getvalue()
            sys.stderr = old_stdout
#            assert 'contract' in output
