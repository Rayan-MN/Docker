CREATE TABLE IF NOT EXISTS app_messages (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO app_messages (message)
VALUES ('PostgreSQL initialization completed');
