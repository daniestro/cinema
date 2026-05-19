FROM python:3.10-alpine

RUN apk add --no-cache postgresql-libs gettext jpeg zlib \
    && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev jpeg-dev zlib-dev \
    && pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir \
    && apk --purge del .build-deps

WORKDIR /app

COPY ./manage.py /app/
COPY ./config /app/config
COPY ./movies /app/movies
COPY ./seed_data.sql /app/seed_data.sql
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
