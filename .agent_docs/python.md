# Python Coding Standards

## Project Structure

```
openrouter-cli/
├── src/
│   ├── (NO __init__.py here) # src/ is NOT a package
│   ├── cli.py                # CLI entry point (Typer)
│   ├── logging_config.py     # Logging setup
│   ├── config.py             # Settings (pydantic-settings)
│   └── services/             # Business logic (future)
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── testdata/             # Golden files
│   └── test_*.py
├── pyproject.toml
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

**Rules:**
- `src/`: Source directory (NOT a package, no `__init__.py` at src/ level)
- Entry point: Use unique name (`cli.py`, `server.py`, `app.py`) — **NEVER `main.py`**
- Tests parallel source structure
- **ALWAYS use src/ layout**

## Coding Conventions

### Naming
- Clear purpose while being concise
- No abbreviations outside standards (id, api, db)
- Boolean: `is_`, `has_`, `should_` prefixes
- Functions: verbs or verb+noun
- Plurals: `users` (list), `user_list` (wrapped), `user_map` (specific)

### Functions
- One function, one responsibility
- If name needs "and"/"or", split it
- Limit conditional/loop depth to 2 levels (use early return)
- Order functions by call order (top-to-bottom)

### Error Handling
- Handle where meaningful response is possible
- Technical details for logs, actionable guidance for users
- Distinguish expected vs unexpected errors
- Use specific exception types, never bare `except`

## File Structure Order

1. Module docstring
2. `from __future__ import annotations`
3. Standard library imports
4. Third-party imports
5. Local imports
6. Module-level constants
7. Type aliases
8. Exception classes
9. Data classes / Pydantic models
10. Protocols / ABCs
11. Implementation classes
12. Module-level functions
13. `if __name__ == "__main__":` block

## Async-First

- Always prefer async patterns (asyncio, httpx, asyncpg)
- Use `asyncio.TaskGroup` for structured concurrency
- Use `asyncio.Semaphore` for rate limiting
- Wrap sync libs with `asyncio.to_thread()`

## Testing

### Unit Tests
- Use `@pytest.mark.parametrize` for table-driven tests
- Use fixtures in `conftest.py` for shared setup
- Mock with `unittest.mock.AsyncMock` for async code
- Run with `make test`

### Coverage
- Run with `make test-cov`
- Minimum 80% coverage enforced

## Forbidden Practices

- **Mutable default arguments**: Use `field(default_factory=list)`
- **Bare except**: Always catch specific exceptions
- **Wildcard imports**: Use explicit imports
- **`assert` in production**: Use `raise ValueError()`
- **`print()` for debugging**: Use `logger.debug()`
- **Global mutable state**: Use dependency injection

## Recommended Libraries

| Purpose | Library |
|---------|---------|
| CLI | typer |
| API | fastapi, uvicorn |
| HTTP | httpx, aiohttp |
| Validation | pydantic |
| Database | asyncpg, aiosqlite |
| Testing | pytest, pytest-asyncio, respx |
| Logging | rich |
| Config | pydantic-settings |
