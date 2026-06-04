-- Migration 003: friend requests and messages
CREATE TABLE IF NOT EXISTS friend_requests (
    id          BIGSERIAL PRIMARY KEY,
    sender_id   BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status      TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(sender_id, receiver_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id          BIGSERIAL PRIMARY KEY,
    sender_id   BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_friend_requests_receiver ON friend_requests(receiver_id, status);
CREATE INDEX IF NOT EXISTS idx_messages_pair ON messages(
    LEAST(sender_id, receiver_id),
    GREATEST(sender_id, receiver_id),
    created_at
);
