import logging
import math
import requests

BASE_URL = "https://api.gbgb.org.uk/api"
ITEMS_PER_PAGE = 100
REQUEST_TIMEOUT = 20
PROGRESS_BATCH_SIZE = 100
SUCCESS_LEVEL = 25

logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.gbgb.org.uk/",
}

class ExtractionError(RuntimeError):
    pass


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_json(session, path, params, failures, label):
    try:
        response = session.get(
            f"{BASE_URL}{path}",
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    except (requests.RequestException, ValueError) as error:
        failures.append(f"{label}: {error}")
        logger.error("%s: %s", label, error)
        return None


def _read_items(payload, failures, label):
    if not isinstance(payload, dict):
        message = f"{label}: expected a JSON object"
        failures.append(message)
        logger.error("%s", message)
        return []

    items = payload.get("items")

    if not isinstance(items, list):
        message = f"{label}: response does not contain a valid items list"
        failures.append(message)
        logger.error("%s", message)
        return []

    records = []

    for item in items:
        if isinstance(item, dict):
            records.append(item)
        else:
            message = f"{label}: ignored a non-object record"
            failures.append(message)
            logger.error("%s", message)

    return records


def _log_batch(label, processed, total, failures_before, failures, details):
    batch_failures = len(failures) - failures_before
    message = (
        f"{label}: {processed}/{total} processed; "
        f"{details}; {batch_failures} failure(s) in batch"
    )

    if batch_failures:
        logger.warning("%s", message)
    else:
        logger.log(SUCCESS_LEVEL, "%s", message)


def _extract_races(session, failures):
    logger.info("Retrieving global race records")

    first_page = _get_json(
        session,
        "/results",
        {"page": 1, "itemsPerPage": ITEMS_PER_PAGE},
        failures,
        "Global races page 1",
    )

    if first_page is None:
        raise ExtractionError("Unable to retrieve the first global races page")

    if not isinstance(first_page, dict):
        message = "Global races page 1: expected a JSON object"
        failures.append(message)
        raise ExtractionError(message)

    races = _read_items(first_page, failures, "Global races page 1")

    meta = first_page.get("meta")
    total_count = (
        _integer(meta.get("count"))
        if isinstance(meta, dict)
        else None
    )

    total_pages = (
        math.ceil(total_count / ITEMS_PER_PAGE)
        if total_count is not None and total_count > 0
        else 1
    )

    logger.info(
        "Global races: %s records across %d pages",
        total_count if total_count is not None else "unknown number of",
        total_pages,
    )

    for page in range(2, total_pages + 1):
        payload = _get_json(
            session,
            "/results",
            {"page": page, "itemsPerPage": ITEMS_PER_PAGE},
            failures,
            f"Global races page {page}",
        )

        if payload is None:
            continue

        races.extend(
            _read_items(payload, failures, f"Global races page {page}")
        )

        if page % 10 == 0 or page == total_pages:
            logger.info(
                "Global races: %d/%s records retrieved",
                len(races),
                total_count if total_count is not None else "unknown",
            )

    if total_count is not None and len(races) < total_count:
        message = (
            f"Global races: retrieved {len(races)} of {total_count} records"
        )
        failures.append(message)
        logger.warning("%s", message)

    if total_count is not None and len(races) == total_count:
        logger.log(SUCCESS_LEVEL, "All %d global race records retrieved", len(races))
    else:
        logger.info("Global races extraction finished: %d records", len(races))

    return races


def _extract_meeting_details(session, meeting_ids, failures):
    meeting_details = []
    total = len(meeting_ids)
    batch_failures_before = len(failures)

    logger.info("Retrieving details for %d meetings", total)

    for index, meeting_id in enumerate(sorted(meeting_ids), start=1):
        payload = _get_json(
            session,
            f"/results/meeting/{meeting_id}",
            {"meeting": meeting_id},
            failures,
            f"Meeting {meeting_id}",
        )

        if payload is not None:
            if isinstance(payload, list):
                for detail in payload:
                    if isinstance(detail, dict):
                        meeting_details.append(detail)
                    else:
                        message = (
                            f"Meeting {meeting_id}: "
                            "response contains a non-object record"
                        )
                        failures.append(message)
                        logger.error("%s", message)
            else:
                message = (
                    f"Meeting {meeting_id}: expected a JSON array, "
                    f"received {type(payload).__name__}"
                )
                failures.append(message)
                logger.error("%s", message)

        if index % PROGRESS_BATCH_SIZE == 0 or index == total:
            _log_batch(
                "Meeting details",
                index,
                total,
                batch_failures_before,
                failures,
                f"{len(meeting_details)} meeting records retrieved",
            )
            batch_failures_before = len(failures)

    return meeting_details


def _extract_dog_history(session, dog_id, failures):
    dog_races = []
    page = 1
    total_count = None

    while True:
        payload = _get_json(
            session,
            f"/results/dog/{dog_id}",
            {
                "page": page,
                "itemsPerPage": ITEMS_PER_PAGE,
                "race_type": "race",
            },
            failures,
            f"Dog {dog_id}, page {page}",
        )

        if payload is None:
            break

        if not isinstance(payload, dict):
            message = f"Dog {dog_id}, page {page}: expected a JSON object"
            failures.append(message)
            logger.error("%s", message)
            break

        items = _read_items(
            payload,
            failures,
            f"Dog {dog_id}, page {page}",
        )

        if not items:
            break

        dog_races.extend(items)

        meta = payload.get("meta")

        if isinstance(meta, dict):
            total_count = _integer(meta.get("count"))

        if total_count is not None and len(dog_races) >= total_count:
            break

        if len(items) < ITEMS_PER_PAGE:
            break

        page += 1

    if total_count is not None and len(dog_races) < total_count:
        message = (
            f"Dog {dog_id}: retrieved {len(dog_races)} "
            f"of {total_count} records"
        )
        failures.append(message)
        logger.warning("%s", message)

    return {
        "dogId": dog_id,
        "totalRaces": len(dog_races),
        "items": dog_races,
    }


def extract_datasets():
    failures = []

    logger.info("Starting GBGB extraction")

    with requests.Session() as session:
        session.headers.update(HEADERS)

        race_records = _extract_races(session, failures)

        meeting_ids = set()
        dog_ids = set()

        for record in race_records:
            meeting_id = _integer(record.get("meetingId"))
            dog_id = _integer(record.get("dogId"))

            if meeting_id is not None:
                meeting_ids.add(meeting_id)

            if dog_id is not None:
                dog_ids.add(dog_id)

        logger.info(
            "Identified %d unique meetings and %d unique greyhounds",
            len(meeting_ids),
            len(dog_ids),
        )

        meeting_details = _extract_meeting_details(
            session,
            meeting_ids,
            failures,
        )

        dog_histories = []
        total_dogs = len(dog_ids)
        batch_failures_before = len(failures)
        total_history_records = 0

        logger.info("Retrieving histories for %d greyhounds", total_dogs)

        for index, dog_id in enumerate(sorted(dog_ids), start=1):
            history = _extract_dog_history(
                session,
                dog_id,
                failures,
            )
            dog_histories.append(history)
            total_history_records += len(history["items"])

            if index % PROGRESS_BATCH_SIZE == 0 or index == total_dogs:
                _log_batch(
                    "Dog histories",
                    index,
                    total_dogs,
                    batch_failures_before,
                    failures,
                    f"{total_history_records} historical races retrieved",
                )
                batch_failures_before = len(failures)

    datasets = {
        "race_records": race_records,
        "meeting_details": meeting_details,
        "dog_histories": dog_histories,
    }

    if failures:
        logger.warning(
            "Extraction finished with %d failure(s)",
            len(failures),
        )
    else:
        logger.log(SUCCESS_LEVEL, "GBGB extraction completed without failures")

    return datasets, failures