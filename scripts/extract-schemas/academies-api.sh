#!/bin/bash

SERVICE=academies-api
COMPOSE_NAME=academies_api

source ./scripts/extract-schemas/_helper.sh

${COMPOSE_CMD} up --no-deps -d "${COMPOSE_NAME}"
${COMPOSE_CMD} cp "${COMPOSE_NAME}":/app/SQL/DbMigrationScriptLegacy.sql "${DUMPS_DIR}/db-extraction-${SERVICE}.legacy.sql"
${COMPOSE_CMD} cp "${COMPOSE_NAME}":/app/SQL/DbMigrationScript.sql "${DUMPS_DIR}/db-extraction-${SERVICE}.sql"

cat "${DUMPS_DIR}/db-extraction-${SERVICE}.legacy.sql" >> "${DUMPS_DIR}/db-extraction-${SERVICE}.sql"
rm "${DUMPS_DIR}/db-extraction-${SERVICE}.legacy.sql"

DEFAULT_SCHEMA=sdd
cat "${DUMPS_DIR}/db-extraction-${SERVICE}.sql" \
    | sed -r "s/CREATE TABLE \[([^\[]*)\] \(/CREATE TABLE [${DEFAULT_SCHEMA}].[\1] (/" \
    > "${DUMPS_DIR}/schema-extraction-${SERVICE}.sql"
rm "${DUMPS_DIR}/db-extraction-${SERVICE}.sql"
