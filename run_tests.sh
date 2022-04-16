docker run --rm -d -p 6379:6379 --name test_redis redis:alpine
python3 init_db.py
coverage run -m pytest -s -v --asyncio-mode=strict --cache-clear classquiz/tests
rm classquiz.db
docker container stop test_redis
