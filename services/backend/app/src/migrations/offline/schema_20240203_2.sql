BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO alembic_version (version_num) VALUES ('0c06b1b456e1') RETURNING alembic_version.version_num;

-- Running upgrade  -> 8b97a0c567f2

CREATE TABLE shared.tenant (
    id BIGSERIAL NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    identifier VARCHAR NOT NULL,
    schema_name VARCHAR,
    PRIMARY KEY (id),
    UNIQUE (identifier)
);

UPDATE alembic_version SET version_num='8b97a0c567f2' WHERE alembic_version.version_num = '0c06b1b456e1';

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

-- Running upgrade ad9b83d61dcf -> 7ca3376e6937

CREATE TABLE tenant.book (
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

-- Running upgrade 7ca3376e6937 -> 6360d085c2af

CREATE TABLE tenant.critic (
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

-- Running upgrade 6360d085c2af -> 829f639ffb10

CREATE TABLE tenant.review (
    title VARCHAR NOT NULL,
    critic_id BIGINT NOT NULL,
    book_id BIGINT NOT NULL,
    rating INTEGER NOT NULL,
    body VARCHAR,
    id BIGSERIAL NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(book_id) REFERENCES tenant.book (id),
    FOREIGN KEY(critic_id) REFERENCES tenant.critic (id),
    CONSTRAINT "uc_Review_CriticId_BookId" UNIQUE (critic_id, book_id)
);

UPDATE alembic_version SET version_num='829f639ffb10' WHERE alembic_version.version_num = '6360d085c2af';

COMMIT;
