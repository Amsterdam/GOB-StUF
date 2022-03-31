FROM amsterdam/python:3.9-buster as application
MAINTAINER datapunt@amsterdam.nl

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

# Install StUF service in /app folder
WORKDIR /app

RUN apt-get install -y apt-transport-https

# Install SQL Server driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install GDAL
RUN apt-get install -y libgdal-dev

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install required Python packages
COPY requirements.txt /app/

# Install gdal separately from the rest of the python requirements.
# This avoids that changes to requirements.txt incure a time consuming gdal build
RUN LIBGDAL_VERSION=$(gdal-config --version) && pip3 install GDAL==${LIBGDAL_VERSION}
RUN LIBGDAL_VERSION=$(gdal-config --version) \
    pip3 install  \
    --trusted-host pypi.python.org  \
    --trusted-host pypi.org  \
    --trusted-host files.pythonhosted.org  \
    --no-cache-dir  \
    -r requirements.txt
RUN rm requirements.txt

COPY *.crt /usr/local/share/ca-certificates/extras/
RUN chmod -R 644 /usr/local/share/ca-certificates/extras/ \
 && update-ca-certificates

# Create directory for client certs
RUN mkdir -p /certs/gob/ && chmod -R 755 /certs

# Copy gob stuf module
COPY gobstuf gobstuf

# OAuth2 Proxy
COPY ./oauth2-proxy oauth2-proxy
COPY ./oauth2-proxy.cfg oauth2-proxy.cfg
RUN chmod 755 oauth2-proxy
RUN mkdir -p /var/log/oauth2-proxy && chown datapunt /var/log/oauth2-proxy
RUN ./oauth2-proxy --version

# Create downloaded dir for regression tests with correct permissions
RUN mkdir -p /app/gobstuf/regression_tests/downloaded
RUN chown datapunt /app/gobstuf/regression_tests/downloaded

USER datapunt

CMD uwsgi
FROM application as development
USER root
# Install GOB-Core and GOB-Config in development mode. Will be overridden with
# mounts from the developer filesystem. Changes made to GOB-Core and GOB-Config
# will be available immediately.
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Core.git
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install -e /app/GOB-Core
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Config.git
RUN pip install -e /app/GOB-Config
USER datapunt

FROM application as test
USER root
# Remove gobcore tests
RUN rm -rf /app/src/gobcore/tests
RUN rm -rf /app/src/gobconfig/tests
RUN rm -rf /app/src/datapunt-flask-audit-log/tests

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh

# Copy jenkins files
COPY .jenkins /.jenkins
RUN mkdir -p /app/shared && chown datapunt /app/shared
USER datapunt
