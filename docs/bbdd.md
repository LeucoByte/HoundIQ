# Database Structure

## 1. Design
The database uses four relational tables:
- `meetings`
- `races`
- `greyhounds`
- `race_participations`

The structure follows the domain model defined in `data-fields-relations.md`, rather than reproducing the GBGB JSON datasets.

## 2. Tables

### meetings
Represents a racing meeting.

| Column | Type | Constraints |
|---|---|---|
| `meeting_id` | BIGINT | Primary key |
| `meeting_date` | DATE | NOT NULL |
| `track_name` | TEXT | NOT NULL |

### races
Represents a race belonging to a meeting.

| Column | Type | Constraints |
|---|---|---|
| `race_id` | BIGINT | Primary key |
| `meeting_id` | BIGINT | NOT NULL, Foreign key → meetings |
| `race_number` | SMALLINT | |
| `race_time` | TIME | |
| `race_class` | TEXT | |
| `race_distance` | NUMERIC(7,2) | |
| `race_type` | TEXT | |
| `race_handicap` | BOOLEAN | |
| `race_going` | INTEGER | |
| `race_win_time` | NUMERIC(6,2) | |

`race_date` is not stored separately because the meeting date provides this information.

### greyhounds
Represents an individual greyhound and its identity and pedigree.

| Column | Type | Constraints |
|---|---|---|
| `dog_id` | BIGINT | Primary key |
| `dog_name` | TEXT | NOT NULL |
| `dog_born` | VARCHAR(7) | |
| `dog_sex` | TEXT | |
| `sire_name` | TEXT | |
| `dam_name` | TEXT | |
| `dog_origin` | TEXT | |

`dog_born` uses the `YYYY-MM` format because GBGB only provides month and year.

Pedigree names are stored as attributes rather than foreign keys because the source does not provide parent identifiers.

### race_participations
Connects a greyhound to a race and stores information specific to that participation.

| Column | Type | Constraints |
|---|---|---|
| `race_id` | BIGINT | Primary key, Foreign key → races |
| `dog_id` | BIGINT | Primary key, Foreign key → greyhounds |
| `trap_number` | SMALLINT | NOT NULL |
| `trap_handicap` | NUMERIC(7,2) | |
| `trainer_name` | TEXT | |
| `result_position` | SMALLINT | |
| `result_btn_distance` | TEXT | |
| `result_run_time` | NUMERIC(6,2) | |
| `result_adjusted_time` | NUMERIC(6,2) | |
| `result_sectional_time` | NUMERIC(6,2) | |
| `result_comment` | TEXT | |
| `result_dog_weight` | NUMERIC(5,2) | |
| `starting_price` | TEXT | |

The composite primary key `(race_id, dog_id)` identifies each participation. Its uniqueness must be validated against the source data before ingestion is implemented.

`result_btn_distance` and `starting_price` remain textual because GBGB provides fractional representations that should not be altered without an explicit conversion rule.

## 3. Relationships
- One meeting contains multiple races.
- One race contains multiple race participations.
- One greyhound can have multiple race participations.
- Each participation belongs to exactly one race and one greyhound.

Foreign keys enforce these relationships and prevent orphan records.

## 4. Data handling
- Source identifiers are preserved as primary keys.
- Fields whose values may be unavailable, particularly race results, are nullable.
- Missing optional values are stored as SQL `NULL`, not fabricated defaults.
- Empty strings are normalised to `NULL` when they represent missing information.
- Source-provided values are stored without unverified unit conversions.
- Derived values, such as a greyhound's age at race time, are calculated when needed rather than stored.
- Excluded and deferred fields are not included in the initial schema.

## 5. Indexes
In addition to primary key indexes:
- `races(meeting_id)` supports retrieving races belonging to a meeting.
- `race_participations(dog_id)` supports retrieving a greyhound's racing history.

The primary key on `race_participations(race_id, dog_id)` already supports participant lookups by race.

Additional indexes should only be introduced when justified by actual query requirements.

## 6. Constraints and deletion
Foreign key relationships use restrictive deletion behaviour to prevent accidental loss of related racing history.

Database records are not expected to be deleted as part of the initial functionality.

This structure provides the persistence foundation for GBGB ingestion and the Python data-access operations.