from backend.constants import BackendConf


def test_db_api() -> None:
    assert BackendConf.database_url.startswith("sqlite+pysqlite:///")
