"""Tests for cron-explain."""
import pytest
from cron_explain import explain, _parse_field, _describe_minute, _describe_hour, _describe_dom, _describe_month, _describe_dow, _dow_name


class TestExplain:
    def test_every_minute(self):
        assert explain("* * * * *") == "Every minute"

    def test_specific_time(self):
        result = explain("0 9 * * *")
        assert result == "At minute 0, at 09:00"

    def test_weekday_morning(self):
        result = explain("0 9 * * 1-5")
        assert result == "At minute 0, at 09:00, on every day-of-week from Monday through Friday"

    def test_every_five_minutes(self):
        result = explain("*/5 * * * *")
        assert result == "Every 5 minutes"

    def test_specific_month(self):
        result = explain("0 0 1 6 *")
        assert "in June" in result
        assert "on day-of-month 1" in result

    def test_multiple_days_of_week(self):
        result = explain("0 10 * * 1,3,5")
        assert "on Monday, Wednesday, Friday" in result

    def test_invalid_fields(self):
        with pytest.raises(ValueError, match="5 fields"):
            explain("* * *")

    def test_invalid_minute_value(self):
        with pytest.raises(ValueError, match="out of range"):
            explain("60 * * * *")

    def test_invalid_hour_value(self):
        with pytest.raises(ValueError, match="out of range"):
            explain("* 24 * * *")

    def test_invalid_dom_value(self):
        with pytest.raises(ValueError, match="out of range"):
            explain("* * 32 * *")

    def test_invalid_month_value(self):
        with pytest.raises(ValueError, match="out of range"):
            explain("* * * 13 *")

    def test_invalid_dow_value(self):
        with pytest.raises(ValueError, match="out of range"):
            explain("* * * * 8")

    def test_invalid_step_zero(self):
        with pytest.raises(ValueError, match="Invalid step"):
            explain("*/0 * * * *")

    def test_invalid_range(self):
        with pytest.raises(ValueError, match="Invalid range"):
            explain("* 10-8 * * *")


class TestParseField:
    def test_valid_single_value(self):
        assert _parse_field("5", 0, 59) == "5"

    def test_valid_range(self):
        assert _parse_field("1-5", 0, 59) == "1-5"

    def test_valid_step(self):
        assert _parse_field("*/10", 0, 59) == "*/10"

    def test_valid_list(self):
        assert _parse_field("1,2,3", 0, 59) == "1,2,3"

    def test_valid_complex(self):
        assert _parse_field("1-5,10-15,20", 0, 59) == "1-5,10-15,20"

    def test_invalid_non_numeric(self):
        with pytest.raises(ValueError, match="Invalid value"):
            _parse_field("abc", 0, 59)

    def test_invalid_step_non_numeric(self):
        with pytest.raises(ValueError, match="Invalid step"):
            _parse_field("*/abc", 0, 59)

    def test_valid_range_with_step(self):
        assert _parse_field("10-20/5", 0, 59) == "10-20/5"

    def test_valid_base_number_with_step(self):
        assert _parse_field("5/10", 0, 59) == "5/10"


class TestDescribeMinute:
    def test_every_minute(self):
        assert _describe_minute("*") == ""

    def test_step(self):
        assert _describe_minute("*/5") == "Every 5 minutes"

    def test_step_plural(self):
        assert _describe_minute("*/1") == "Every 1 minute"

    def test_specific(self):
        assert _describe_minute("30") == "At minute 30"


class TestDescribeHour:
    def test_every_hour(self):
        assert _describe_hour("*", "0") == ""

    def test_specific_hour(self):
        assert _describe_hour("9", "0") == "at 09:00"

    def test_hour_range(self):
        assert _describe_hour("9-17", "0") == "between 09:00 and 17:59"

    def test_hour_step(self):
        assert _describe_hour("*/2", "0") == "every 2 hours from 00:00"

    def test_hour_list(self):
        assert _describe_hour("8,12,18", "0") == "at 08:00 and 12:00 and 18:00"


class TestDescribeDom:
    def test_every_dom(self):
        assert _describe_dom("*") == ""

    def test_specific_dom(self):
        assert _describe_dom("15") == "on day-of-month 15"

    def test_dom_range(self):
        assert _describe_dom("1-15") == "on every day-of-month from 1 through 15"

    def test_dom_step(self):
        assert _describe_dom("*/5") == "every 5 days of the month"

    def test_dom_list(self):
        assert _describe_dom("1,15,30") == "on day-of-month 1, 15, 30"


class TestDescribeMonth:
    def test_every_month(self):
        assert _describe_month("*") == ""

    def test_specific_month(self):
        assert _describe_month("6") == "in June"

    def test_month_range(self):
        result = _describe_month("3-5")
        assert "March" in result
        assert "May" in result

    def test_month_step(self):
        assert _describe_month("*/3") == "every 3 months"

    def test_month_list(self):
        result = _describe_month("1,6,12")
        assert "January" in result
        assert "June" in result
        assert "December" in result


class TestDescribeDow:
    def test_every_dow(self):
        assert _describe_dow("*") == ""

    def test_specific_dow(self):
        assert _describe_dow("1") == "on Monday"

    def test_dow_range(self):
        result = _describe_dow("1-5")
        assert "Monday" in result
        assert "Friday" in result

    def test_dow_step(self):
        assert _describe_dow("*/2") == "every 2 days of the week"

    def test_dow_list(self):
        result = _describe_dow("1,3,5")
        assert "Monday" in result
        assert "Wednesday" in result
        assert "Friday" in result

    def test_dow_seven_as_sunday(self):
        assert _describe_dow("7") == "on Sunday"
        assert _describe_dow("0") == "on Sunday"


class TestDowName:
    def test_dow_zero_is_sunday(self):
        assert _dow_name(0) == "Sunday"

    def test_dow_seven_is_sunday(self):
        assert _dow_name(7) == "Sunday"

    def test_dow_one_is_monday(self):
        assert _dow_name(1) == "Monday"

    def test_dow_six_is_saturday(self):
        assert _dow_name(6) == "Saturday"


class TestCLI:
    """End-to-end CLI tests via subprocess.

    Uses sys.executable (the interpreter running pytest, i.e. the project venv)
    instead of a hardcoded machine path, so the suite runs anywhere.
    """

    def _run(self, *args):
        import subprocess
        import sys
        return subprocess.run(
            [sys.executable, "-m", "cron_explain", *args],
            capture_output=True,
            text=True
        )

    def test_help(self):
        result = self._run("--help")
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_valid_expression(self):
        result = self._run("0 9 * * *")
        assert result.returncode == 0
        assert "09:00" in result.stdout

    def test_invalid_expression(self):
        result = self._run("* *")
        assert result.returncode == 2
        assert "Error:" in result.stderr

    def test_no_args(self):
        result = self._run()
        assert result.returncode == 1
        assert "Usage:" in result.stdout
