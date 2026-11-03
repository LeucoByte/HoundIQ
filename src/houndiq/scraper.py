import logging
import sys
from houndiq.database import get_connection
from houndiq.gbgb import SUCCESS_LEVEL, ExtractionError, extract_datasets
from houndiq.ingestion import ingest_datasets

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: "\033[34m",
        SUCCESS_LEVEL: "\033[32m",
        logging.WARNING: "\033[38;5;208m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[1;31m",
    }

    def format(self, record):
        message = super().format(record)

        if not sys.stderr.isatty():
            return message

        color = self.COLORS.get(record.levelno, "")
        return f"{color}{message}\033[0m"


def main():
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColorFormatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )

    logger = logging.getLogger(__name__)

    logger.info("Starting HoundIQ scraper")

    try:
        datasets, failures = extract_datasets()
    except ExtractionError as error:
        logger.error("Extraction failed: %s", error)
        return 1

    if not datasets["race_records"]:
        logger.error("No race records retrieved. Nothing to ingest.")
        return 1

    logger.info("Starting database ingestion")

    try:
        with get_connection() as connection:
            report = ingest_datasets(connection, **datasets)
    except Exception:
        logger.exception("Database ingestion failed")
        return 1

    logger.log(SUCCESS_LEVEL, "Database ingestion completed")
    logger.log(SUCCESS_LEVEL, "Meetings: %d", report["meetings"])
    logger.log(SUCCESS_LEVEL, "Races: %d", report["races"])
    logger.log(SUCCESS_LEVEL, "Greyhounds: %d", report["greyhounds"])
    logger.log(SUCCESS_LEVEL, "Participations: %d", report["participations"])

    skipped = {
        name: count
        for name, count in report["skipped"].items()
        if count
    }

    if skipped:
        logger.warning("Skipped or ignored records: %s", skipped)

    if failures:
        logger.warning(
            "Extraction completed with %d failure(s). "
            "Available data was persisted.",
            len(failures),
        )
        return 1

    logger.log(SUCCESS_LEVEL, "All extraction requests completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())