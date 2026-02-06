# Prisma Advanced Patterns

## Relations

```prisma
// One-to-many
model User {
  id    Int    @id @default(autoincrement())
  posts Post[]
}

model Post {
  id       Int  @id @default(autoincrement())
  author   User @relation(fields: [authorId], references: [id])
  authorId Int
}

// Many-to-many (implicit)
model Post {
  id   Int   @id @default(autoincrement())
  tags Tag[]
}

model Tag {
  id    Int    @id @default(autoincrement())
  posts Post[]
}

// Many-to-many (explicit join table)
model PostTag {
  post   Post @relation(fields: [postId], references: [id])
  postId Int
  tag    Tag  @relation(fields: [tagId], references: [id])
  tagId  Int

  @@id([postId, tagId])
}

// Self-relation
model User {
  id         Int    @id @default(autoincrement())
  followers  User[] @relation("UserFollows")
  following  User[] @relation("UserFollows")
}
```

## Queries

```typescript
// Create with relation
const user = await prisma.user.create({
  data: {
    email: "alice@test.com",
    posts: {
      create: [
        { title: "First Post" },
        { title: "Second Post" },
      ],
    },
  },
  include: { posts: true },
});

// Nested where
const users = await prisma.user.findMany({
  where: {
    posts: {
      some: { published: true },
    },
  },
});

// Transactions
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: "bob@test.com" } }),
  prisma.post.create({ data: { title: "Hello", authorId: 1 } }),
]);

// Interactive transaction
await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUnique({ where: { id: 1 } });
  if (user.balance < amount) throw new Error("Insufficient funds");
  await tx.user.update({
    where: { id: 1 },
    data: { balance: { decrement: amount } },
  });
});
```

## Seeding

```typescript
// prisma/seed.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.user.upsert({
    where: { email: "admin@test.com" },
    update: {},
    create: {
      email: "admin@test.com",
      name: "Admin",
      posts: {
        create: { title: "Welcome", published: true },
      },
    },
  });
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

```json
// package.json
{
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
```

## Common Migration Patterns

```bash
# Rename field (two-step)
# Step 1: Add new column
npx prisma migrate dev --name add_full_name
# Step 2: Migrate data with raw SQL, then remove old column
npx prisma migrate dev --name remove_name

# Add required field to existing table
# Step 1: Add as optional
# Step 2: Backfill data
# Step 3: Make required
```
