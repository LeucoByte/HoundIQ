from houndiq.database import get_connection

def test_database_is_available_and_schema_is_initialized():
    with get_connection() as connection:
        result = connection.execute("SELECT 1").fetchone()

        rows = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        ).fetchall()

    tables = {row[0] for row in rows}

    assert result == (1,)
    assert {
        "meetings",
        "races",
        "greyhounds",
        "race_participations",
    }.issubset(tables)