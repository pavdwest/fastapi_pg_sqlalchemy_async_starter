FROM python:3.10-slim

# Virtual Env
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /backend/app

RUN python3 -m venv /opt/venv

# Python dependencies layer
COPY ./app/requirements /backend/app/requirements
RUN pip install --no-cache-dir --upgrade pip -r /backend/app/requirements/base.txt

# Everything else - not actually required because of volume mount, but doesn't hurt
COPY ./app /backend/app
