from psycopg import Connection
from psycopg.rows import dict_row


def _group(record, prefix):
    prefix = f"{prefix}__"

    return {
        key[len(prefix):]: value
        for key, value in record.items()
        if key.startswith(prefix)
    }


def get_race(
    connection: Connection,
    meeting_id: int,
    race_id: int,
) -> dict | None:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
                m.meeting_id AS meeting__meeting_id,
                m.meeting_date AS meeting__meeting_date,
                m.track_name AS meeting__track_name,
                r.race_id AS race__race_id,
                r.meeting_id AS race__meeting_id,
                r.race_number AS race__race_number,
                r.race_time AS race__race_time,
                r.race_class AS race__race_class,
                r.race_distance AS race__race_distance,
                r.race_type AS race__race_type,
                r.race_handicap AS race__race_handicap,
                r.race_going AS race__race_going,
                r.race_win_time AS race__race_win_time
            FROM races r
            JOIN meetings m ON m.meeting_id = r.meeting_id
            WHERE r.meeting_id = %s
              AND r.race_id = %s
            """,
            (meeting_id, race_id),
        )

        record = cursor.fetchone()

        if record is None:
            return None

        meeting = _group(record, "meeting")
        race = _group(record, "race")

        cursor.execute(
            """
            SELECT
                rp.race_id AS participation__race_id,
                rp.dog_id AS participation__dog_id,
                rp.trap_number AS participation__trap_number,
                rp.trap_handicap AS participation__trap_handicap,
                rp.trainer_name AS participation__trainer_name,
                rp.result_position AS participation__result_position,
                rp.result_btn_distance AS participation__result_btn_distance,
                rp.result_run_time AS participation__result_run_time,
                rp.result_adjusted_time AS participation__result_adjusted_time,
                rp.result_sectional_time AS participation__result_sectional_time,
                rp.result_comment AS participation__result_comment,
                rp.result_dog_weight AS participation__result_dog_weight,
                rp.starting_price AS participation__starting_price,
                g.dog_id AS greyhound__dog_id,
                g.dog_name AS greyhound__dog_name,
                g.dog_born AS greyhound__dog_born,
                g.dog_sex AS greyhound__dog_sex,
                g.sire_name AS greyhound__sire_name,
                g.dam_name AS greyhound__dam_name,
                g.dog_origin AS greyhound__dog_origin
            FROM race_participations rp
            JOIN greyhounds g ON g.dog_id = rp.dog_id
            WHERE rp.race_id = %s
            ORDER BY rp.trap_number, rp.dog_id
            """,
            (race_id,),
        )

        participants = [
            {
                "participation": _group(row, "participation"),
                "greyhound": _group(row, "greyhound"),
            }
            for row in cursor.fetchall()
        ]

    return {
        "meeting": meeting,
        "race": race,
        "participants": participants,
    }


def get_greyhound(
    connection: Connection,
    dog_id: int,
) -> dict | None:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
                dog_id,
                dog_name,
                dog_born,
                dog_sex,
                sire_name,
                dam_name,
                dog_origin
            FROM greyhounds
            WHERE dog_id = %s
            """,
            (dog_id,),
        )

        greyhound = cursor.fetchone()

        if greyhound is None:
            return None

        cursor.execute(
            """
            SELECT
                m.meeting_id AS meeting__meeting_id,
                m.meeting_date AS meeting__meeting_date,
                m.track_name AS meeting__track_name,
                r.race_id AS race__race_id,
                r.meeting_id AS race__meeting_id,
                r.race_number AS race__race_number,
                r.race_time AS race__race_time,
                r.race_class AS race__race_class,
                r.race_distance AS race__race_distance,
                r.race_type AS race__race_type,
                r.race_handicap AS race__race_handicap,
                r.race_going AS race__race_going,
                r.race_win_time AS race__race_win_time,
                rp.race_id AS participation__race_id,
                rp.dog_id AS participation__dog_id,
                rp.trap_number AS participation__trap_number,
                rp.trap_handicap AS participation__trap_handicap,
                rp.trainer_name AS participation__trainer_name,
                rp.result_position AS participation__result_position,
                rp.result_btn_distance AS participation__result_btn_distance,
                rp.result_run_time AS participation__result_run_time,
                rp.result_adjusted_time AS participation__result_adjusted_time,
                rp.result_sectional_time AS participation__result_sectional_time,
                rp.result_comment AS participation__result_comment,
                rp.result_dog_weight AS participation__result_dog_weight,
                rp.starting_price AS participation__starting_price
            FROM race_participations rp
            JOIN races r ON r.race_id = rp.race_id
            JOIN meetings m ON m.meeting_id = r.meeting_id
            WHERE rp.dog_id = %s
            ORDER BY
                m.meeting_date DESC,
                r.race_time DESC NULLS LAST,
                r.race_number DESC NULLS LAST,
                r.race_id DESC
            """,
            (dog_id,),
        )

        history = [
            {
                "meeting": _group(row, "meeting"),
                "race": _group(row, "race"),
                "participation": _group(row, "participation"),
            }
            for row in cursor.fetchall()
        ]

    return {
        "greyhound": greyhound,
        "history": history,
    }

def get_greyhound_by_name(
    connection: Connection,
    dog_name: str,
) -> dict | None:
    if not dog_name or not dog_name.strip():
        raise ValueError("Greyhound name cannot be empty.")

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT dog_id
            FROM greyhounds
            WHERE LOWER(
                REGEXP_REPLACE(
                    BTRIM(dog_name),
                    '[[:space:]]+',
                    ' ',
                    'g'
                )
            ) = LOWER(
                REGEXP_REPLACE(
                    BTRIM(%s),
                    '[[:space:]]+',
                    ' ',
                    'g'
                )
            )
            LIMIT 2
            """,
            (dog_name,),
        )

        matches = cursor.fetchall()

    if not matches:
        return None

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous greyhound name: {dog_name}"
        )

    return get_greyhound(connection, matches[0]["dog_id"])
