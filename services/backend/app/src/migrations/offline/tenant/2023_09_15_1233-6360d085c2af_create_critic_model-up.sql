BEGIN;
    -- Running upgrade 7ca3376e6937 -> 6360d085c2af

    CREATE TABLE tenant_00000000_0000_0000_0000_000000000000.critic (
        username VARCHAR NOT NULL,
        bio VARCHAR,
        id BIGSERIAL NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        name VARCHAR,
        PRIMARY KEY (id),
        UNIQUE (username)
    );

    UPDATE alembic_version SET version_num='6360d085c2af' WHERE alembic_version.version_num = '7ca3376e6937';
COMMIT;
