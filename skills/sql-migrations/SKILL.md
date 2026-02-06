---
name: sql-migrations
description: Database migration mastery with Prisma, Drizzle, and raw SQL. Use when user asks to "create a migration", "update database schema", "add a column", "set up Prisma", "rollback migration", "write SQL migration", "set up Drizzle", or any database schema change tasks.
---

# SQL Migrations

Database migrations with Prisma, Drizzle, and raw SQL.

## Prisma

### Setup

```bash
npm install prisma @prisma/client
npx prisma init
```

### Schema (prisma/schema.prisma)

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  tags      Tag[]

  @@index([authorId])
}

model Tag {
  id    Int    @id @default(autoincrement())
  name  String @unique
  posts Post[]
}
```

### Migration Commands

```bash
# Create migration from schema changes
npx prisma migrate dev --name add_users_table

# Apply migrations in production
npx prisma migrate deploy

# Reset database (destructive)
npx prisma migrate reset

# Check migration status
npx prisma migrate status

# Generate client after schema change
npx prisma generate

# Open database GUI
npx prisma studio

# Push schema without migration file (prototyping)
npx prisma db push

# Seed database
npx prisma db seed
```

## Drizzle

### Setup

```bash
npm install drizzle-orm drizzle-kit
```

### Schema (src/db/schema.ts)

```typescript
import { pgTable, serial, text, boolean, timestamp, integer } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const posts = pgTable("posts", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false),
  authorId: integer("author_id").references(() => users.id),
});
```

### Migration Commands

```bash
# Generate migration
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Push schema directly (prototyping)
npx drizzle-kit push

# Open Drizzle Studio
npx drizzle-kit studio

# Drop migration
npx drizzle-kit drop
```

### Config (drizzle.config.ts)

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

## Raw SQL Migrations

### Directory Structure

```
migrations/
├── 001_create_users.sql
├── 002_create_posts.sql
├── 003_add_email_index.sql
└── 004_add_tags.sql
```

### Common Patterns

```sql
-- 001_create_users.sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

```sql
-- Add column
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';

-- Rename column
ALTER TABLE users RENAME COLUMN name TO full_name;

-- Change type
ALTER TABLE users ALTER COLUMN role TYPE TEXT;

-- Add NOT NULL (with default for existing rows)
UPDATE users SET role = 'user' WHERE role IS NULL;
ALTER TABLE users ALTER COLUMN role SET NOT NULL;

-- Drop column
ALTER TABLE users DROP COLUMN IF EXISTS legacy_field;
```

```sql
-- Add foreign key
ALTER TABLE posts
ADD CONSTRAINT fk_posts_author
FOREIGN KEY (author_id) REFERENCES users(id)
ON DELETE CASCADE;

-- Add unique constraint
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);

-- Add check constraint
ALTER TABLE users ADD CONSTRAINT chk_users_role
CHECK (role IN ('admin', 'user', 'moderator'));
```

### Rollback Patterns

```sql
-- Down migration: 003_add_email_index.down.sql
DROP INDEX IF EXISTS idx_users_email;

-- Down migration: 002_add_role.down.sql
ALTER TABLE users DROP COLUMN IF EXISTS role;
```

## Best Practices

```
1. One change per migration - easier to rollback
2. Always write down migrations
3. Never edit applied migrations - create new ones
4. Test migrations on copy of production data
5. Use transactions for multi-statement migrations
6. Add indexes concurrently in production:
   CREATE INDEX CONCURRENTLY idx_name ON table(column);
7. Backfill data in separate migration from schema change
```

## Reference

For Prisma patterns: `references/prisma.md`
For raw SQL patterns: `references/raw-sql.md`
