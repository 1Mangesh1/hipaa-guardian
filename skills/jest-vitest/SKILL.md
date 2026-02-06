---
name: jest-vitest
description: JavaScript/TypeScript testing with Jest and Vitest. Use when user asks to "write JS tests", "add unit tests", "test React component", "mock a module", "snapshot testing", "test async code", "set up Jest", "migrate to Vitest", or any JS/TS testing tasks.
---

# Jest & Vitest

JavaScript/TypeScript testing with Jest and Vitest.

## Running Tests

```bash
# Jest
npx jest
npx jest --watch
npx jest --coverage
npx jest path/to/test.ts
npx jest -t "test name pattern"

# Vitest
npx vitest
npx vitest run          # Single run (no watch)
npx vitest --coverage
npx vitest path/to/test.ts
```

## Test Structure

```typescript
// Jest and Vitest share the same API
describe("Calculator", () => {
  let calc: Calculator;

  beforeEach(() => {
    calc = new Calculator();
  });

  afterEach(() => {
    calc.reset();
  });

  it("should add two numbers", () => {
    expect(calc.add(2, 3)).toBe(5);
  });

  it("should throw on division by zero", () => {
    expect(() => calc.divide(1, 0)).toThrow("Division by zero");
  });

  describe("negative numbers", () => {
    it("should handle negative addition", () => {
      expect(calc.add(-1, -2)).toBe(-3);
    });
  });
});
```

## Common Matchers

```typescript
// Equality
expect(value).toBe(exact);           // === strict
expect(value).toEqual(deepEqual);    // Deep equality
expect(value).toStrictEqual(strict); // Deep + type

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeLessThanOrEqual(10);
expect(value).toBeCloseTo(0.3, 5);

// Strings
expect(str).toMatch(/regex/);
expect(str).toContain("substring");

// Arrays/Objects
expect(arr).toContain(item);
expect(arr).toHaveLength(3);
expect(obj).toHaveProperty("key", "value");
expect(obj).toMatchObject({ name: "Alice" });

// Exceptions
expect(() => fn()).toThrow();
expect(() => fn()).toThrow("message");
expect(() => fn()).toThrow(ErrorClass);
```

## Mocking

```typescript
// Mock function
const mockFn = jest.fn();              // Jest
const mockFn = vi.fn();                // Vitest

mockFn.mockReturnValue(42);
mockFn.mockReturnValueOnce(1);
mockFn.mockResolvedValue({ data: [] });
mockFn.mockImplementation((x) => x * 2);

// Assertions
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith("arg1", "arg2");

// Mock module
jest.mock("./database");               // Jest
vi.mock("./database");                 // Vitest

// Mock with implementation
jest.mock("./api", () => ({
  fetchUser: jest.fn().mockResolvedValue({ name: "Alice" }),
}));

// Vitest equivalent
vi.mock("./api", () => ({
  fetchUser: vi.fn().mockResolvedValue({ name: "Alice" }),
}));

// Spy on existing method
const spy = jest.spyOn(object, "method");   // Jest
const spy = vi.spyOn(object, "method");     // Vitest

// Mock timers
jest.useFakeTimers();  // Jest
vi.useFakeTimers();    // Vitest

jest.advanceTimersByTime(1000);  // Jest
vi.advanceTimersByTime(1000);    // Vitest
```

## Async Testing

```typescript
// Async/await
it("fetches users", async () => {
  const users = await fetchUsers();
  expect(users).toHaveLength(3);
});

// Resolved/rejected
it("resolves with data", async () => {
  await expect(fetchData()).resolves.toEqual({ ok: true });
});

it("rejects with error", async () => {
  await expect(fetchBad()).rejects.toThrow("Network error");
});
```

## Snapshot Testing

```typescript
// Create/update snapshot
it("renders correctly", () => {
  const tree = render(<Button label="Click" />);
  expect(tree).toMatchSnapshot();
});

// Inline snapshot
it("serializes", () => {
  expect(serialize(data)).toMatchInlineSnapshot(`"expected output"`);
});

// Update snapshots: jest --updateSnapshot / vitest --update
```

## React Testing (Testing Library)

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

it("renders and interacts", async () => {
  render(<LoginForm onSubmit={mockSubmit} />);

  // Query elements
  const input = screen.getByRole("textbox", { name: /email/i });
  const button = screen.getByRole("button", { name: /submit/i });

  // Interact
  fireEvent.change(input, { target: { value: "alice@test.com" } });
  fireEvent.click(button);

  // Assert
  await waitFor(() => {
    expect(mockSubmit).toHaveBeenCalledWith("alice@test.com");
  });

  expect(screen.getByText("Success")).toBeInTheDocument();
});

// userEvent (more realistic)
import userEvent from "@testing-library/user-event";

it("types and submits", async () => {
  const user = userEvent.setup();
  render(<Form />);

  await user.type(screen.getByRole("textbox"), "hello");
  await user.click(screen.getByRole("button"));
});
```

## Coverage

```bash
# Jest
npx jest --coverage --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80}}'

# Vitest (vitest.config.ts)
# coverage: { provider: "v8", thresholds: { lines: 80 } }
```

## Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      exclude: ["node_modules/", "tests/"],
    },
  },
});
```

```javascript
// jest.config.js
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterSetup: ["./tests/setup.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
};
```

## Reference

For advanced patterns, React testing recipes, and migration guides: `references/patterns.md`
