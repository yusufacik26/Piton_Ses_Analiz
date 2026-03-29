CREATE TABLE IF NOT EXISTS audio_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    data BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS audio_metadata (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES audio_files(id),
    device_id VARCHAR(100),
    duration FLOAT,
    created_at TIMESTAMP
);