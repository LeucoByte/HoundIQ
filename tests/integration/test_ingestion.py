from datetime import date, time
from decimal import Decimal
from houndiq.database import get_connection
from houndiq.ingestion import ingest_datasets
from fixtures.gbgb_samples import (
    DOG_HISTORIES,
    DOG_ID,
    MEETING_DETAILS,
    MEETING_ID,
    RACE_ID,
    RACE_RECORDS,
    SECOND_RACE_ID,
)

def test_ingestion_is_correct_and_idempotent():
    connection = get_connection()

    try:
        first_report = ingest_datasets(
            connection,
            RACE_RECORDS,
            MEETING_DETAILS,
            DOG_HISTORIES,
        )

        second_report = ingest_datasets(
            connection,
            RACE_RECORDS,
            MEETING_DETAILS,
            DOG_HISTORIES,
        )

        meeting = connection.execute(
            """
            SELECT meeting_date, track_name
            FROM meetings
            WHERE meeting_id = %s
            """,
            (MEETING_ID,),
        ).fetchone()

        assert meeting == (date(2026, 10, 4), "Yarmouth")

        first_race = connection.execute(
            """
            SELECT meeting_id, race_number, race_time, race_class,
                   race_distance, race_type, race_handicap,
                   race_going, race_win_time
            FROM races
            WHERE race_id = %s
            """,
            (RACE_ID,),
        ).fetchone()

        assert first_race == (
            MEETING_ID,
            1,
            time(11, 1),
            "A6",
            Decimal("462.00"),
            "Flat",
            False,
            0,
            Decimal("28.50"),
        )

        second_race = connection.execute(
            """
            SELECT meeting_id, race_number, race_time, race_class,
                   race_distance, race_type, race_handicap,
                   race_going, race_win_time
            FROM races
            WHERE race_id = %s
            """,
            (SECOND_RACE_ID,),
        ).fetchone()

        assert second_race == (
            MEETING_ID,
            2,
            time(11, 15),
            "A5",
            Decimal("462.00"),
            "Flat",
            False,
            0,
            Decimal("28.40"),
        )

        greyhound = connection.execute(
            """
            SELECT dog_name, dog_born, dog_sex,
                   sire_name, dam_name, dog_origin
            FROM greyhounds
            WHERE dog_id = %s
            """,
            (DOG_ID,),
        ).fetchone()

        assert greyhound == (
            "Good Anna",
            "2023-08",
            "b",
            "Ballyhimikin Jet",
            "Epic Majesty",
            "Ir",
        )

        first_participation = connection.execute(
            """
            SELECT trap_number, trainer_name, result_position,
                   result_btn_distance, result_run_time,
                   result_adjusted_time, result_sectional_time,
                   result_comment, result_dog_weight, starting_price
            FROM race_participations
            WHERE race_id = %s AND dog_id = %s
            """,
            (RACE_ID, DOG_ID),
        ).fetchone()

        assert first_participation == (
            6,
            "C R Morris",
            1,
            None,
            Decimal("28.63"),
            Decimal("28.63"),
            Decimal("5.39"),
            None,
            Decimal("25.80"),
            "11/8F",
        )

        second_participation = connection.execute(
            """
            SELECT trap_number, trainer_name, result_position,
                   result_btn_distance, result_run_time,
                   result_adjusted_time, result_sectional_time,
                   result_comment, result_dog_weight, starting_price
            FROM race_participations
            WHERE race_id = %s AND dog_id = %s
            """,
            (SECOND_RACE_ID, DOG_ID),
        ).fetchone()

        assert second_participation == (
            3,
            None,
            2,
            None,
            Decimal("28.70"),
            Decimal("28.70"),
            None,
            None,
            None,
            None,
        )

        empty_trap_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM race_participations
            WHERE race_id = %s AND trap_number = 2
            """,
            (RACE_ID,),
        ).fetchone()[0]

        assert empty_trap_count == 0

        assert first_report["meetings"] == 1
        assert first_report["races"] == 2
        assert first_report["greyhounds"] == 1
        assert first_report["participations"] == 2
        assert first_report["skipped"]["empty_traps_ignored"] == 1

        assert second_report["meetings"] == 1
        assert second_report["races"] == 2
        assert second_report["greyhounds"] == 1
        assert second_report["participations"] == 2
        assert second_report["skipped"]["empty_traps_ignored"] == 1

        meeting_count = connection.execute(
            "SELECT COUNT(*) FROM meetings WHERE meeting_id = %s",
            (MEETING_ID,),
        ).fetchone()[0]

        race_count = connection.execute(
            "SELECT COUNT(*) FROM races WHERE meeting_id = %s",
            (MEETING_ID,),
        ).fetchone()[0]

        dog_count = connection.execute(
            "SELECT COUNT(*) FROM greyhounds WHERE dog_id = %s",
            (DOG_ID,),
        ).fetchone()[0]

        participation_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM race_participations
            WHERE dog_id = %s
              AND race_id IN (%s, %s)
            """,
            (DOG_ID, RACE_ID, SECOND_RACE_ID),
        ).fetchone()[0]

        assert meeting_count == 1
        assert race_count == 2
        assert dog_count == 1
        assert participation_count == 2

    finally:
        connection.rollback()
        connection.close()