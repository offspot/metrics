from backend.constants import BackendConf


def test_db_api():
    assert BackendConf.database_url.startswith("sqlite+aiosqlite:///")
