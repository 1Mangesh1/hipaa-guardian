# GraphQL Tooling Reference

## Apollo Server (Node.js)

```typescript
import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";

const typeDefs = `#graphql
  type Query {
    hello: String
    users: [User!]!
  }

  type User {
    id: ID!
    name: String!
  }
`;

const resolvers = {
  Query: {
    hello: () => "Hello World",
    users: (_, __, { dataSources }) => dataSources.userAPI.getUsers(),
  },
};

const server = new ApolloServer({ typeDefs, resolvers });

const { url } = await startStandaloneServer(server, {
  context: async ({ req }) => ({
    token: req.headers.authorization,
    dataSources: { userAPI: new UserAPI() },
  }),
  listen: { port: 4000 },
});
```

### Apollo with Express

```typescript
import express from "express";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";

const app = express();
const server = new ApolloServer({ typeDefs, resolvers });
await server.start();

app.use(
  "/graphql",
  express.json(),
  expressMiddleware(server, {
    context: async ({ req }) => ({ token: req.headers.authorization }),
  })
);

app.listen(4000);
```

## Apollo Client (React)

```typescript
import { ApolloClient, InMemoryCache, ApolloProvider, gql, useQuery, useMutation } from "@apollo/client";

// Setup
const client = new ApolloClient({
  uri: "http://localhost:4000/graphql",
  cache: new InMemoryCache(),
  headers: { authorization: `Bearer ${token}` },
});

// Provider
function App() {
  return (
    <ApolloProvider client={client}>
      <Users />
    </ApolloProvider>
  );
}

// Query hook
const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
    }
  }
`;

function Users() {
  const { loading, error, data, refetch } = useQuery(GET_USERS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return data.users.map((user) => <div key={user.id}>{user.name}</div>);
}

// Mutation hook
const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id
      name
    }
  }
`;

function CreateUserForm() {
  const [createUser, { loading }] = useMutation(CREATE_USER, {
    refetchQueries: [{ query: GET_USERS }],
    onCompleted: (data) => console.log("Created:", data.createUser),
  });

  const handleSubmit = (name: string) => {
    createUser({ variables: { input: { name } } });
  };
}
```

## GraphQL Code Generator

```bash
npm install -D @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations @graphql-codegen/typescript-react-apollo
```

```yaml
# codegen.yml
schema: "http://localhost:4000/graphql"
documents: "src/**/*.graphql"
generates:
  src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-react-apollo
    config:
      withHooks: true
```

```bash
npx graphql-codegen
```

## Testing GraphQL

### Server Testing

```typescript
import { ApolloServer } from "@apollo/server";

describe("GraphQL API", () => {
  let server: ApolloServer;

  beforeAll(() => {
    server = new ApolloServer({ typeDefs, resolvers });
  });

  it("returns users", async () => {
    const response = await server.executeOperation({
      query: "query { users { id name } }",
    });

    expect(response.body.kind).toBe("single");
    expect(response.body.singleResult.data?.users).toHaveLength(2);
  });

  it("creates user", async () => {
    const response = await server.executeOperation({
      query: `mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) { id name }
      }`,
      variables: { input: { name: "Alice", email: "alice@test.com" } },
    });

    expect(response.body.singleResult.data?.createUser.name).toBe("Alice");
  });
});
```

### Client Testing (MockedProvider)

```typescript
import { MockedProvider } from "@apollo/client/testing";
import { render, screen } from "@testing-library/react";

const mocks = [
  {
    request: { query: GET_USERS },
    result: {
      data: {
        users: [{ id: "1", name: "Alice" }],
      },
    },
  },
];

it("renders users", async () => {
  render(
    <MockedProvider mocks={mocks}>
      <Users />
    </MockedProvider>
  );

  expect(await screen.findByText("Alice")).toBeInTheDocument();
});
```

## GraphQL Tools & Utilities

| Tool | Purpose |
|------|---------|
| GraphQL Playground | Interactive IDE (browser) |
| Apollo Studio | Schema explorer, metrics |
| GraphQL Code Generator | Type-safe code from schema |
| graphql-tools | Schema stitching, mocking |
| DataLoader | N+1 query batching |
| graphql-shield | Permission layer |
| graphql-scalars | Common custom scalars |

## DataLoader (N+1 Prevention)

```typescript
import DataLoader from "dataloader";

// Create loader
const userLoader = new DataLoader(async (userIds: string[]) => {
  const users = await db.user.findMany({ where: { id: { in: userIds } } });
  return userIds.map((id) => users.find((u) => u.id === id));
});

// Use in resolver
const resolvers = {
  Post: {
    author: (post) => userLoader.load(post.authorId),
  },
};
```
