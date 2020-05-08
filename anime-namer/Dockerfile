FROM python:3.7

RUN pip3 install flask requests

COPY . /app
WORKDIR /app
ENV PORT=9010

CMD python3 app.py
