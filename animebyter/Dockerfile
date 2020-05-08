FROM python:alpine3.7

RUN apk add build-base
RUN apk add libffi-dev
RUN apk add openssl-dev
RUN apk add python3-dev

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ENV PYTHONUNBUFFERED=0 
ENV interval 300
EXPOSE 5000

COPY . /app
WORKDIR /app

CMD python3 main.py
