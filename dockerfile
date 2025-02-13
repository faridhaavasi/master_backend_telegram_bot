FROM python:3.10

WORKDIR /app

COPY requirments.txt ./

RUN pip install --no-cache-dir -r requirments.txt

COPY . .
