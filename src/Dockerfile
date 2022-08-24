# syntax=docker/dockerfile:1
FROM amsterdam/gob_wheelhouse:3.9-buster as wheelhouse
MAINTAINER datapunt@amsterdam.nl


# Application stage.
FROM amsterdam/gob_baseimage:3.9-buster as application
MAINTAINER datapunt@amsterdam.nl
# GOB base image: SQL Server driver.

# Fill the wheelhouse.
COPY --from=wheelhouse /opt/wheelhouse /opt/wheelhouse

# Install StUF service in /app folder.
WORKDIR /app

# Install required Python packages.
COPY requirements.txt /app/
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install --no-cache-dir \
	--find-links /opt/wheelhouse --requirement requirements.txt
RUN rm requirements.txt
# Wheelhouse cleanup.
RUN rm -rf /opt/wheelhouse

# Custom certs.
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
COPY *.crt /usr/local/share/ca-certificates/extras/
RUN chmod 755 /usr/local/share/ca-certificates/extras && \
	chmod 644 /usr/local/share/ca-certificates/extras/* && update-ca-certificates

# Create directory for client certs (datapunt Openstack).
RUN mkdir -p /certs/gob/ && chmod -R 755 /certs

# OAuth2 Proxy.
COPY ./oauth2-proxy oauth2-proxy
COPY ./oauth2-proxy.cfg oauth2-proxy.cfg
RUN chmod 755 oauth2-proxy
RUN mkdir -p /var/log/oauth2-proxy && chown datapunt /var/log/oauth2-proxy
RUN ./oauth2-proxy --version

# Copy gobstuf module.
COPY gobstuf gobstuf

# Create downloaded dir for regression tests with correct permissions
RUN mkdir -p /app/gobstuf/regression_tests/downloaded
RUN chown datapunt /app/gobstuf/regression_tests/downloaded

USER datapunt

CMD uwsgi


# Development.
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


# Test.
FROM application as test
USER root
# Remove gobcore tests
RUN rm -rf /app/src/gobcore/tests
RUN rm -rf /app/src/gobconfig/tests
# flask-audit-log cleanup.
RUN rm -rf /app/src/datapunt-flask-audit-log/tests

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh

# Copy Jenkins files.
COPY .jenkins /.jenkins
RUN mkdir -p /app/shared && chown datapunt /app/shared
USER datapunt
