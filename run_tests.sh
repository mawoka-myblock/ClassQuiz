run_tests() {
  pipenv run coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests
}

stop() {
  docker container stop test_redis
  docker container stop test_meili
}

init() {
  mkdir /tmp/storage
  docker run --rm -d -p 6379:6379 --name test_redis redis:alpine
  docker run -it --rm -d -p 7700:7700 --name test_meili getmeili/meilisearch:latest
  pipenv run alembic upgrade head
}

case $1 in
+) init ;;
-) stop ;;
a)
  rm classquiz.db
  init
  run_tests
  stop
  ;;
*)
  echo "Invalid option: -$OPTARG" >&2
  exit 1
  ;;
esac
