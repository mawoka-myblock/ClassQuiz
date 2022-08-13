FROM python:3.10-slim

COPY Pipfile* /app/
WORKDIR /app/
RUN pip3 install --upgrade pip && \
    pip install packaging \
    pip install pipenv && \
    pipenv install --system

COPY classquiz/ /app/classquiz/
COPY image_cleanup.py /app/image_cleanup.py
COPY alembic.ini /app/
COPY migrations/ /app/migrations/
COPY *start.sh /app/
COPY gunicorn_conf.py /app/


EXPOSE 80
ENV PYTHONPATH=/app
RUN chmod +x start.sh
ENV APP_MODULE=classquiz:app
CMD ["./start.sh"]
