FROM python:3.8-slim

COPY requirements.txt requirements.txt
COPY config.json config.json
RUN apt-get -y update
RUN apt-get -y install git
# ^^ Git required to install packages from a git url
RUN pip3 install -r requirements.txt
ENV DISCORD_BOT_CONFIG_PATH=/config.json
WORKDIR /src
COPY src .

CMD [ "python3", "main.py" ]