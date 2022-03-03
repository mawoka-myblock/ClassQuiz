FROM python:3.10-slim
COPY classquiz/ /app/classquiz/
COPY init_db.py /app/
COPY *start.sh /app/
COPY gunicorn_conf.py /app/

COPY Pipfile* /app/
WORKDIR /app/
RUN pip install pipenv && pipenv install --system
EXPOSE 80
ENV PYTHONPATH=/app
RUN chmod +x start.sh
ENV APP_MODULE=classquiz:app
CMD ["./start.sh"]