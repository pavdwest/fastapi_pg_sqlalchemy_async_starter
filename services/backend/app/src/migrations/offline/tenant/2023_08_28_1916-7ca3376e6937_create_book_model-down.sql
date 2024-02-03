BEGIN;
    DROP TABLE tenant_00000000_0000_0000_0000_000000000000.book;

    UPDATE alembic_version SET version_num='ad9b83d61dcf' WHERE alembic_version.version_num = '7ca3376e6937';
COMMIT;
