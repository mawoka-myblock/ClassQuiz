FROM python:3.10-slim


COPY Pipfile* /app/
WORKDIR /app/
RUN pip install pipenv && pipenv install --system

COPY classquiz/ /app/classquiz/
COPY import_to_meili.py /app/import_to_meili.py
COPY alembic.ini /app/
COPY migrations/ /app/migrations/
COPY init_db.py /app/
COPY *start.sh /app/
COPY gunicorn_conf.py /app/


EXPOSE 80
ENV PYTHONPATH=/app
RUN chmod +x start.sh
ENV APP_MODULE=classquiz:app
CMD ["./start.sh"]
