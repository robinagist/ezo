from core.lib import DB
import pytest
import time, shutil


class TestDB:

    db = None
    dbpath = None
    project = None

    @classmethod
    def setup(cls):
        cls.dbpath = "/tmp/ezotest" #{}/".format(int(time.time()))
        cls.project = "pytest"
        cls.db = DB(cls.project, cls.dbpath)

    @classmethod
    def teardown(cls):
        try:
            shutil.rmtree(cls.dbpath)
        except:
            pass


    def test_01_db_save_okay(self):
        key = "hello"
        value = "me"
        ks, err = TestDB.db.save(key, value)
        assert err is None

    def test_02_db_attempt_duplicate_insert(self):
        key = "hello"
        value = "me"
        ks, err = TestDB.db.save(key, value)
        assert err is not None
        assert 'already exists' in err

#    @pytest.mark.skip
    def test_03_db_get_key(self):
        key = "hello"
        ks, err = TestDB.db.get(key)
        assert err is None
        assert ks is not None


    @pytest.mark.skip
    def test_04_db_find_3(self):
        key = "hello2"
        value = "me"
        ks, err = TestDB.db.save(key, value)
        assert err is None
        key = "hello3"
        ks, err = TestDB.db.save(key, value)
        assert err is None
        ks, err = TestDB.db.find("hello")
        assert err is None
        assert len(ks) == 3


