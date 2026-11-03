from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

def _value(record, *keys):
    for key in keys:
        value = record.get(key)

        if value is not None:
            return value

    return None


def _text(value):
    if value is None:
        return None

    value = str(value).strip()
    return value or None


def _decimal(value):
    if value is None or value == "":
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _integer(value):
    number = _decimal(value)

    if number is None or number != number.to_integral_value():
        return None

    return int(number)


def _boolean(value):
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes"}:
        return True

    if normalized in {"false", "0", "no"}:
        return False

    return None


def _date(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if value is None:
        return None

    normalized = str(value).strip()

    for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(normalized, date_format).date()
        except ValueError:
            continue

    return None


def _time(value):
    if isinstance(value, time):
        return value

    if value is None:
        return None

    try:
        return time.fromisoformat(str(value).strip())
    except ValueError:
        return None


def _dog_born(value):
    if value is None:
        return None

    normalized = str(value).strip()

    for date_format in ("%b-%Y", "%B-%Y", "%Y-%m"):
        try:
            return datetime.strptime(normalized, date_format).strftime("%Y-%m")
        except ValueError:
            continue

    return None



def _merge(records, identifier, values):
    if identifier is None:
        return

    current = records.setdefault(identifier, values.copy())

    for key, value in values.items():
        if value is not None:
            current[key] = value



def _add_meeting(record, meetings):
    meeting_id = _integer(_value(record, "meetingId"))

    if meeting_id is None:
        return None

    meeting_date = _date(_value(record, "meetingDate"))

    if meeting_date is None:
        meeting_date = _date(_value(record, "raceDate"))

    _merge(
        meetings,
        meeting_id,
        {
            "meeting_id": meeting_id,
            "meeting_date": meeting_date,
            "track_name": _text(_value(record, "trackName")),
        },
    )

    return meeting_id


def _add_race(record, races, fallback_meeting_id=None):
    race_id = _integer(_value(record, "raceId"))

    if race_id is None:
        return None

    meeting_id = _integer(_value(record, "meetingId"))

    if meeting_id is None:
        meeting_id = fallback_meeting_id

    _merge(
        races,
        race_id,
        {
            "race_id": race_id,
            "meeting_id": meeting_id,
            "race_number": _integer(_value(record, "raceNumber")),
            "race_time": _time(_value(record, "raceTime")),
            "race_class": _text(_value(record, "raceClass")),
            "race_distance": _decimal(_value(record, "raceDistance")),
            "race_type": _text(_value(record, "raceType")),
            "race_handicap": _boolean(_value(record, "raceHandicap")),
            "race_going": _integer(_value(record, "raceGoing")),
            "race_win_time": _decimal(_value(record, "raceWinTime")),
        },
    )

    return race_id


def _add_dog(record, greyhounds, fallback_dog_id=None):
    dog_id = _integer(_value(record, "dogId"))

    if dog_id is None:
        dog_id = fallback_dog_id

    if dog_id is None:
        return None

    _merge(
        greyhounds,
        dog_id,
        {
            "dog_id": dog_id,
            "dog_name": _text(_value(record, "dogName")),
            "dog_born": _dog_born(_value(record, "dogBorn")),
            "dog_sex": _text(_value(record, "dogSex")),
            "sire_name": _text(_value(record, "dogSire", "sireName")),
            "dam_name": _text(_value(record, "dogDam", "damName")),
            "dog_origin": _text(_value(record, "dogOrigin")),
        },
    )

    return dog_id


def _add_participation(
    record,
    participations,
    fallback_dog_id=None,
):
    race_id = _integer(_value(record, "raceId"))
    dog_id = _integer(_value(record, "dogId"))

    if dog_id is None:
        dog_id = fallback_dog_id

    if race_id is None or dog_id is None:
        return "missing_identifiers"

    trap_number = _integer(_value(record, "trapNumber"))

    if trap_number is None:
        return "missing_trap"

    _merge(
        participations,
        (race_id, dog_id),
        {
            "race_id": race_id,
            "dog_id": dog_id,
            "trap_number": trap_number,
            "trap_handicap": _decimal(_value(record, "trapHandicap")),
            "trainer_name": _text(_value(record, "trainerName")),
            "result_position": _integer(_value(record, "resultPosition")),
            "result_btn_distance": _text(_value(record, "resultBtnDistance")),
            "result_run_time": _decimal(_value(record, "resultRunTime")),
            "result_adjusted_time": _decimal(
                _value(record, "resultAdjustedTime")
            ),
            "result_sectional_time": _decimal(
                _value(record, "resultSectionalTime")
            ),
            "result_comment": _text(_value(record, "resultComment")),
            "result_dog_weight": _decimal(_value(record, "resultDogWeight")),
            "starting_price": _text(_value(record, "SP", "startingPrice")),
        },
    )

    return None


def map_datasets(race_records, meeting_details, dog_histories):
    meetings = {}
    races = {}
    greyhounds = {}
    participations = {}

    skipped = {
        "invalid_records": 0,
        "empty_traps_ignored": 0,
        "participations_missing_identifiers": 0,
        "participations_missing_trap": 0,
        "meetings_missing_required_fields": 0,
        "races_missing_valid_meeting": 0,
        "greyhounds_missing_name": 0,
        "participations_missing_valid_references": 0,
    }

    for record in race_records:
        if not isinstance(record, dict):
            skipped["invalid_records"] += 1
            continue

        _add_meeting(record, meetings)
        _add_race(record, races)
        _add_dog(record, greyhounds)

        reason = _add_participation(record, participations)

        if reason == "missing_identifiers":
            skipped["participations_missing_identifiers"] += 1
        elif reason == "missing_trap":
            skipped["participations_missing_trap"] += 1

    for history in dog_histories:
        if not isinstance(history, dict):
            skipped["invalid_records"] += 1
            continue

        dog_id = _integer(_value(history, "dogId"))
        items = history.get("items", [])

        if not isinstance(items, list):
            skipped["invalid_records"] += 1
            continue

        for record in items:
            if not isinstance(record, dict):
                skipped["invalid_records"] += 1
                continue

            _add_meeting(record, meetings)
            _add_race(record, races)
            _add_dog(record, greyhounds, dog_id)

            reason = _add_participation(
                record,
                participations,
                dog_id,
            )

            if reason == "missing_identifiers":
                skipped["participations_missing_identifiers"] += 1
            elif reason == "missing_trap":
                skipped["participations_missing_trap"] += 1

    for detail in meeting_details:
        if not isinstance(detail, dict):
            skipped["invalid_records"] += 1
            continue

        meeting_id = _add_meeting(detail, meetings)
        detail_races = detail.get("races", [])

        if not isinstance(detail_races, list):
            skipped["invalid_records"] += 1
            continue

        for race in detail_races:
            if not isinstance(race, dict):
                skipped["invalid_records"] += 1
                continue

            race_id = _add_race(race, races, meeting_id)
            traps = race.get("traps", [])

            if not isinstance(traps, list):
                continue

            for trap in traps:
                if not isinstance(trap, dict):
                    skipped["invalid_records"] += 1
                    continue

                dog_id = _integer(_value(trap, "dogId"))

                if dog_id is None:
                    skipped["empty_traps_ignored"] += 1
                    continue

                _add_dog(trap, greyhounds)

                reason = _add_participation(
                    {
                        **trap,
                        "raceId": _value(trap, "raceId") or race_id,
                    },
                    participations,
                )

                if reason == "missing_identifiers":
                    skipped["participations_missing_identifiers"] += 1
                elif reason == "missing_trap":
                    skipped["participations_missing_trap"] += 1

    valid_meetings = {
        identifier: record
        for identifier, record in meetings.items()
        if record.get("meeting_date") is not None
        and record.get("track_name")
    }

    skipped["meetings_missing_required_fields"] += (
        len(meetings) - len(valid_meetings)
    )

    valid_races = {
        identifier: record
        for identifier, record in races.items()
        if record.get("meeting_id") in valid_meetings
    }

    skipped["races_missing_valid_meeting"] += (
        len(races) - len(valid_races)
    )

    valid_greyhounds = {
        identifier: record
        for identifier, record in greyhounds.items()
        if record.get("dog_name")
    }

    skipped["greyhounds_missing_name"] += (
        len(greyhounds) - len(valid_greyhounds)
    )

    valid_participations = {
        identifier: record
        for identifier, record in participations.items()
        if record.get("race_id") in valid_races
        and record.get("dog_id") in valid_greyhounds
        and record.get("trap_number") is not None
    }

    skipped["participations_missing_valid_references"] += (
        len(participations) - len(valid_participations)
    )

    return {
        "meetings": list(valid_meetings.values()),
        "races": list(valid_races.values()),
        "greyhounds": list(valid_greyhounds.values()),
        "participations": list(valid_participations.values()),
        "skipped": skipped,
    }


def ingest_datasets(
    connection,
    race_records,
    meeting_details,
    dog_histories,
):
    mapped = map_datasets(
        race_records,
        meeting_details,
        dog_histories,
    )

    with connection.cursor() as cursor:
        if mapped["meetings"]:
            cursor.executemany(
                """
                INSERT INTO meetings (
                    meeting_id,
                    meeting_date,
                    track_name
                )
                VALUES (
                    %(meeting_id)s,
                    %(meeting_date)s,
                    %(track_name)s
                )
                ON CONFLICT (meeting_id) DO UPDATE SET
                    meeting_date = COALESCE(
                        EXCLUDED.meeting_date,
                        meetings.meeting_date
                    ),
                    track_name = COALESCE(
                        EXCLUDED.track_name,
                        meetings.track_name
                    )
                """,
                mapped["meetings"],
            )

        if mapped["races"]:
            cursor.executemany(
                """
                INSERT INTO races (
                    race_id,
                    meeting_id,
                    race_number,
                    race_time,
                    race_class,
                    race_distance,
                    race_type,
                    race_handicap,
                    race_going,
                    race_win_time
                )
                VALUES (
                    %(race_id)s,
                    %(meeting_id)s,
                    %(race_number)s,
                    %(race_time)s,
                    %(race_class)s,
                    %(race_distance)s,
                    %(race_type)s,
                    %(race_handicap)s,
                    %(race_going)s,
                    %(race_win_time)s
                )
                ON CONFLICT (race_id) DO UPDATE SET
                    meeting_id = COALESCE(
                        EXCLUDED.meeting_id,
                        races.meeting_id
                    ),
                    race_number = COALESCE(
                        EXCLUDED.race_number,
                        races.race_number
                    ),
                    race_time = COALESCE(
                        EXCLUDED.race_time,
                        races.race_time
                    ),
                    race_class = COALESCE(
                        EXCLUDED.race_class,
                        races.race_class
                    ),
                    race_distance = COALESCE(
                        EXCLUDED.race_distance,
                        races.race_distance
                    ),
                    race_type = COALESCE(
                        EXCLUDED.race_type,
                        races.race_type
                    ),
                    race_handicap = COALESCE(
                        EXCLUDED.race_handicap,
                        races.race_handicap
                    ),
                    race_going = COALESCE(
                        EXCLUDED.race_going,
                        races.race_going
                    ),
                    race_win_time = COALESCE(
                        EXCLUDED.race_win_time,
                        races.race_win_time
                    )
                """,
                mapped["races"],
            )

        if mapped["greyhounds"]:
            cursor.executemany(
                """
                INSERT INTO greyhounds (
                    dog_id,
                    dog_name,
                    dog_born,
                    dog_sex,
                    sire_name,
                    dam_name,
                    dog_origin
                )
                VALUES (
                    %(dog_id)s,
                    %(dog_name)s,
                    %(dog_born)s,
                    %(dog_sex)s,
                    %(sire_name)s,
                    %(dam_name)s,
                    %(dog_origin)s
                )
                ON CONFLICT (dog_id) DO UPDATE SET
                    dog_name = COALESCE(
                        EXCLUDED.dog_name,
                        greyhounds.dog_name
                    ),
                    dog_born = COALESCE(
                        EXCLUDED.dog_born,
                        greyhounds.dog_born
                    ),
                    dog_sex = COALESCE(
                        EXCLUDED.dog_sex,
                        greyhounds.dog_sex
                    ),
                    sire_name = COALESCE(
                        EXCLUDED.sire_name,
                        greyhounds.sire_name
                    ),
                    dam_name = COALESCE(
                        EXCLUDED.dam_name,
                        greyhounds.dam_name
                    ),
                    dog_origin = COALESCE(
                        EXCLUDED.dog_origin,
                        greyhounds.dog_origin
                    )
                """,
                mapped["greyhounds"],
            )

        if mapped["participations"]:
            cursor.executemany(
                """
                INSERT INTO race_participations (
                    race_id,
                    dog_id,
                    trap_number,
                    trap_handicap,
                    trainer_name,
                    result_position,
                    result_btn_distance,
                    result_run_time,
                    result_adjusted_time,
                    result_sectional_time,
                    result_comment,
                    result_dog_weight,
                    starting_price
                )
                VALUES (
                    %(race_id)s,
                    %(dog_id)s,
                    %(trap_number)s,
                    %(trap_handicap)s,
                    %(trainer_name)s,
                    %(result_position)s,
                    %(result_btn_distance)s,
                    %(result_run_time)s,
                    %(result_adjusted_time)s,
                    %(result_sectional_time)s,
                    %(result_comment)s,
                    %(result_dog_weight)s,
                    %(starting_price)s
                )
                ON CONFLICT (race_id, dog_id) DO UPDATE SET
                    trap_number = COALESCE(
                        EXCLUDED.trap_number,
                        race_participations.trap_number
                    ),
                    trap_handicap = COALESCE(
                        EXCLUDED.trap_handicap,
                        race_participations.trap_handicap
                    ),
                    trainer_name = COALESCE(
                        EXCLUDED.trainer_name,
                        race_participations.trainer_name
                    ),
                    result_position = COALESCE(
                        EXCLUDED.result_position,
                        race_participations.result_position
                    ),
                    result_btn_distance = COALESCE(
                        EXCLUDED.result_btn_distance,
                        race_participations.result_btn_distance
                    ),
                    result_run_time = COALESCE(
                        EXCLUDED.result_run_time,
                        race_participations.result_run_time
                    ),
                    result_adjusted_time = COALESCE(
                        EXCLUDED.result_adjusted_time,
                        race_participations.result_adjusted_time
                    ),
                    result_sectional_time = COALESCE(
                        EXCLUDED.result_sectional_time,
                        race_participations.result_sectional_time
                    ),
                    result_comment = COALESCE(
                        EXCLUDED.result_comment,
                        race_participations.result_comment
                    ),
                    result_dog_weight = COALESCE(
                        EXCLUDED.result_dog_weight,
                        race_participations.result_dog_weight
                    ),
                    starting_price = COALESCE(
                        EXCLUDED.starting_price,
                        race_participations.starting_price
                    )
                """,
                mapped["participations"],
            )

    return {
        "meetings": len(mapped["meetings"]),
        "races": len(mapped["races"]),
        "greyhounds": len(mapped["greyhounds"]),
        "participations": len(mapped["participations"]),
        "skipped": mapped["skipped"],
    }