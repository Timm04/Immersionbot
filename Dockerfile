FROM ubuntu:20.04

WORKDIR /Immersionbot

RUN apt-get update && \
    apt-get install -y python3 python3-pip

USER root

COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "launch_bot.py"]