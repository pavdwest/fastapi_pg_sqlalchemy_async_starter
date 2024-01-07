#!/usr/bin/env bash

(cd services/backend/app/src/modules/tax/rst_tax_calculator && maturin build --release --manylinux off --strip)
docker compose up --build --remove-orphans --force-recreate
