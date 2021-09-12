FROM python:3.9.2

ENV PYTHONUNBUFFERED 1
RUN apt-get -y update

RUN mkdir /slack-api
ADD . /slack-api

WORKDIR /slack-api

RUN pip install --upgrade pip
RUN pip install -r requirements.txt