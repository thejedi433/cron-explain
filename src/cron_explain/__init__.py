"""cron-explain: translate cron expressions to human-readable English."""

DAYS_OF_WEEK = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]
MONTHS = [
    "", "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December",
]


def explain(expression: str) -> str:
    """Convert a 5-field cron expression to a human-readable description.

    Raises ValueError on invalid input.
    """
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Cron expression must have 5 fields, got {len(parts)}: {expression!r}"
        )
    minute, hour, dom, month, dow = parts

    parts_text = []

    # Minute field
    parts_text.append(_describe_minute(minute))

    # Hour field
    parts_text.append(_describe_hour(hour, minute))

    # Day of month
    parts_text.append(_describe_dom(dom))

    # Month
    parts_text.append(_describe_month(month))

    # Day of week
    parts_text.append(_describe_dow(dow))

    # Combine meaningful parts
    meaningful = [p for p in parts_text if p]

    if not meaningful:
        return "Every minute"

    return ", ".join(meaningful)


def _parse_field(field: str, min_val: int, max_val: int) -> str:
    """Validate and normalize a single cron field. Returns the field as-is if valid."""
    for piece in field.split(","):
        if "/" in piece:
            base, step = piece.split("/", 1)
            if not step.isdigit() or int(step) == 0:
                raise ValueError(f"Invalid step value in {piece!r}")
            if base == "*":
                pass
            elif "-" in base:
                lo, hi = base.split("-", 1)
                _check_range(lo, hi, min_val, max_val)
            else:
                _check_val(base, min_val, max_val)
        elif "-" in piece:
            lo, hi = piece.split("-", 1)
            _check_range(lo, hi, min_val, max_val)
        elif piece == "*":
            pass
        else:
            _check_val(piece, min_val, max_val)
    return field

def _check_val(val: str, min_val: int, max_val: int):
    if not val.isdigit():
        raise ValueError(f"Invalid value: {val!r}")
    n = int(val)
    if not (min_val <= n <= max_val):
        raise ValueError(f"Value {n} out of range {min_val}-{max_val}")


def _check_range(lo: str, hi: str, min_val: int, max_val: int):
    _check_val(lo, min_val, max_val)
    _check_val(hi, min_val, max_val)
    if int(lo) > int(hi):
        raise ValueError(f"Invalid range {lo}-{hi}")


def _describe_minute(field: str) -> str:
    _parse_field(field, 0, 59)
    if field == "*":
        return ""  # every minute is default
    if field.startswith("*/"):
        step = int(field.split("/")[1])
        return f"Every {step} minute{'s' if step > 1 else ''}"
    return f"At minute {field}"


def _describe_hour(field: str, minute_field: str) -> str:
    _parse_field(field, 0, 23)
    if field == "*":
        return ""
    if "-" in field and "," not in field and "/" not in field:
        lo, hi = field.split("-", 1)
        return f"between {int(lo):02d}:00 and {int(hi):02d}:59"
    if "/" in field:
        base, step = field.split("/", 1)
        step_n = int(step)
        start = "00" if base == "*" else base.split("-")[0]
        return f"every {step_n} hour{'s' if step_n > 1 else ''} from {int(start):02d}:00"
    if "," in field:
        vals = field.split(",")
        return "at " + " and ".join(f"{int(v):02d}:00" for v in vals)
    return f"at {int(field):02d}:00"


def _describe_dom(field: str) -> str:
    _parse_field(field, 1, 31)
    if field == "*":
        return ""
    if field.startswith("*/"):
        step = int(field.split("/")[1])
        return f"every {step} day{'s' if step > 1 else ''} of the month"
    if "," in field:
        return "on day-of-month " + ", ".join(field.split(","))
    if "-" in field:
        lo, hi = field.split("-", 1)
        return f"on every day-of-month from {lo} through {hi}"
    return f"on day-of-month {field}"


def _describe_month(field: str) -> str:
    _parse_field(field, 1, 12)
    if field == "*":
        return ""
    if field.startswith("*/"):
        step = int(field.split("/")[1])
        return f"every {step} month{'s' if step > 1 else ''}"
    if "," in field:
        names = [MONTHS[int(m)] for m in field.split(",")]
        return "in " + ", ".join(names)
    if "-" in field:
        lo, hi = field.split("-", 1)
        return f"in every month from {MONTHS[int(lo)]} through {MONTHS[int(hi)]}"
    return f"in {MONTHS[int(field)]}"


def _describe_dow(field: str) -> str:
    _parse_field(field, 0, 7)  # allow 7 as Sunday alias
    if field == "*":
        return ""
    if field.startswith("*/"):
        step = int(field.split("/")[1])
        return f"every {step} day{'s' if step > 1 else ''} of the week"
    if "," in field:
        names = [_dow_name(int(d)) for d in field.split(",")]
        return "on " + ", ".join(names)
    if "-" in field:
        lo, hi = field.split("-", 1)
        return f"on every day-of-week from {_dow_name(int(lo))} through {_dow_name(int(hi))}"
    return f"on {_dow_name(int(field))}"


def _dow_name(n: int) -> str:
    if n == 7:
        n = 0
    return DAYS_OF_WEEK[n]
