BEGIN;
    CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    );
    CREATE SCHEMA shared;
    CREATE SCHEMA tenant_00000000_0000_0000_0000_000000000000;

    INSERT INTO alembic_version (version_num) VALUES ('0c06b1b456e1') RETURNING alembic_version.version_num;
COMMIT;
