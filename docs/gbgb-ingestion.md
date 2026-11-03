# GBGB Data Ingestion
HoundIQ retrieves historical racing data from the GBGB API and persists it directly into PostgreSQL.

## Execution
Start the database:

```bash
docker compose up -d db
```

Run the scraper:

```bash
uv run --env-file .env python -m houndiq.scraper
```

## Data Sources
The ingestion process uses three GBGB datasets:
- `Races`: global race-result records.
- `Details`: meeting information, races and trap entries.
- `Winners`: historical race records for each greyhound.

Records are merged using `meetingId`, `raceId` and `dogId`.

Meeting details are processed after the global records and dog histories, allowing them to complete previously retrieved information.

## Persistence
The application maps records to the PostgreSQL tables:
- `meetings`
- `races`
- `greyhounds`
- `race_participations`

Repeated ingestion uses PostgreSQL upserts to avoid duplicate records.

Records missing required identifiers or relationship data are not inserted.

Empty trap entries are ignored because they do not represent greyhound participations.

## Partial Retrieval Failures
When an individual API request fails, the scraper records the failure and continues with the remaining datasets whenever possible.

Successfully retrieved data is persisted.

The process exits with a non-zero status when extraction was incomplete, allowing the failure to be detected by external automation.

## Output
The normal ingestion workflow writes directly to PostgreSQL.

It does not generate JSON exports or ZIP archives.