FROM python:3.11.1-slim

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create dir /app
WORKDIR /app

# create venv
RUN python3 -m venv /opt/venv

COPY requirements.txt .

# setup requirements
RUN . /opt/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY . .

# add entry point command

RUN chmod a+x docker/*.sh

# RUN chmod +x ./docker-entrypoint.sh

# ENTRYPOINT ["/bin/bash", "-c", "./docker-entrypoint.sh"]