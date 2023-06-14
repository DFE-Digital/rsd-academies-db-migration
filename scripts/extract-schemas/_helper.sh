set -e

SERVICES_REPO_DIR=$1
REPO_DIR="${SERVICES_REPO_DIR}/${SERVICE}"
DUMPS_DIR="${REPO_DIR}/_sql_dumps"
COMPOSE_CMD="docker compose -f services.compose.yml"

if [ -z "$1" ]; then
    echo "No repository directory supplied"
    exit 1
fi

rm -rf "${DUMPS_DIR}"

${COMPOSE_CMD} build "${COMPOSE_NAME}"

mkdir -p "${DUMPS_DIR}"
