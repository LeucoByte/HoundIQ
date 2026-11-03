#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
    printf 'Usage: %s [--database DATABASE] [--output FILE]\n' "$0"
}

caller_directory="$PWD"
database=""
output_file=""

while (($#)); do
    case "$1" in
        --database)
            if (($# < 2)); then
                usage >&2
                exit 2
            fi
            database="$2"
            shift 2
            ;;
        --output)
            if (($# < 2)); then
                usage >&2
                exit 2
            fi
            output_file="$2"
            shift 2
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -n "$output_file" && "$output_file" != /* ]]; then
    output_file="$caller_directory/$output_file"
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ -z "$database" ]]; then
    database="$(docker compose exec -T db sh -c 'printf "%s" "$POSTGRES_DB"')"
fi

if [[ ! "$database" =~ ^[A-Za-z_][A-Za-z0-9_]{0,62}$ ]]; then
    printf 'Invalid PostgreSQL database name: %s\n' "$database" >&2
    exit 2
fi

umask 077

if [[ -z "$output_file" ]]; then
    backup_dir="${HOUNDIQ_BACKUP_DIR:-$HOME/.local/share/houndiq/backups}"
    mkdir -p "$backup_dir"
    chmod 700 "$backup_dir"
    output_file="$backup_dir/houndiq_${database}_$(date -u +%Y%m%dT%H%M%SZ).dump"
else
    backup_dir="$(dirname "$output_file")"
    mkdir -p "$backup_dir"
fi

if [[ -e "$output_file" || -L "$output_file" ]]; then
    printf 'Backup destination already exists: %s\n' "$output_file" >&2
    exit 1
fi

temporary_file=""
cleanup() {
    if [[ -n "$temporary_file" ]]; then
        rm -f -- "$temporary_file"
    fi
}
trap cleanup EXIT

temporary_file="$(mktemp "$backup_dir/.$(basename "$output_file").XXXXXX")"

printf 'Creating backup of database: %s\n' "$database"

docker compose exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" -d "$1" -Fc' \
    sh "$database" > "$temporary_file"

if [[ ! -s "$temporary_file" ]]; then
    printf 'Backup file is empty.\n' >&2
    exit 1
fi

docker compose exec -T db pg_restore --list \
    < "$temporary_file" > /dev/null

mv -- "$temporary_file" "$output_file"
temporary_file=""

printf 'Backup created and validated:\n%s\n' "$output_file"
du -h "$output_file"
