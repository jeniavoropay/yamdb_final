FROM --platform=linux/amd64 python:3.7-slim

WORKDIR /app

COPY requirements.txt /app

RUN apt update && apt install -y gcc libpq-dev

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]