FROM python:3.10

WORKDIR /etl

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
