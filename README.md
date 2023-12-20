# Overview

An auto-initialised dockerised starter stack containing the following components (all on latest versions):

* FastAPI backend with single & bulk CRUD endpoints
* Postgres 16 database
* SQLAlchemy 2.0+ ORM (Async)
* Alembic Migrations (with auto-migrate on db create)
* Pydantic Validations
* Pytests with new DB created for each run

Project homepage: [https://github.com/pavdwest/fastapi_pg_sqlalchemy_async_starter](https://github.com/pavdwest/fastapi_pg_sqlalchemy_async_starter)

# Requirements

* [Docker](https://www.docker.com/)
* Git (optional but recommended)

# Getting Started

1. Clone repo:

    ```git clone git@github.com:pavdwest/fastapi_pg_sqlalchemy_async_starter.git```

2. Enter directory:

    ```cd fastapi_pg_sqlalchemy_async_starter```

3. (Optional) Create & activate virtual environment for local development:

    ```python -m venv services/backend/app/.ignore/venv && source services/backend/app/.ignore/venv/bin/activate```

4. (Optional) Install dependencies for local development/intellisense:

    ```pip install -r services/backend/app/requirements/base.txt```

5. Run stack (we attach only to the backend as we don't want to listen to PGAdmin4 spam):

    ```docker compose up --build --attach backend```

6. Everything's running:

    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

7. Run migrations with Alembic (if you want the Books model for testing/demo purposes):

     ```docker compose exec backend alembic upgrade head```

# Notes

## Set up Alembic from scratch:

1. Init

    ```docker compose exec backend alembic init -t async src/migrations```

2. Setup DB config

See changes to ```services/backend/app/src/migrations/env.py```

3. Create first migration

    ```docker compose exec backend alembic revision -m "Init" --autogenerate```

4. Run first migration

     ```docker compose exec backend alembic upgrade head```

## PGAdmin4

You can access PGAdmin4 at [http://127.0.0.1:5050](http://127.0.0.1:5050).

See the `pgadmin` service in the ```docker-componse.yml``` file for credentials.

Once you've logged into PGAdmin add the db server using the details as per `db` service in the ```docker-componse.yml```. **_Tip: Host name/address is `db` (name of the service) by default._**

## Adding a New Model

A note on conventions: https://stackoverflow.com/questions/4702728/relational-table-naming-convention/4703155#4703155

1. Add folder to ```services/backend/app/src/modules```

    `.../models/my_model/routes.py`         for the endpoints

    `.../models/my_model/models.py`         for the SQLAlchemy model

    `.../models/my_model/validators.py`     for the Pydantic validators

2. Import models to ```services/backend/app/src/migrations/env.py```

3. Create migration:

    ```docker exec -it fastapi_pg_sqlalchemy-backend-1 alembic revision --autogenerate -m "Add MyModel"```

4. Run migration:

    ```docker exec -it fastapi_pg_sqlalchemy-backend-1 alembic upgrade head"```

# Further Considerations

## Logging solution

TODO

## Task Queues & Workers

Most likely Redis/RabbitMQ/Celery

## Multi-Tenancy

There is currently no concept of multi-tenancy. Will likely implement multi-tenancy at schema (most likely the best middle-ground between separation and amount of admin) or database level. Row-level separation makes me uncomfortable for a number of reasons.

# Auditing

TODO

## Authentication/Authorization

TODO

## Append-Only vs. Standard CRUD

Currently uses all operations, create, read, update and delete. Might consider create only, but that brings with it its own slew of complications. Does simplify write-scalability and auditing.
