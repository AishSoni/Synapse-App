-- Synapse Captures Table Schema
-- Run this in your Supabase SQL Editor

-- Drop tables if exists (be careful in production!)
-- DROP TABLE IF EXISTS capture_chunks CASCADE;
-- DROP TABLE IF EXISTS captures CASCADE;

-- Main captures table with comprehensive metadata
CREATE TABLE IF NOT EXISTS captures (
    -- Core identifiers
    id UUID PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Visual data
    screenshot TEXT,  -- Base64 encoded image

    -- Content analysis (from LLM)
    content_type TEXT NOT NULL,  -- product, video, article, code, etc.
    summary TEXT,                -- 1-2 sentence summary
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Array of tags

    -- Structured metadata (JSON)
    metadata JSONB DEFAULT '{}'::JSONB,  -- Product prices, video duration, etc.
    key_points TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Key takeaways
    entities JSONB DEFAULT '{}'::JSONB,  -- People, places, technologies

    -- Content storage
    html_excerpt TEXT,   -- First 5k chars of HTML
    clean_content TEXT,  -- Cleaned text content

    -- Visual analysis (from screenshot)
    visual_analysis JSONB DEFAULT NULL,  -- UI elements, colors, detected text

    -- Full scraped content (comprehensive)
    full_html TEXT,          -- Complete HTML
    full_text TEXT,          -- All extracted text
    main_content TEXT,       -- Main article/content
    word_count INTEGER,      -- Total words

    -- Platform-specific data
    platform TEXT,           -- youtube, twitter, arxiv, web, etc.
    platform_metadata JSONB DEFAULT '{}'::JSONB,  -- Platform-specific fields

    -- Structured data
    structured_data JSONB DEFAULT '[]'::JSONB,  -- JSON-LD, microdata
    links JSONB DEFAULT '[]'::JSONB,            -- Extracted links
    images_data JSONB DEFAULT '[]'::JSONB,      -- Extracted images

    -- Search optimization
    search_vector tsvector  -- For full-text search
);

-- Content chunks table (for long pages)
CREATE TABLE IF NOT EXISTS capture_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capture_id UUID REFERENCES captures(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,

    -- Chunk content
    heading TEXT,            -- Section heading if available
    chunk_text TEXT NOT NULL,
    word_count INTEGER,

    -- Position in document
    start_position INTEGER,
    end_position INTEGER,

    -- Search
    search_vector tsvector,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ensure unique chunks per capture
    UNIQUE(capture_id, chunk_index)
);

-- Indexes for captures
CREATE INDEX IF NOT EXISTS idx_captures_created_at ON captures(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_captures_content_type ON captures(content_type);
CREATE INDEX IF NOT EXISTS idx_captures_platform ON captures(platform);
CREATE INDEX IF NOT EXISTS idx_captures_tags ON captures USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_captures_metadata ON captures USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_captures_platform_metadata ON captures USING GIN(platform_metadata);
CREATE INDEX IF NOT EXISTS idx_captures_search ON captures USING GIN(search_vector);

-- Indexes for chunks
CREATE INDEX IF NOT EXISTS idx_chunks_capture_id ON capture_chunks(capture_id);
CREATE INDEX IF NOT EXISTS idx_chunks_search ON capture_chunks USING GIN(search_vector);

-- Create search vector triggers
CREATE OR REPLACE FUNCTION captures_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.main_content, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER captures_search_vector_trigger
    BEFORE INSERT OR UPDATE ON captures
    FOR EACH ROW
    EXECUTE FUNCTION captures_search_vector_update();

-- Chunks search vector trigger
CREATE OR REPLACE FUNCTION chunks_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.heading, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.chunk_text, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chunks_search_vector_trigger
    BEFORE INSERT OR UPDATE ON capture_chunks
    FOR EACH ROW
    EXECUTE FUNCTION chunks_search_vector_update();

-- Create view for mind map display
CREATE OR REPLACE VIEW mind_map_nodes AS
SELECT
    id,
    url,
    title,
    content_type,
    tags,
    summary,
    metadata,
    screenshot,
    created_at,
    -- Extract specific metadata fields for easy access
    metadata->>'price' as price,
    metadata->>'currency' as currency,
    metadata->>'author' as author,
    metadata->>'duration' as duration,
    metadata->>'rating' as rating
FROM captures
ORDER BY created_at DESC;

-- Sample queries for testing

-- Get all products with prices
-- SELECT * FROM captures WHERE content_type = 'product' AND metadata->>'price' IS NOT NULL;

-- Get recent videos
-- SELECT * FROM captures WHERE content_type = 'video' ORDER BY created_at DESC LIMIT 10;

-- Search by tag
-- SELECT * FROM captures WHERE 'python' = ANY(tags);

-- Full-text search
-- SELECT * FROM captures WHERE search_vector @@ to_tsquery('english', 'machine & learning');

-- Get captures by date range
-- SELECT * FROM captures WHERE created_at >= NOW() - INTERVAL '7 days';

-- Count by content type
-- SELECT content_type, COUNT(*) FROM captures GROUP BY content_type ORDER BY COUNT(*) DESC;
