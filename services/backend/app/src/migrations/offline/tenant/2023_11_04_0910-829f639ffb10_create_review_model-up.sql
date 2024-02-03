BEGIN;
    -- Running upgrade 6360d085c2af -> 829f639ffb10

    CREATE TABLE tenant_00000000_0000_0000_0000_000000000000.review (
        title VARCHAR NOT NULL,
        critic_id BIGINT NOT NULL,
        book_id BIGINT NOT NULL,
        rating INTEGER NOT NULL,
        body VARCHAR,
        id BIGSERIAL NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(book_id) REFERENCES tenant_00000000_0000_0000_0000_000000000000.book (id),
        FOREIGN KEY(critic_id) REFERENCES tenant_00000000_0000_0000_0000_000000000000.critic (id),
        CONSTRAINT "uc_Review_CriticId_BookId" UNIQUE (critic_id, book_id)
    );

    UPDATE alembic_version SET version_num='829f639ffb10' WHERE alembic_version.version_num = '6360d085c2af';
COMMIT;
