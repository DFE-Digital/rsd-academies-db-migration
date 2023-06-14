#!/bin/bash

SERVICE=dfe-complete-conversions-transfers-and-changes
COMPOSE_NAME=complete

source ./scripts/extract-schemas/_helper.sh

${COMPOSE_CMD} run --rm "${COMPOSE_NAME}" echo "Creating DB by running entrypoint once"

SQL_DB_TABLES=$(${COMPOSE_CMD} run --rm --entrypoint "" "${COMPOSE_NAME}" bundle exec rails runner "puts ActiveRecord::Base.connection.tables")
echo "Found Rails schema: ${SQL_DB_TABLES}"
echo "${SQL_DB_TABLES}" > "${DUMPS_DIR}/db-extraction-${SERVICE}.txt"

grep -h "create_table" "${REPO_DIR}/db/schema.rb" \
    | sed -nr 's/.*create_table "([^"]*)".*/\1/p' \
    >> "${DUMPS_DIR}/db-extraction-${SERVICE}.txt"

DEFAULT_SCHEMA=complete
cat "${DUMPS_DIR}/db-extraction-${SERVICE}.txt" \
    | sed -r "s/(.*)/CREATE TABLE [${DEFAULT_SCHEMA}].[\1] (/" \
    > "${DUMPS_DIR}/schema-extraction-${SERVICE}.sql"
rm "${DUMPS_DIR}/db-extraction-${SERVICE}.txt"
