BEGIN;
    -- Running upgrade ad9b83d61dcf -> 7ca3376e6937

    CREATE TABLE tenant_00000000_0000_0000_0000_000000000000.book (
        author VARCHAR NOT NULL,
        release_year INTEGER,
        id BIGSERIAL NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        identifier VARCHAR NOT NULL,
        name VARCHAR,
        PRIMARY KEY (id),
        UNIQUE (identifier)
    );

    UPDATE alembic_version SET version_num='7ca3376e6937' WHERE alembic_version.version_num = 'ad9b83d61dcf';
COMMIT;
