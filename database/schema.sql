CREATE TABLE ideas (
    id SERIAL PRIMARY KEY,
    content TEXT,
    source VARCHAR(50),
    timestamp TIMESTAMP,
    user_id VARCHAR(100),
    project VARCHAR(100),
    theme VARCHAR(100),
    emotion VARCHAR(50),
    transformed_output TEXT
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    auth0_id VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    subscription VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_ideas_user_id ON ideas(user_id);
CREATE INDEX idx_ideas_timestamp ON ideas(timestamp);
CREATE INDEX idx_ideas_project ON ideas(project);
CREATE INDEX idx_ideas_theme ON ideas(theme);
CREATE INDEX idx_ideas_emotion ON ideas(emotion);

-- Full-text search index
CREATE INDEX idx_ideas_content_fts ON ideas USING gin(to_tsvector('english', content));

-- Index for users table
CREATE INDEX idx_users_auth0_id ON users(auth0_id);
CREATE INDEX idx_users_email ON users(email); 