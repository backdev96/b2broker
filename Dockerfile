FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install the necessary packages
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install -U --force-reinstall pip
ENV DJANGO_SETTINGS_MODULE=src.settings
COPY /src /src
WORKDIR /src
RUN pip3 install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000
