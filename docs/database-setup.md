# Database Environmen
HoundIQ uses PostgreSQL 18 as its persistent relational database.

The database runs in Docker Compose, while the Python application connects to it from the host environment.

## Requirements
- Docker Engine
- Docker Compose
- uv

## Configuration
Create a local environment file:

```bash
cp .env.example .env
```

Set the database password in `.env`.

## Start the database
```bash
docker compose up -d db
```

Check the service status:
```bash
docker compose ps
```

The database is ready when its health status is `healthy`.

## Run tests
Synchronize the Python environment:

```bash
uv sync
```

Run the default test suite:
```bash
uv run pytest
```

Run database integration tests:
```bash
uv run --env-file .env pytest tests/integration
```

## Stop the database
```bash
docker compose down
```

The named volume is preserved, so database contents remain available when the container is started again.

To permanently remove the database volume and its contents:

```bash
docker compose down --volumes
```

This operation deletes the persisted database data.

## Initialization
SQL files under `database/init/` are executed alphabetically when PostgreSQL initializes an empty data volume.

They are not executed again when the volume already contains a database.

Changes to an existing database schema must therefore be applied through an explicit schema update or migration process.