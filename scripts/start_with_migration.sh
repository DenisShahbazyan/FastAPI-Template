#!/bin/bash

wait_for_db() {
    echo "$(date): Waiting for database to be ready..."
    local max_retries=30
    local count=0
    local wait_seconds=5

    local host=${DB__HOST:-db}
    local port=${DB__PORT:-5432}
    local user=${DB__USERNAME:-postgres}
    local db_name=${DB__NAME:-postgres}

    while [ $count -lt $max_retries ]; do
        pg_isready -h $host -p $port -U $user -d $db_name -t 1 > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "$(date): Database is ready!"
            return 0
        fi
        echo "$(date): Database not ready. Waiting $wait_seconds seconds... (Attempt $((count+1)) of $max_retries)"
        count=$((count+1))
        sleep $wait_seconds
    done

    echo "$(date): Database connection timed out after $max_retries attempts."
    return 1
}

run_migration() {
    local retries=3
    local count=0
    local delay=30

    echo "$(date): Running alembic migration..."
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "$(date): Migrations applied successfully."
        return 0
    fi

    echo "$(date): Initial migration attempt failed. Will retry a few times."
    while [ $count -lt $retries ]; do
        echo "$(date): Retrying migration. Attempt $((count+1)) of $retries. Waiting $delay seconds..."
        sleep $delay

        alembic upgrade head
        if [ $? -eq 0 ]; then
            echo "$(date): Migrations applied successfully on retry."
            return 0
        fi

        echo "$(date): Migration retry failed. Attempt $((count+1)) of $retries."
        count=$((count+1))
    done

    echo "$(date): Migration failed after $retries retry attempts. Exiting."
    return 1
}

wait_for_db || { echo "Cannot connect to database. Exiting."; exit 1; }

run_migration || exit 1

exec ./scripts/start.sh
