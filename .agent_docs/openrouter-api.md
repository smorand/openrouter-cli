# OpenRouter API Behavior and Limitations

## Activity Endpoint (`/api/v1/activity`)

### Known Limitation: Completed UTC Days Only

The `/activity` endpoint returns data only for **completed UTC days**:

> "Returns user activity data grouped by endpoint for the last 30 (completed) UTC days."

**Impact:** Data for the current day (and potentially yesterday) will not appear until those UTC days are fully completed.

- UTC day ends at 00:00 UTC
- If you are in UTC+1 timezone, UTC day ends at 01:00 local time
- Data for 21/03 will appear after 01:00 UTC+1 on 22/03
- Data for 22/03 will appear after 01:00 UTC+1 on 23/03

### Behavior Summary

| Endpoint | Per Model | Per Day | Real-time | Latency |
|----------|-----------|---------|-----------|---------|
| `/api/v1/activity` | Yes | Yes | No | 1-2 days (completed UTC days) |
| `/api/v1/auth/key` | No | No | Yes | Real-time |

### Workaround

For real-time usage totals (without per-model/per-day breakdown), use `/auth/key` endpoint:

```python
response = await client.get("/auth/key")
data = response.json()
usage_daily = data["data"]["usage_daily"]    # Today's total
usage_weekly = data["data"]["usage_weekly"]  # Last 7 days total
usage_monthly = data["data"]["usage_monthly"] # Last 30 days total
```

### Activity Response Structure

```json
{
  "data": [
    {
      "date": "2026-03-20 00:00:00",
      "model": "anthropic/claude-haiku-4.5",
      "model_permaslug": "anthropic/claude-4.5-haiku-20251001",
      "endpoint_id": "d000261c-5aeb-47d1-ac87-ad64dbe1cdb6",
      "usage": 0.075432,
      "requests": 40,
      "prompt_tokens": 80577,
      "completion_tokens": 284,
      "reasoning_tokens": 0,
      "provider_name": "amazon-bedrock"
    }
  ]
}
```

### Authentication

- `/activity` requires a **management key** (`is_management_key: true`)
- Regular API keys receive 403 Forbidden error

## Credits Endpoint (`/api/v1/auth/key`)

Returns real-time aggregate usage totals for the current API key:

```json
{
  "data": {
    "label": "sk-or-v1-502...dbf",
    "usage": 102.016,
    "usage_daily": 30.95,
    "usage_weekly": 36.028,
    "usage_monthly": 50.009
  }
}
```

## Models Endpoint (`/api/v1/models`)

Returns list of available models with pricing and capabilities. No authentication required for basic listing.
