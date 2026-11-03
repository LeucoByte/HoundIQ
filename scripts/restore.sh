#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
    printf 'Usage: %s BACKUP_FILE TARGET_DATABASE\n' "$0"
}

if (($# == 1)) && [[ "$1" == "--help" ]]; then
    usage
    exit 0
fi

if (($# != 2)); then
    usage >&2
    exit 2
fi

backup_file="$1"
target_database="$2"
caller_directory="$PWD"

if [[ "$backup_file" != /* ]]; then
    backup_file="$caller_directory/$backup_file"
fi

if [[ ! -f "$backup_file" ]]; then
    printf 'Backup file does not exist: %s\n' "$backup_file" >&2
    exit 1
fi

if [[ ! "$target_database" =~ ^[A-Za-z_][A-Za-z0-9_]{0,62}$ ]]; then
    printf 'Invalid PostgreSQL database name: %s\n' "$target_database" >&2
    exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

docker compose exec -T db pg_restore --list \
    < "$backup_file" > /dev/null

target_created=0
restore_completed=0

cleanup() {
    local status=$?
    trap - EXIT

    if [[ "$target_created" == "1" && "$restore_completed" != "1" ]]; then
        if ! docker compose exec -T db sh -c \
            'dropdb --if-exists -U "$POSTGRES_USER" "$1"' \
            sh "$target_database"; then
            printf 'Could not remove the incomplete target database: %s\n' \
                "$target_database" >&2
        fi
    fi

    exit "$status"
}
trap cleanup EXIT

printf 'Creating isolated database: %s\n' "$target_database"

docker compose exec -T db sh -c \
    'createdb -T template0 -U "$POSTGRES_USER" "$1"' \
    sh "$target_database"

target_created=1

printf 'Restoring backup into: %s\n' "$target_database"

docker compose exec -T db sh -c '
    pg_restore --exit-on-error --no-owner --no-privileges \
        -U "$POSTGRES_USER" -d "$1"
' sh "$target_database" < "$backup_file"

restore_completed=1

printf 'Backup successfully restored into: %s\n' "$target_database"
