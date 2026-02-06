# Raw SQL Migration Patterns

## Table Operations

```sql
-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create with foreign key
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    published BOOLEAN DEFAULT FALSE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create junction table
CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
```

## Column Operations

```sql
-- Add column
ALTER TABLE users ADD COLUMN bio TEXT;
ALTER TABLE users ADD COLUMN age INTEGER CHECK (age >= 0);

-- Add column with default (for existing rows)
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active' NOT NULL;

-- Drop column
ALTER TABLE users DROP COLUMN IF EXISTS legacy_field;

-- Rename column
ALTER TABLE users RENAME COLUMN name TO full_name;

-- Change type
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;

-- Set/drop default
ALTER TABLE users ALTER COLUMN role SET DEFAULT 'member';
ALTER TABLE users ALTER COLUMN role DROP DEFAULT;

-- Set/drop NOT NULL
ALTER TABLE users ALTER COLUMN name SET NOT NULL;
ALTER TABLE users ALTER COLUMN name DROP NOT NULL;
```

## Index Operations

```sql
-- Basic index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Composite index
CREATE INDEX idx_posts_author_date ON posts(author_id, created_at DESC);

-- Partial index
CREATE INDEX idx_posts_published ON posts(author_id) WHERE published = TRUE;

-- Concurrent (no lock - use in production)
CREATE INDEX CONCURRENTLY idx_users_name ON users(name);

-- Drop index
DROP INDEX IF EXISTS idx_users_email;
```

## Data Migrations

```sql
-- Backfill column
UPDATE users SET role = 'user' WHERE role IS NULL;

-- Copy data between tables
INSERT INTO new_users (email, name)
SELECT email, name FROM old_users;

-- Merge columns
UPDATE users SET full_name = first_name || ' ' || last_name;

-- Conditional update
UPDATE orders SET status = 'archived'
WHERE created_at < NOW() - INTERVAL '1 year'
AND status = 'completed';
```

## Enum Pattern (PostgreSQL)

```sql
-- Create enum
CREATE TYPE user_role AS ENUM ('admin', 'user', 'moderator');

-- Use enum
ALTER TABLE users ADD COLUMN role user_role DEFAULT 'user';

-- Add value to enum
ALTER TYPE user_role ADD VALUE 'editor';

-- Note: Cannot remove enum values - create new type and migrate
```

## Transaction Safety

```sql
BEGIN;

ALTER TABLE users ADD COLUMN department_id INTEGER;

UPDATE users SET department_id = (
    SELECT id FROM departments WHERE name = users.department
);

ALTER TABLE users ADD CONSTRAINT fk_department
    FOREIGN KEY (department_id) REFERENCES departments(id);

ALTER TABLE users DROP COLUMN department;

COMMIT;
```

## Rollback Template

```sql
-- Up
BEGIN;
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
COMMIT;

-- Down
BEGIN;
DROP TABLE IF EXISTS audit_logs;
COMMIT;
```
