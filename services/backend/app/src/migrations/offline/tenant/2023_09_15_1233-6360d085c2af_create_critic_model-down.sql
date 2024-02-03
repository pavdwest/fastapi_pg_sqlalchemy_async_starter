BEGIN;
    DROP TABLE tenant_00000000_0000_0000_0000_000000000000.critic;

    UPDATE alembic_version SET version_num='7ca3376e6937' WHERE alembic_version.version_num = '6360d085c2af';
COMMIT;
