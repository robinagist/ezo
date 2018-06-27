from core.lib import DB
import pytest
import shutil


class TestDB:

    db = None
    dbpath = None
    project = None

    @classmethod
    def setup(cls):
        cls.dbpath = "/tmp/ezotest"
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

    def test_03_db_get_key(self):
        key = "hello"
        ks, err = TestDB.db.get(key)
        assert err is None
        assert ks is not None

    def test_03a_db_get_key_no_value(self):
        key = "FattyMcFatFat"
        ks, err = TestDB.db.get(key)
        assert err is None
        assert ks is None

    def test_03z_db_save_okay(self):
        key = "hello333"
        value = "me"
        ks, err = TestDB.db.save(key, value)
        assert err is None

    @pytest.mark.skip
    def test_04_db_find_3(self):
        key = "hello33"
        value = "me"
        ks, err = TestDB.db.save(key, value)
        assert err is None
        key = "hello3"
        ks, err = TestDB.db.save(key, value)
        assert err is None
        ks, err = TestDB.db.find("hello")
        assert err is None
        assert len(ks) == 3

    def test_05_pkey_good(self):
        a =["this","is","a", "test"]
        a_s = b"this:is:a:test:"
        key = DB.pkey(a)
        assert key == a_s

    def test_05a_pkey_single_element(self):
        a = ["this"]
        a_s = b"this:"
        key = DB.pkey(a)
        assert key == a_s

    def test_06_open_good(self):
        assert not DB.db
        ks, err = TestDB.db.open()
        assert not err
        assert DB.db
        TestDB.db.close()
        assert not DB.db

    def test_06a_fail_open_already_open(self):
        assert not DB.db
        ks, err = TestDB.db.open()
        assert not err
        assert DB.db
        ks, err = TestDB.db.open()
        assert 'LOCK' in err
        TestDB.db.close()
        assert not DB.db

    def test_07a_fail_keypart_not_str_or_dict(self):
        ks, err = TestDB.db.find(dict())
        assert err
        assert "keypart must be a string or byte string" in err