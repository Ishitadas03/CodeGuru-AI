-- Enable pgvector extension and create vector_chunks table for RAG embeddings.
-- Run this in Supabase SQL Editor or via migration before deploying to Vercel.

-- 1. Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the vector_chunks table
CREATE TABLE IF NOT EXISTS vector_chunks (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    page INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding vector(384) NOT NULL
);

-- 3. Create indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_vector_chunks_user_id ON vector_chunks (user_id);
CREATE INDEX IF NOT EXISTS idx_vector_chunks_document_id ON vector_chunks (document_id);

-- 4. Create IVFFlat index for approximate nearest neighbor search
-- Note: This requires at least 100 rows. For initial deployment, you can skip this
-- and create it after ingesting some documents:
--   CREATE INDEX idx_vector_chunks_embedding ON vector_chunks
--     USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
--
-- For small datasets (<1000 vectors), use exact search (no IVFFlat index needed).

-- 5. Row Level Security (RLS) — users can only access their own vectors
ALTER TABLE vector_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own vectors"
    ON vector_chunks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own vectors"
    ON vector_chunks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own vectors"
    ON vector_chunks FOR DELETE
    USING (auth.uid() = user_id);
