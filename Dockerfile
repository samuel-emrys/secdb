FROM ubuntu:16.04
MAINTAINER Sam Dowling <samuel.dowling@protonmail.com>

RUN apt-get update && apt-get install -y apt-utils apt-transport-https debconf-utils build-essential libssl-dev sudo
RUN apt-get upgrade -y

RUN mkdir -p /appfiles
WORKDIR /appfiles
COPY . .

RUN apt-get install -y postgresql postgresql-contrib
RUN apt-get install -y python3 python3-pip python3-dev python3-psycopg2

RUN pip3 install --upgrade pip
#RUN pip3 install -r requirements.txt

RUN apt-get install -y nano

# install necessary locales
RUN apt-get update && apt-get install -y locales \
    && echo "en_AU.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

# Set the locale
RUN sed -i -e 's/# en_AU.UTF-8 UTF-8/en_AU.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_AU.UTF-8
ENV LANGUAGE en_AU:en
ENV LC_ALL en_AU.UTF-8

