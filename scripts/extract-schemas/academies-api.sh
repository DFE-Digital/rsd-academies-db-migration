#!/bin/bash

set -e

SERVICE=academies-api
SERVICES_REPO_DIR=$1

if [ -z "$1" ]; then
    echo "No repository directory supplied"
    exit 1
fi

cd "${SERVICES_REPO_DIR}/${SERVICE}"
rm -f "schema-extraction-${SERVICE}.sql"

cp .env.example .env.development
cp .env.database.example .env.database
docker compose build webapi

docker compose up --no-deps -d webapi
docker compose cp webapi:/app/SQL/DbMigrationScriptLegacy.sql "schema-extraction-${SERVICE}.legacy.sql"
docker compose cp webapi:/app/SQL/DbMigrationScript.sql "schema-extraction-${SERVICE}.sql"

cat "schema-extraction-${SERVICE}.legacy.sql" >> "schema-extraction-${SERVICE}.sql"
rm "schema-extraction-${SERVICE}.legacy.sql"

DEFAULT_SCHEMA=sdd
sed -i '' -r -e "s/CREATE TABLE \[([^\[]*)\] \(/CREATE TABLE [${DEFAULT_SCHEMA}].[\1] (/" "schema-extraction-${SERVICE}.sql"

docker compose down --remove-orphans --volumes
