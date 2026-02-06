# Python Environment Tools Comparison

## Quick Comparison

| Feature | venv + pip | Poetry | uv | Pipenv | conda |
|---------|-----------|--------|-----|--------|-------|
| Speed | Slow | Medium | Very Fast | Slow | Slow |
| Lock file | No* | Yes | Yes | Yes | Yes |
| Dependency resolution | Basic | Advanced | Advanced | Advanced | Advanced |
| Python version mgmt | No | No | Yes | No | Yes |
| Built-in | Yes | No | No | No | No |
| Monorepo support | No | No | Partial | No | No |
| Non-Python deps | No | No | No | No | Yes |

*pip-tools can add lock file support to pip

## Migration Guides

### pip to Poetry

```bash
# From requirements.txt
poetry init
# Answer prompts, then:
cat requirements.txt | xargs poetry add

# Or use import
poetry add $(cat requirements.txt | sed 's/==/>=/g')
```

### pip to uv

```bash
# Drop-in replacement (same commands)
uv pip install -r requirements.txt
uv pip freeze > requirements.txt

# Or use uv project management
uv init
uv add requests flask
```

### Poetry to pip

```bash
poetry export -f requirements.txt --output requirements.txt
poetry export -f requirements.txt --output requirements-dev.txt --with dev
```

### Pipenv to Poetry

```bash
# Export from Pipenv
pipenv requirements > requirements.txt
pipenv requirements --dev > requirements-dev.txt

# Import to Poetry
poetry init
poetry add $(cat requirements.txt)
poetry add --group dev $(cat requirements-dev.txt)
```

## pyproject.toml Configurations

### Setuptools (PEP 621)

```toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.1",
]

[project.scripts]
serve = "my_project.main:app"
```

### Hatchling

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.envs.default]
dependencies = ["pytest", "ruff"]

[tool.hatch.envs.default.scripts]
test = "pytest"
lint = "ruff check ."
```

## Recommended Stack by Project Type

### Quick Script
```bash
python -m venv .venv && source .venv/bin/activate && pip install requests
```

### Application (Web, CLI)
```bash
# Poetry or uv for dependency management
poetry init && poetry add flask sqlalchemy
# OR
uv init && uv add flask sqlalchemy
```

### Library (Published to PyPI)
```bash
# Poetry with pyproject.toml
poetry new my-library
poetry build && poetry publish
```

### Data Science
```bash
# conda for non-Python dependencies (numpy, scipy)
conda create -n analysis python=3.12 numpy pandas matplotlib jupyter
```

### Monorepo
```bash
# uv workspaces or pip-tools per package
uv init --workspace
```
