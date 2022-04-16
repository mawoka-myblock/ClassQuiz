docker run --rm -d -p 6379:6379 --name test_redis redis:alpine
python3 init_db.py
coverage run -m pytest -s -v --asyncio-mode=strict classquiz/tests/test_users.py
rm classquiz.db
docker container stop test_redis
