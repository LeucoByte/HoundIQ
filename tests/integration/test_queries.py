from datetime import date
from decimal import Decimal

from houndiq.database import get_connection
from houndiq.queries import get_greyhound, get_race


def test_get_race_returns_meeting_and_participants():
    connection = get_connection()

    try:
        result = get_race(connection, 454669, 1256370)

        assert result is not None

        assert result["meeting"] == {
            "meeting_id": 454669,
            "meeting_date": date(2026, 11, 3),
            "track_name": "Monmore",
        }

        assert result["race"] == {
            "race_id": 1256370,
            "meeting_id": 454669,
            "race_number": 11,
            "race_time": None,
            "race_class": "T3",
            "race_distance": Decimal("264.00"),
            "race_type": "Flat",
            "race_handicap": None,
            "race_going": 5,
            "race_win_time": None,
        }

        participants = {
            item["greyhound"]["dog_id"]: item
            for item in result["participants"]
        }

        assert set(participants) == {665184, 638994, 645340}

        assert {
            dog_id: (
                item["greyhound"]["dog_name"],
                item["participation"]["trap_number"],
                item["participation"]["result_position"],
            )
            for dog_id, item in participants.items()
        } == {
            665184: ("Devious Dave", 2, 2),
            638994: ("Bang On Molly", 4, 3),
            645340: ("Carmac Pete", 6, 1),
        }

        carmac = participants[645340]

        assert carmac["greyhound"] == {
            "dog_id": 645340,
            "dog_name": "Carmac Pete",
            "dog_born": "2023-04",
            "dog_sex": "d",
            "sire_name": "Redzer Ardfert",
            "dam_name": "Ardfert Josie",
            "dog_origin": "Ir",
        }

        assert carmac["participation"] == {
            "race_id": 1256370,
            "dog_id": 645340,
            "trap_number": 6,
            "trap_handicap": None,
            "trainer_name": "N J Hunt",
            "result_position": 1,
            "result_btn_distance": "NK",
            "result_run_time": Decimal("15.44"),
            "result_adjusted_time": Decimal("15.49"),
            "result_sectional_time": None,
            "result_comment": "QAw,Wide,HeldOn",
            "result_dog_weight": Decimal("32.30"),
            "starting_price": None,
        }

        assert participants[665184]["participation"]["trainer_name"] is None
        assert participants[638994]["participation"]["result_run_time"] is None

    finally:
        connection.rollback()
        connection.close()


def test_get_greyhound_returns_profile_and_history():
    connection = get_connection()

    try:
        result = get_greyhound(connection, 645340)

        assert result is not None

        assert result["greyhound"] == {
            "dog_id": 645340,
            "dog_name": "Carmac Pete",
            "dog_born": "2023-04",
            "dog_sex": "d",
            "sire_name": "Redzer Ardfert",
            "dam_name": "Ardfert Josie",
            "dog_origin": "Ir",
        }

        assert result["history"]
        
        historical_race = next(
            item
            for item in result["history"]
            if item["race"]["race_id"] == 1256370
        )

        assert historical_race["meeting"] == {
            "meeting_id": 454669,
            "meeting_date": date(2026, 11, 3),
            "track_name": "Monmore",
        }

        assert historical_race["race"] == {
            "race_id": 1256370,
            "meeting_id": 454669,
            "race_number": 11,
            "race_time": None,
            "race_class": "T3",
            "race_distance": Decimal("264.00"),
            "race_type": "Flat",
            "race_handicap": None,
            "race_going": 5,
            "race_win_time": None,
        }

        assert historical_race["participation"] == {
            "race_id": 1256370,
            "dog_id": 645340,
            "trap_number": 6,
            "trap_handicap": None,
            "trainer_name": "N J Hunt",
            "result_position": 1,
            "result_btn_distance": "NK",
            "result_run_time": Decimal("15.44"),
            "result_adjusted_time": Decimal("15.49"),
            "result_sectional_time": None,
            "result_comment": "QAw,Wide,HeldOn",
            "result_dog_weight": Decimal("32.30"),
            "starting_price": None,
        }

    finally:
        connection.rollback()
        connection.close()


def test_queries_return_none_for_missing_entities():
    connection = get_connection()

    try:
        assert get_race(connection, 454669, 999999999) is None
        assert get_race(connection, 454688, 1256370) is None
        assert get_greyhound(connection, 999999999) is None

    finally:
        connection.rollback()
        connection.close()
