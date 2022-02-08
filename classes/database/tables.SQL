

CREATE TABLE wallets(
    id SMALLSERIAL PRIMARY KEY,
    address TEXT UNIQUE NOT NULL,
    last_use TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE transactions(
    id SMALLSERIAL PRIMARY KEY,
    hash VARCHAR(64) UNIQUE NOT NULL,
    from_wallet VARCHAR(34) NOT NULL,
    to_wallet VARCHAR(34) NOT NULL,
    amount NUMERIC(8, 2),
    created_at TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE membership(
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    chat_id BIGINT NOT NULL,
    start_date TIMESTAMP DEFAULT current_timestamp,
    end_date TIMESTAMP NOT NULL,
    discord_invite VARCHAR(10),
    discord_id BIGINT
);