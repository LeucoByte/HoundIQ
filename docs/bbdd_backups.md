## 1. Approach
HoundIQ uses PostgreSQL logical backups through `pg_dump` in custom format.

Backups are independent snapshots containing the database schema and stored data. They are not database migrations or synchronization mechanisms.

The process follows three principles:

- Backups are created explicitly and retained independently of the repository.
- Restoration always targets a new database and never overwrites an existing one.
- Backup and recovery are verified through automated integration tests.

Multiple backups can coexist, allowing different historical database snapshots to be restored and selected independently.

## 2. Backup creation
Run:

```bash
./scripts/backup.sh
```

By default, the script backs up the database configured in .env and stores the archive under:
~/.local/share/houndiq/backups/


A specific source database and output file can be selected:
```bash
./scripts/backup.sh \
    --database houndiq \
    --output "$HOME/.local/share/houndiq/backups/houndiq_20261001.dump"
```

The backup uses PostgreSQL custom format (pg_dump -Fc).

The script creates the archive temporarily, validates that PostgreSQL can read its contents, and only then moves it to its final destination.

Existing backup files are never overwritten.

Backup files are stored outside the repository and must not be committed to Git.

## 3. Database restoration
Run:

```bash
./scripts/restore.sh BACKUP_FILE TARGET_DATABASE
```

Example:
```bash
./scripts/restore.sh \
    "$HOME/.local/share/houndiq/backups/houndiq_20261001.dump" \
    houndiq_20261001
```


The restoration process:
1. Validates the backup archive.
2. Creates a new database from template0.
3. Restores the schema and data using pg_restore.
4. Preserves the restored database for subsequent use.
The target database must not already exist. The script never overwrites an existing database.

If restoration fails after the target database has been created, the incomplete database is removed automatically.

The source database and backup archive remain unchanged.

A restored database can be selected by overriding POSTGRES_DB when running the Python application or its tests:

```bash
POSTGRES_DB=houndiq_20261001 uv run --env-file .env pytest tests/integration
```

This allows HoundIQ to operate against different historical snapshots without modifying the default database configuration.

## 4. Backup and restoration verification
Run:

```bash
uv run --env-file .env pytest tests/integration/test_backup_restore.py -v
```

The integration test performs the complete recovery process:
1. Captures the source database state.
2. Generates a temporary backup.
3. Restores it into a uniquely named, isolated database.
4. Compares all records in the four tables.
5. Compares database columns, constraints and indexes.
6. Checks referential integrity.
7. Runs database and ingestion integration tests against the restored database.
8. Exercises Python race and greyhound retrieval operations using records found dynamically in the restored database.
The test removes its temporary backup and restored database after execution, including when a verification step fails.

It does not delete permanent backups or manually restored databases.

The test requires the Docker Compose PostgreSQL service to be running and a source database containing the HoundIQ schema and data.

The query verification is independent of fixed meeting, race and greyhound identifiers, so the test can be run against older historical snapshots.

## 5. Operational considerations
Backups are created on demand. No automatic backup schedule or retention policy is configured.

Historical snapshots can be retained for later analysis and restored under separate database names.

The user is responsible for keeping important backup files safe and ensuring that the required snapshots remain available.

Temporary test databases are disposable. Manually restored databases and permanent backup archives are retained until explicitly removed.
EOF