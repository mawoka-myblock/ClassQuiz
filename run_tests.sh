#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

run_tests() {
  pipenv run coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests
}

stop() {
  docker container stop test_redis
  docker container stop test_meili
  docker container stop classquiz_db
}

init() {
  mkdir /tmp/storage
  docker run --rm -d -p 6379:6379 --name test_redis redis:alpine
  docker run -it --rm -d -p 7700:7700 --name test_meili getmeili/meilisearch:v0.28.0
  docker volume create classquiz_db_data
  docker run --name classquiz_db -p 5432:5432 --rm -d -e POSTGRES_PASSWORD=mysecretpassword -v classquiz_db_data:/var/lib/postgresql/data -e POSTGRES_DB=classquiz postgres
  sleep 1
  pipenv run alembic upgrade head
}

case $1 in
+) init ;;
-) stop ;;
a)
  docker volume rm classquiz_db_data
  init
  run_tests
  stop
  ;;
prepare)
  stop
  docker volume rm classquiz_db_data
  init
  ;;
*)
  echo "Invalid option: -$OPTARG" >&2
  exit 1
  ;;
esac
