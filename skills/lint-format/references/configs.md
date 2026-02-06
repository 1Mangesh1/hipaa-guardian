# Lint & Format Configuration Recipes

## Starter Configs

### TypeScript + React Project

```bash
npm install -D eslint @eslint/js typescript-eslint eslint-plugin-react eslint-plugin-react-hooks prettier eslint-config-prettier
```

```javascript
// eslint.config.js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import prettier from "eslint-config-prettier";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: { react, "react-hooks": reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react/react-in-jsx-scope": "off",
    },
    settings: { react: { version: "detect" } },
  },
  prettier,
  { ignores: ["dist/", "*.config.*"] },
];
```

### Node.js API Project

```javascript
// eslint.config.js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    },
  },
  prettier,
  { ignores: ["dist/", "node_modules/"] },
];
```

### Python Project (Ruff)

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "TCH", "RUF"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # Allow assert in tests

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.12"
strict = true
```

## IDE Integration

### VS Code settings.json

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "[typescript]": {
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": "explicit"
    }
  },
  "eslint.useFlatConfig": true
}
```

### VS Code Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "charliermarsh.ruff",
    "editorconfig.editorconfig"
  ]
}
```

## CI Integration

```yaml
# .github/workflows/lint.yml
name: Lint & Format
on: [push, pull_request]

jobs:
  lint-js:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx eslint .
      - run: npx prettier --check .
      - run: npx tsc --noEmit

  lint-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff mypy
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src/
```

## Migration Guides

### TSLint → ESLint
TSLint is deprecated. Use `typescript-eslint` with flat config.

### ESLint Legacy → Flat Config
```bash
# Old: .eslintrc.json with extends/plugins
# New: eslint.config.js with imports

# Migration tool
npx @eslint/migrate-config .eslintrc.json
```

### Flake8/isort/Black → Ruff
```bash
# Ruff replaces all three in one tool
# Remove: flake8, isort, black, pycodestyle, pyflakes
# Install: ruff
# Ruff reads existing flake8/isort config and auto-migrates
```
