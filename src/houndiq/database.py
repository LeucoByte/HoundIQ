import os
import psycopg

def get_connection() -> psycopg.Connection:
    required_settings = (
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )

    missing_settings = [
        setting for setting in required_settings if not os.getenv(setting)
    ]

    if missing_settings:
        raise RuntimeError(
            f"Missing database environment variables: {', '.join(missing_settings)}"
        )

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )