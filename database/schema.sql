CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    content TEXT,
    source VARCHAR(50),
    timestamp TIMESTAMP,
    project VARCHAR(100),
    theme VARCHAR(100),
    emotion VARCHAR(50),
    transformed_output TEXT
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    auth0_id VARCHAR(100),
    email VARCHAR(255),
    subscription VARCHAR(50)
); 