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

CMD sh -c "python manage.py migrate contenttypes --noinput && python manage.py migrate auth --noinput && python manage.py migrate admin --noinput && python manage.py migrate sessions --noinput && python manage.py migrate movies --fake --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 config.wsgi:application"
