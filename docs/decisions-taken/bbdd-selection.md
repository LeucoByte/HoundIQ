# Database Selection

## Decision
**PostgreSQL is selected as HoundIQ's persistent database.**

It provides a relational model suited to HoundIQ's domain, where meetings, races, greyhounds and race participations are connected through explicit relationships.

Its support for transactions, foreign keys, constraints and indexes provides the consistency and querying capabilities required by the application.

## Alternatives considered

| Candidate | Assessment | Decision |
|---|---|---|
| **SQLite** | Embedded relational database requiring no separate server. Simple and reliable, but allows only one simultaneous writer per database file. Less suitable for a shared database service accessed by different application components. | Rejected |
| **MySQL / MariaDB** | Mature client-server relational databases supporting transactions, indexes and foreign-key constraints. Technically suitable, but offer no decisive advantage for HoundIQ over PostgreSQL. | Rejected |
| **PostgreSQL** | Mature relational database with strong integrity guarantees, transactional support, indexing and an extensive extension ecosystem. Fits the current requirements and provides room for future capabilities. | **Selected** |

## Rationale
PostgreSQL satisfies the current requirements for inserting, updating and retrieving related racing data while maintaining referential integrity.

It also offers a useful future option for AI-powered retrieval: **pgvector**, an extension that enables vector storage and similarity search directly in PostgreSQL. This could allow HoundIQ to explore vector-based retrieval without introducing a separate database initially. It does not imply a commitment to RAG or to using pgvector.

Performance benchmarks are not considered necessary at this stage. The current workload does not justify choosing a database based on differences in raw query speed.

## Deployment and persistence
- **Docker image:** Official PostgreSQL image, pinned to the `postgres:18` major version tag rather than `latest`.
- **Execution:** Docker Compose, with the database running as a separate service.
- **Persistence:** Docker-managed named volume mounted at `/var/lib/postgresql`, keeping database files outside the repository and independent of the container lifecycle.
- **Repository:** Compose configuration is version-controlled; database files and actual data are not.
- **Backups:** A separate backup and recovery process will be implemented and verified. A Docker volume alone is not considered a backup.

## Configuration
Database connection settings and credentials will be supplied through environment variables.

Local credentials will be stored in an untracked `.env` file. A `.env.example` containing placeholder values will be committed to document the required configuration.

Actual credentials and sensitive configuration must never be committed to Git.