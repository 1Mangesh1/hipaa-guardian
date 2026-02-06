---
name: graphql
description: GraphQL schema design, queries, mutations, and tooling. Use when user asks to "write a GraphQL schema", "create a query", "add a mutation", "set up Apollo", "GraphQL resolver", "type definitions", or any GraphQL tasks.
---

# GraphQL

Schema design, queries, mutations, and tooling.

## Schema Definition

```graphql
# Type definitions
type User {
  id: ID!
  email: String!
  name: String
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String
  published: Boolean!
  author: User!
  tags: [Tag!]!
}

type Tag {
  id: ID!
  name: String!
  posts: [Post!]!
}

# Input types
input CreateUserInput {
  email: String!
  name: String
}

input UpdateUserInput {
  email: String
  name: String
}

input PostFilter {
  published: Boolean
  authorId: ID
  search: String
}

# Enums
enum Role {
  ADMIN
  USER
  MODERATOR
}

enum SortOrder {
  ASC
  DESC
}

# Custom scalars
scalar DateTime
scalar JSON

# Interfaces
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  email: String!
}

# Unions
union SearchResult = User | Post | Tag
```

## Queries

```graphql
type Query {
  # Single item
  user(id: ID!): User
  post(id: ID!): Post

  # Lists with filtering and pagination
  users(
    filter: UserFilter
    limit: Int = 20
    offset: Int = 0
    orderBy: SortOrder = DESC
  ): UserConnection!

  posts(
    filter: PostFilter
    first: Int
    after: String
  ): PostConnection!

  # Search
  search(query: String!): [SearchResult!]!

  # Current user
  me: User
}

# Cursor-based pagination
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Query Examples

```graphql
# Basic query
query {
  user(id: "1") {
    name
    email
  }
}

# With variables
query GetUser($id: ID!) {
  user(id: $id) {
    name
    email
    posts {
      title
      published
    }
  }
}

# Fragment
fragment UserFields on User {
  id
  name
  email
}

query {
  user(id: "1") {
    ...UserFields
    posts {
      title
    }
  }
}

# Pagination
query GetPosts($first: Int!, $after: String) {
  posts(first: $first, after: $after) {
    edges {
      node {
        id
        title
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Mutations

```graphql
type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!

  createPost(input: CreatePostInput!): Post!
  publishPost(id: ID!): Post!

  login(email: String!, password: String!): AuthPayload!
}

type AuthPayload {
  token: String!
  user: User!
}
```

### Mutation Examples

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    email
    name
  }
}

# Variables:
# { "input": { "email": "alice@test.com", "name": "Alice" } }

mutation Login($email: String!, $password: String!) {
  login(email: $email, password: $password) {
    token
    user {
      id
      name
    }
  }
}
```

## Subscriptions

```graphql
type Subscription {
  postCreated: Post!
  messageReceived(channelId: ID!): Message!
}

# Client usage
subscription OnPostCreated {
  postCreated {
    id
    title
    author {
      name
    }
  }
}
```

## Resolvers (Node.js)

```typescript
const resolvers = {
  Query: {
    user: (_, { id }, context) => context.db.user.findUnique({ where: { id } }),
    users: (_, { filter, limit, offset }, context) =>
      context.db.user.findMany({ where: filter, take: limit, skip: offset }),
    me: (_, __, context) => context.currentUser,
  },

  Mutation: {
    createUser: (_, { input }, context) =>
      context.db.user.create({ data: input }),
    updateUser: (_, { id, input }, context) =>
      context.db.user.update({ where: { id }, data: input }),
  },

  User: {
    posts: (user, _, context) =>
      context.db.post.findMany({ where: { authorId: user.id } }),
  },
};
```

## Error Handling

```graphql
# Union-based errors
type CreateUserResult = CreateUserSuccess | ValidationError | EmailTakenError

type CreateUserSuccess {
  user: User!
}

type ValidationError {
  message: String!
  field: String!
}

type EmailTakenError {
  message: String!
  suggestedEmail: String
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserResult!
}
```

## Reference

For Apollo, Relay, and testing patterns: `references/tooling.md`
