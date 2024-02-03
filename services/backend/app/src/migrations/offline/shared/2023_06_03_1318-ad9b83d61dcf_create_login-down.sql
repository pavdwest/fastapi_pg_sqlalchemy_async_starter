BEGIN;
    DROP TABLE shared.login;

    UPDATE alembic_version SET version_num='8b97a0c567f2' WHERE alembic_version.version_num = 'ad9b83d61dcf';
COMMIT;
