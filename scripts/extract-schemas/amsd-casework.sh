#!/bin/bash

SERVICE=amsd-casework
COMPOSE_NAME=concerns

source ./scripts/extract-schemas/_helper.sh

${COMPOSE_CMD} up --no-deps -d "${COMPOSE_NAME}"
${COMPOSE_CMD} cp "${COMPOSE_NAME}":/app/SQL/DbMigrationScript.sql "${DUMPS_DIR}/schema-extraction-${SERVICE}.sql"
