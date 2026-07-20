CREATE TABLE IF NOT EXISTS research_digests (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT,
    category TEXT,
    summary TEXT NOT NULL,
    risk_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
