#!/bin/bash

set -e

SERVICE=dfe-complete-conversions-transfers-and-changes
SERVICES_REPO_DIR=$1

if [ -z "$1" ]; then
    echo "No repository directory supplied"
    exit 1
fi

cd "${SERVICES_REPO_DIR}/${SERVICE}"
rm -f "schema-extraction-${SERVICE}.sql"

docker compose -f docker-compose.ci.yml build
docker compose -f docker-compose.ci.yml run --rm test echo "Creating DB by running entrypoint once"

SQL_DB_TABLES=$(docker compose -f docker-compose.ci.yml run --rm --entrypoint "" test bundle exec rails runner "puts ActiveRecord::Base.connection.tables")
echo "Found Rails schema: ${SQL_DB_TABLES}"
echo "${SQL_DB_TABLES}" > "db-extraction-${SERVICE}.txt"

DEFAULT_SCHEMA=complete
cat "db-extraction-${SERVICE}.txt" \
    | sed -r "s/(.*)/CREATE TABLE [${DEFAULT_SCHEMA}].[\1] (/" \
    > "schema-extraction-${SERVICE}.sql"
rm "db-extraction-${SERVICE}.txt"

docker compose -f docker-compose.ci.yml down --remove-orphans --volumes
