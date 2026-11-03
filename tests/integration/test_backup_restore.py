import os
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest

from houndiq.database import get_connection
from houndiq.queries import get_greyhound, get_race


ROOT = Path(__file__).resolve().parents[2]
BACKUP_SCRIPT = ROOT / "scripts" / "backup.sh"
RESTORE_SCRIPT = ROOT / "scripts" / "restore.sh"

TABLES = {
    "meetings": "records.meeting_id",
    "races": "records.race_id",
    "greyhounds": "records.dog_id",
    "race_participations": "records.race_id, records.dog_id",
}


def _run(command):
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
    )


def _snapshot(connection):
    table_data = {}

    for table, ordering in TABLES.items():
        table_data[table] = connection.execute(
            f"""
            SELECT
                COUNT(*),
                COALESCE(
                    md5(
                        string_agg(
                            md5(row_to_json(records)::text),
                            '' ORDER BY {ordering}
                        )
                    ),
                    md5('')
                )
            FROM {table} AS records
            """
        ).fetchone()

    columns = connection.execute(
        """
        SELECT
            table_name,
            column_name,
            ordinal_position,
            data_type,
            udt_name,
            is_nullable,
            COALESCE(column_default, '')
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """
    ).fetchall()

    constraints = connection.execute(
        """
        SELECT
            conrelid::regclass::text,
            conname,
            contype::text,
            pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE connamespace = 'public'::regnamespace
        ORDER BY conrelid::regclass::text, conname
        """
    ).fetchall()

    indexes = connection.execute(
        """
        SELECT tablename, indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
        """
    ).fetchall()

    integrity = connection.execute(
        """
        SELECT
            (
                SELECT COUNT(*)
                FROM races r
                LEFT JOIN meetings m ON m.meeting_id = r.meeting_id
                WHERE m.meeting_id IS NULL
            ),
            (
                SELECT COUNT(*)
                FROM race_participations rp
                LEFT JOIN races r ON r.race_id = rp.race_id
                WHERE r.race_id IS NULL
            ),
            (
                SELECT COUNT(*)
                FROM race_participations rp
                LEFT JOIN greyhounds g ON g.dog_id = rp.dog_id
                WHERE g.dog_id IS NULL
            )
        """
    ).fetchone()

    return {
        "tables": table_data,
        "columns": columns,
        "constraints": constraints,
        "indexes": indexes,
        "integrity": integrity,
    }


def _verify_queries(connection):
    reference = connection.execute(
        """
        SELECT r.meeting_id, r.race_id, MIN(rp.dog_id), COUNT(*)
        FROM races r
        JOIN meetings m ON m.meeting_id = r.meeting_id
        JOIN race_participations rp ON rp.race_id = r.race_id
        GROUP BY r.meeting_id, r.race_id, m.meeting_date
        ORDER BY m.meeting_date DESC NULLS LAST, r.race_id DESC
        LIMIT 1
        """
    ).fetchone()

    assert reference is not None

    meeting_id, race_id, dog_id, participant_count = reference

    race = get_race(connection, meeting_id, race_id)

    assert race is not None
    assert race["meeting"]["meeting_id"] == meeting_id
    assert race["race"]["race_id"] == race_id
    assert len(race["participants"]) == participant_count

    for item in race["participants"]:
        assert item["participation"]["race_id"] == race_id
        assert (
            item["participation"]["dog_id"]
            == item["greyhound"]["dog_id"]
        )

    greyhound = get_greyhound(connection, dog_id)

    assert greyhound is not None
    assert greyhound["greyhound"]["dog_id"] == dog_id
    assert any(
        item["race"]["race_id"] == race_id
        for item in greyhound["history"]
    )

    assert get_greyhound(connection, -1) is None
    assert get_race(connection, meeting_id, -1) is None


def test_database_backup_and_restore(tmp_path, monkeypatch):
    source_database = os.environ["POSTGRES_DB"]
    backup_file = tmp_path / "backup.dump"
    restore_database = f"houndiq_test_restore_{uuid4().hex[:12]}"

    monkeypatch.setenv("POSTGRES_DB", source_database)

    with get_connection() as connection:
        database_exists = connection.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = %s)",
            (restore_database,),
        ).fetchone()[0]

        assert not database_exists

        original_snapshot = _snapshot(connection)

        assert all(
            count > 0
            for count, _ in original_snapshot["tables"].values()
        )

        assert original_snapshot["integrity"] == (0, 0, 0)

    restore_created = False

    try:
        _run([
            str(BACKUP_SCRIPT),
            "--database",
            source_database,
            "--output",
            str(backup_file),
        ])

        assert backup_file.is_file()
        assert backup_file.stat().st_size > 0

        _run([
            str(RESTORE_SCRIPT),
            str(backup_file),
            restore_database,
        ])

        restore_created = True
        monkeypatch.setenv("POSTGRES_DB", restore_database)

        with get_connection() as connection:
            restored_snapshot = _snapshot(connection)

            assert restored_snapshot == original_snapshot

            _verify_queries(connection)

    finally:
        if restore_created:
            _run([
                "docker",
                "compose",
                "exec",
                "-T",
                "db",
                "sh",
                "-c",
                'dropdb --if-exists -U "$POSTGRES_USER" "$1"',
                "sh",
                restore_database,
            ])

        backup_file.unlink(missing_ok=True)

    assert not backup_file.exists()
