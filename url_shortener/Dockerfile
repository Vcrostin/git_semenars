FROM python:3.12.8-bookworm

WORKDIR /app

COPY requirements.txt .
RUN apt-get install libpq-dev
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
