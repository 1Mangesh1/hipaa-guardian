# Jest & Vitest Advanced Patterns

## React Component Testing

```typescript
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Test form submission
it("submits form data", async () => {
  const onSubmit = vi.fn();
  const user = userEvent.setup();

  render(<ContactForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText(/name/i), "Alice");
  await user.type(screen.getByLabelText(/email/i), "alice@test.com");
  await user.selectOptions(screen.getByLabelText(/role/i), "admin");
  await user.click(screen.getByRole("button", { name: /submit/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    name: "Alice",
    email: "alice@test.com",
    role: "admin",
  });
});

// Test loading states
it("shows loading spinner", async () => {
  render(<UserList />);
  expect(screen.getByRole("progressbar")).toBeInTheDocument();
  await waitFor(() => {
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });
  expect(screen.getAllByRole("listitem")).toHaveLength(3);
});

// Test error states
it("shows error message", async () => {
  server.use(
    http.get("/api/users", () => HttpResponse.error())
  );
  render(<UserList />);
  expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
});
```

## MSW (Mock Service Worker)

```typescript
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const handlers = [
  http.get("/api/users", () => {
    return HttpResponse.json([
      { id: 1, name: "Alice" },
      { id: 2, name: "Bob" },
    ]);
  }),
  http.post("/api/users", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 3, ...body }, { status: 201 });
  }),
];

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("fetches users", async () => {
  render(<UserList />);
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});
```

## Testing Custom Hooks

```typescript
import { renderHook, act } from "@testing-library/react";

it("increments counter", () => {
  const { result } = renderHook(() => useCounter(0));

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});

// With wrapper (providers)
it("uses context", () => {
  const wrapper = ({ children }) => (
    <ThemeProvider theme="dark">{children}</ThemeProvider>
  );
  const { result } = renderHook(() => useTheme(), { wrapper });
  expect(result.current.theme).toBe("dark");
});
```

## Module Mocking Patterns

```typescript
// Partial mock (keep some real implementations)
vi.mock("./utils", async () => {
  const actual = await vi.importActual("./utils");
  return {
    ...actual,
    sendEmail: vi.fn(),  // Only mock sendEmail
  };
});

// Mock specific export
vi.mock("./config", () => ({
  default: { apiUrl: "http://test.local" },
  API_KEY: "test-key",
}));

// Dynamic mock per test
import * as api from "./api";

it("handles success", () => {
  vi.spyOn(api, "fetchData").mockResolvedValue({ data: "ok" });
  // ...
});

it("handles failure", () => {
  vi.spyOn(api, "fetchData").mockRejectedValue(new Error("fail"));
  // ...
});
```

## Testing Error Boundaries

```typescript
it("catches rendering errors", () => {
  const spy = vi.spyOn(console, "error").mockImplementation(() => {});

  render(
    <ErrorBoundary fallback={<p>Something went wrong</p>}>
      <BrokenComponent />
    </ErrorBoundary>
  );

  expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  spy.mockRestore();
});
```

## Vitest-Specific Features

```typescript
// In-source testing
// src/utils.ts
export function add(a: number, b: number) {
  return a + b;
}

if (import.meta.vitest) {
  const { it, expect } = import.meta.vitest;
  it("adds", () => {
    expect(add(1, 2)).toBe(3);
  });
}

// Type testing
import { expectTypeOf } from "vitest";

it("has correct types", () => {
  expectTypeOf(fn).toBeFunction();
  expectTypeOf(fn).parameter(0).toBeString();
  expectTypeOf(fn).returns.toBeNumber();
});

// Benchmark
import { bench } from "vitest";

bench("sort array", () => {
  [3, 1, 2].sort();
});
```

## Jest to Vitest Migration

```
jest.fn()           → vi.fn()
jest.mock()         → vi.mock()
jest.spyOn()        → vi.spyOn()
jest.useFakeTimers() → vi.useFakeTimers()
jest.clearAllMocks() → vi.clearAllMocks()
jest.requireActual() → vi.importActual() (async)
@jest/globals        → vitest

// jest.config.js → vitest.config.ts
// setupFilesAfterSetup → setupFiles
// moduleNameMapper → resolve.alias (in vite config)
```
