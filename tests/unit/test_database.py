import pytest
from houndiq.database import get_connection

def test_get_connection_requires_database_settings(monkeypatch):
    for setting in (
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ):
        monkeypatch.delenv(setting, raising=False)

    with pytest.raises(
        RuntimeError,
        match="Missing database environment variables",
    ):
        get_connection()