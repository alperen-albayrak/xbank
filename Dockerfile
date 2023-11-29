FROM python:3.11.5
LABEL authors="alperenalbayrak"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir xbank
COPY requirements.txt /xbank
# install python dependencies
RUN pip install --upgrade pip
WORKDIR /xbank
RUN pip install --no-cache-dir -r requirements.txt

COPY . /xbank