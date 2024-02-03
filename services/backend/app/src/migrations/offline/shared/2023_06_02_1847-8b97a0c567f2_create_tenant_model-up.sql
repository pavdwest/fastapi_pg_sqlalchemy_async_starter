BEGIN;
    -- Running upgrade  -> 8b97a0c567f2

    CREATE TABLE shared.tenant (
        id BIGSERIAL NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        identifier VARCHAR NOT NULL,
        schema_name VARCHAR,
        PRIMARY KEY (id),
        UNIQUE (identifier)
    );

    UPDATE alembic_version SET version_num='8b97a0c567f2' WHERE alembic_version.version_num = '0c06b1b456e1';
COMMIT;
