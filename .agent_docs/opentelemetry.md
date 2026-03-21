# OpenTelemetry Setup

## Overview

OpenTelemetry tracing is **mandatory** for all Python projects. This document outlines the setup and usage patterns.

## Required Dependencies

```toml
[project.dependencies]
opentelemetry-api>=1.29.0
opentelemetry-sdk>=1.29.0
```

## What MUST Be Traced

| Category | Level | Span attributes |
|----------|-------|-----------------|
| API calls (HTTP, gRPC) | INFO | endpoint, method, status_code, duration |
| External tool calls | INFO | tool name, all arguments, result summary |
| Database queries | DEBUG | query preview (200 chars), row_count, duration |
| File mutations (write, rename, delete) | DEBUG | path, size or count |
| Auth operations | INFO | operation type, success/failure — NEVER tokens |
| Errors and exceptions | ERROR | message + `span.record_exception(e)` |
| Warnings (retries, degraded) | WARNING | reason, retry count |
| LLM calls | INFO | model, input_tokens, output_tokens, duration, cost |

## What MUST NEVER Be Traced

- **LLM prompts and responses** (sensitive data)
- Credentials, API keys, OAuth tokens, passwords, PII

## Span Naming Convention

Use `category.operation` format:
- `api.crossref.search`
- `duckdb.query`
- `auth.token_refresh`
- `llm.call`
- `file.write`
- `tool.convert_pdf`

## HTTP Client Integration

When using httpx or aiohttp, ensure OpenTelemetry instrumentation:

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

HTTPXClientInstrumentor().instrument()
```

## Context Propagation

API calls MUST propagate trace context via headers:
```
traceparent: {version}-{trace-id}-{parent-id}-{trace-flags}
```
