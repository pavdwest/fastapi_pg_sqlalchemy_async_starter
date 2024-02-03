BEGIN;
    -- Running upgrade 8b97a0c567f2 -> ad9b83d61dcf

    CREATE TABLE shared.login (
        hashed_password VARCHAR NOT NULL,
        verification_token UUID NOT NULL,
        verified BOOLEAN NOT NULL,
        identifier VARCHAR NOT NULL,
        tenant_schema_name VARCHAR,
        id BIGSERIAL NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (identifier),
        UNIQUE (verification_token)
    );

    UPDATE alembic_version SET version_num='ad9b83d61dcf' WHERE alembic_version.version_num = '8b97a0c567f2';
COMMIT;
