-- EduNerve Database Initialization Script
-- This script creates the database schemas for all services

-- Create database schemas for different services
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS assistant;
CREATE SCHEMA IF NOT EXISTS admin;
CREATE SCHEMA IF NOT EXISTS sync;
CREATE SCHEMA IF NOT EXISTS files;
CREATE SCHEMA IF NOT EXISTS notifications;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET TIME ZONE 'UTC';

-- Create a function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant permissions to edunerve user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO edunerve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA content TO edunerve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA assistant TO edunerve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA admin TO edunerve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sync TO edunerve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA files TO edunerve;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA notifications TO edunerve;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth TO edunerve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA content TO edunerve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA assistant TO edunerve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA admin TO edunerve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sync TO edunerve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA files TO edunerve;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA notifications TO edunerve;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_school_id ON auth.users(school_id);
CREATE INDEX IF NOT EXISTS idx_content_school_id ON content.courses(school_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON sync.messages(created_at);

-- Insert default data
INSERT INTO auth.schools (id, name, country, state, city, school_type, student_capacity, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'Demo School',
    'Nigeria',
    'Lagos',
    'Lagos',
    'secondary',
    1000,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

-- Create admin user
INSERT INTO auth.users (id, email, password_hash, first_name, last_name, role, school_id, is_active, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'admin@edunerve.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewOhgNLfE9yIFmZS', -- password: admin123
    'Admin',
    'User',
    'admin',
    s.id,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM auth.schools s
WHERE s.name = 'Demo School'
ON CONFLICT DO NOTHING;

COMMIT;
