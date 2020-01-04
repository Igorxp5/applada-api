FROM python:3.7-slim

RUN apt-get update -qq && apt-get -y install python-pip python-dev libpq-dev postgresql postgresql-contrib

COPY . /applada-api

WORKDIR /applada-api

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["/bin/bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:80"]
