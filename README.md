# cron-explain

Translate cron expressions to human-readable English.

## Install

```bash
uv tool install .
```

## Usage

```bash
# Translate a cron expression
cron-explain "0 9 * * *"
# Output: At minute 0, at 09:00

# Or use python -m
python -m cron_explain "*/5 * * * 1-5"
# Output: Every 5 minutes, on every day-of-week from Monday through Friday
```

## Examples

```bash
cron-explain "* * * * *"
# Every minute

cron-explain "0 0 1 1 *"
# At minute 0, at 00:00, on day-of-month 1, in January

cron-explain "0 9 * * 1,3,5"
# At minute 0, at 09:00, on Monday, Wednesday, Friday

cron-explain "*/15 * * * *"
# Every 15 minutes

cron-explain "0 9-17 * * 1-5"
# At minute 0, between 09:00 and 17:59, on every day-of-week from Monday through Friday
```

## Testing

```bash
# Run tests with coverage
uv run pytest --cov=src/cron_explain --cov-report=term-missing --cov-fail-under=100 -v
```

## License

MIT
