FROM python:3.6-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update \
  # dependencies for building Python packages
  && apt install -y build-essential python-dev \
  # curl for node (TODO: GN check if needed)
  curl \
  # psycopg2 dependencies
  libpq-dev \
  # lxml dependencies (TODO: GN check if needed)
  libldap2-dev libsasl2-dev ldap-utils \
  libxml2-dev libxslt-dev \
  python3-lxml \
  # gdal libraries (TODO: GN check if needed)
  binutils libproj-dev gdal-bin \
  # cairo (html -> pdf, for print-friendly formats)
  libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements/
#COPY ./ddhldap/requirements.txt /requirements/ddhldap/
#COPY ./wagtailbase/requirements.txt /requirements/wagtailbase/
#COPY  ./wagtailbiblio/requirements.txt /requirements/wagtailbiblio/
RUN pip install -U pip \
  && pip install -r /requirements/requirements.txt

COPY ./compose/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

WORKDIR /app

ENTRYPOINT ["/entrypoint"]