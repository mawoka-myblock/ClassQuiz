# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

CONTAINER_BIN=podman

run_tests() {
  pipenv run coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests
}

stop() {
  $CONTAINER_BIN container stop classquiz_db --time 2
  $CONTAINER_BIN container stop test_redis --time 2
  $CONTAINER_BIN container stop test_meili --time 2
  $CONTAINER_BIN rm classquiz_db --force
  $CONTAINER_BIN rm test_redis --force
  $CONTAINER_BIN rm test_meili --force
}

init() {
  if [ ! -d /tmp/storage ]; then
    mkdir /tmp/storage
  fi

  $CONTAINER_BIN run --rm -d -p 6379:6379 --name test_redis docker.io/redis:buster
  $CONTAINER_BIN run -it --rm -d -p 7700:7700 --name test_meili docker.io/getmeili/meilisearch:v0.28.0
  $CONTAINER_BIN volume create classquiz_db_data
  $CONTAINER_BIN run --name classquiz_db -p 5432:5432 --rm -d -e POSTGRES_PASSWORD=mysecretpassword -v classquiz_db_data:/var/lib/postgresql/data -e POSTGRES_DB=classquiz docker.io/postgres
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
