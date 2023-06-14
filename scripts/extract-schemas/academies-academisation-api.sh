#!/bin/bash

SERVICE=academies-academisation-api
COMPOSE_NAME=academisation_api

source ./scripts/extract-schemas/_helper.sh

${COMPOSE_CMD} up --no-deps -d "${COMPOSE_NAME}"
${COMPOSE_CMD} cp "${COMPOSE_NAME}":/app/SQL/DbMigrationScript.sql "${DUMPS_DIR}/schema-extraction-${SERVICE}.sql"

DEFAULT_SCHEMA=mstr
grep -h "ToTable(" "${REPO_DIR}/Dfe.Academies.Academisation.Data/Academies/AcademiesContext.cs" \
    | sed -nr "s/.*ToTable\(\"([^\"]*)\".*/CREATE TABLE [${DEFAULT_SCHEMA}].[\1] (/p" \
    >> "${DUMPS_DIR}/schema-extraction-${SERVICE}.sql"
