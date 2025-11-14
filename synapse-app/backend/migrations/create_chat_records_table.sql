-- Chat Records Table
-- Stores summaries of AI chat conversations from external apps

CREATE TABLE IF NOT EXISTS chat_records (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    source_app TEXT DEFAULT 'Unknown',
    content_type TEXT DEFAULT 'chat',
    tags TEXT[] DEFAULT '{}',
    word_count INTEGER DEFAULT 0,
    text_preview TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_chat_records_created_at ON chat_records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_records_source_app ON chat_records(source_app);
CREATE INDEX IF NOT EXISTS idx_chat_records_tags ON chat_records USING GIN(tags);

-- Comment
COMMENT ON TABLE chat_records IS 'Stores AI chat conversation summaries from external apps for Synapse second brain';
