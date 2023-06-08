#!/bin/bash

set -e

SERVICE=amsd-casework
SERVICES_REPO_DIR=$1

if [ -z "$1" ]; then
    echo "No repository directory supplied"
    exit 1
fi

cd "${SERVICES_REPO_DIR}/${SERVICE}"
rm -f "schema-extraction-${SERVICE}.sql"

cp .env.development.local.example .env.development.local
cp .env.database.example .env.database
docker compose build webapi

docker compose up --no-deps -d webapi
docker compose cp webapi:/app/SQL/DbMigrationScript.sql "schema-extraction-${SERVICE}.sql"

docker compose down --remove-orphans --volumes
