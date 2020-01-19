FROM python:3.7

RUN apt-get update && apt-get -y install software-properties-common \
    && apt-get update -qq && apt-get -y install python-pip python-dev \
    libpq-dev postgresql postgresql-contrib gettext binutils libproj-dev \
    gdal-bin postgis netcat

# Copying project requirements to install before moving all project, 
# reduce the number of steps to rebuild always change project files. 
COPY ./requirements.txt /applada-api/requirements.txt

WORKDIR /applada-api

RUN pip install -r requirements.txt

COPY . /applada-api

RUN mv wait-for /bin/wait-for && chmod a+x /bin/wait-for

EXPOSE 80

CMD ["/bin/bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:80"]
