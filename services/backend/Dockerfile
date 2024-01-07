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

# Rust Tax Calc Module layer
COPY ./app/src/modules/tax/rst_tax_calculator/target/wheels/rst_tax_calculator-0.1.0-cp310-cp310-linux_x86_64.whl /backend/app/src/modules/tax/rst_tax_calculator/target/wheels/rst_tax_calculator-0.1.0-cp310-cp310-linux_x86_64.whl
RUN pip install /backend/app/src/modules/tax/rst_tax_calculator/target/wheels/rst_tax_calculator-0.1.0-cp310-cp310-linux_x86_64.whl

# Everything else - not actually required because of volume mount, but doesn't hurt
COPY ./app /backend/app
