#!/bin/bash
set -e

echo "Initializing AION database with pgvector..."

# Enable pgvector extension
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable pgvector
    CREATE EXTENSION IF NOT EXISTS vector;

    -- Create knowledge chunks table
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id VARCHAR(64) PRIMARY KEY,
        content TEXT NOT NULL,
        metadata JSONB DEFAULT '{}',
        embedding vector(1024),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create index for vector search
    CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
        ON knowledge_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);

    -- Create index for metadata search
    CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_metadata
        ON knowledge_chunks USING GIN (metadata);

    -- Create index for content text search
    CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_content
        ON knowledge_chunks USING GIN (to_tsvector('russian', content));

    -- Create updated_at trigger function
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS \$\$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    \$\$ LANGUAGE plpgsql;

    -- Apply trigger to all tables (PG16-compatible)
    DO \$\$
    DECLARE
        t text;
    BEGIN
        FOR t IN SELECT table_name FROM information_schema.tables
                 WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        LOOP
            IF EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = t AND column_name = 'updated_at') THEN
                EXECUTE format(
                    'DROP TRIGGER IF EXISTS update_%s_updated_at ON %I',
                    t, t
                );
                EXECUTE format(
                    'CREATE TRIGGER update_%s_updated_at
                     BEFORE UPDATE ON %I
                     FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()',
                    t, t
                );
            END IF;
        END LOOP;
    END;
    \$\$ LANGUAGE plpgsql;

    -- Verify setup
    SELECT 'pgvector extension enabled' AS status;
    SELECT COUNT(*) AS tables_created FROM information_schema.tables
        WHERE table_schema = 'public';
EOSQL

echo "Database initialization complete."
