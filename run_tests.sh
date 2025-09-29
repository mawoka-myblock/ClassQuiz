# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

CONTAINER_BIN=podman

run_tests() {
  pipenv run coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests
}

stop() {
  $CONTAINER_BIN compose -f docker-compose.dev.yml down --volumes
}

init() {
  if [ ! -d /tmp/storage ]; then
    mkdir /tmp/storage
  fi
  $CONTAINER_BIN compose -f docker-compose.dev.yml up -d
  sleep 2
  pipenv run alembic upgrade head
}

case $1 in
+) init ;;
-) stop ;;
a)
  $CONTAINER_BIN volume rm classquiz_db
  init
  run_tests
  stop
  ;;
prepare)
  stop
  $CONTAINER_BIN volume rm classquiz_db
  init
  ;;
*)
  echo "Invalid option: -$OPTARG" >&2
  exit 1
  ;;
esac
