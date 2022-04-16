run_tests() {
  pipenv run coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests
}

stop() {
  rm classquiz.db
  docker container stop test_redis
  docker container stop test_meili
}

init() {
  mkdir /tmp/storage
  docker run --rm -d -p 6379:6379 --name test_redis redis:alpine
  docker run -it --rm -d -p 7700:7700 --name test_meili getmeili/meilisearch:latest
  pipenv run python3 init_db.py
}

case $1 in
+) init ;;
-) stop ;;
a)
  init
  run_tests
  stop
  ;;
*)
  echo "Invalid option: -$OPTARG" >&2
  exit 1
  ;;
esac
