BEGIN;
    DROP TABLE tenant_00000000_0000_0000_0000_000000000000.review;

    UPDATE alembic_version SET version_num='6360d085c2af' WHERE alembic_version.version_num = '829f639ffb10';
COMMIT;
