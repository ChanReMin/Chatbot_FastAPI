-- ============================================
-- PostgreSQL Initialization Script
-- Enable pgvector extension for vector operations
-- ============================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
