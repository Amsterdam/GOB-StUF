FROM python:3.11-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 DEBIAN_FRONTEND=noninteractive

# uWSGI build dependencies:
# - gcc
# - libpcre2-dev (regex parsing)
RUN apt-get update && apt-get install -y --no-install-recommends git gcc libpcre2-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

FROM python:3.11-slim-bookworm AS test

RUN useradd --user-group --system --no-create-home benktest

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY requirements-dev.txt requirements-dev.txt
RUN pip install -r requirements-dev.txt && rm requirements-dev.txt

COPY gobstuf gobstuf
COPY tests tests
COPY .flake8 test.sh ./

USER benktest
CMD ["bash", "-c", "./test.sh"]

FROM python:3.11-slim-bookworm AS application

WORKDIR /app

RUN useradd --user-group --system --no-create-home benk && \
    apt-get update && \
    apt-get install -y --no-install-recommends libpcre2-dev && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists

COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY --chmod=755 oauth2-proxy oauth2-proxy.sh ./
COPY oauth2-proxy.cfg ca-bundle.crt oauth2-proxy-entra.cfg oauth2-proxy-entra.yml ./
COPY gobstuf gobstuf

RUN mkdir -p /var/log/oauth2-proxy && chown benk /var/log/oauth2-proxy

USER benk
CMD uwsgi
