CREATE EXTENSION IF NOT EXISTS vector;

--- The recipe catalog
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    tags TEXT,
    ingredients TEXT,
    direction TEXT,
    embedding vector(384)
);

---Conversation History with Metadata
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    model TEXT,
    recipe_ids INT[],     ---recipe ids sent to LLM
    prompt_tokens INT,
    response_tokens INT,
    cost_usd NUMERIC(10,6),
    response_seconds REAL,
    feedback INT,         --- +1 thumbs up , -1 thumbs down, NULL no response
    created_at TIMESTAMPTZ DEFAULT now()
);