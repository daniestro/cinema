FROM python:3.10.13-alpine3.17 

WORKDIR /opt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/opt/tests"

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . ./tests

ENTRYPOINT [ "pytest", "./tests/functional/src" ]