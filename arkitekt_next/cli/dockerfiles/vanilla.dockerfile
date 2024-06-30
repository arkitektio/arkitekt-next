FROM python:3.8-slim-buster

RUN pip install "arkitekt_next[all]>=0.7.a7"

RUN mkdir /app
WORKDIR /app
COPY .arkitekt_next /app/.arkitekt_next
COPY app.py /app/app.py
