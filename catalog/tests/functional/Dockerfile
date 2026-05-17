FROM python:3.11

WORKDIR /tests/functional

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/tests"