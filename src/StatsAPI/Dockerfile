FROM python:3.8-slim

COPY requirements.txt requirements.txt
COPY config.json config.json
RUN pip3 install -r requirements.txt
ENV STATS_API_CONFIG_PATH=/config.json
WORKDIR /src
COPY src .

CMD [ "python3", "main.py" ]