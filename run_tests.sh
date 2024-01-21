# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

CONTAINER_BIN=podman

run_tests() {
  pipenv run coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests
}

stop() {
  $CONTAINER_BIN container stop classquiz_db
  $CONTAINER_BIN container stop test_redis
  $CONTAINER_BIN container stop test_meili
}

init() {
  mkdir /tmp/storage
  $CONTAINER_BIN run --rm -d -p 6379:6379 --name test_redis redis:alpine
  $CONTAINER_BIN run -it --rm -d -p 7700:7700 --name test_meili getmeili/meilisearch:v0.28.0
  $CONTAINER_BIN volume create classquiz_db_data
  $CONTAINER_BIN run --name classquiz_db -p 5432:5432 --rm -d -e POSTGRES_PASSWORD=mysecretpassword -v classquiz_db_data:/var/lib/postgresql/data -e POSTGRES_DB=classquiz postgres
  sleep 1
  pipenv run alembic upgrade head
}

case $1 in
+) init ;;
-) stop ;;
a)
  $CONTAINER_BIN volume rm classquiz_db_data
  init
  run_tests
  stop
  ;;
prepare)
  stop
  $CONTAINER_BIN volume rm classquiz_db_data
  init
  ;;
*)
  echo "Invalid option: -$OPTARG" >&2
  exit 1
  ;;
esac
