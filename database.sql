CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    country VARCHAR(50),
    plan VARCHAR(50) DEFAULT 'free',
    plan_expires_at TIMESTAMP,
    plan_requests_left INT DEFAULT 0,
    free_requests_today INT DEFAULT 0,
    last_free_request_at DATE
);

CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    prompt TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);