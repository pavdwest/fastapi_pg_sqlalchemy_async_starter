BEGIN;
    DROP TABLE shared.tenant;

    UPDATE alembic_version SET version_num='0c06b1b456e1' WHERE alembic_version.version_num = '0c06b1b456e1';
COMMIT;
