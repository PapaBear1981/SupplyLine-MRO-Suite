"""
Comprehensive tests for time_utils module.

Tests cover all functions with edge cases, timezone handling,
and various input scenarios.
"""

import pytest
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import time_utils


class TestGetUtcNow:
    """Tests for get_utc_now function."""

    def test_returns_datetime_object(self):
        """Should return a datetime object."""
        result = time_utils.get_utc_now()
        assert isinstance(result, datetime)

    def test_returns_timezone_aware_datetime(self):
        """Should return a timezone-aware datetime with UTC timezone."""
        result = time_utils.get_utc_now()
        assert result.tzinfo is not None
        assert result.tzinfo == UTC

    def test_returns_current_time(self):
        """Should return time close to current UTC time."""
        before = datetime.now(UTC)
        result = time_utils.get_utc_now()
        after = datetime.now(UTC)

        assert before <= result <= after

    def test_consecutive_calls_increase(self):
        """Consecutive calls should return increasing times."""
        first = time_utils.get_utc_now()
        # Small delay to ensure time passes
        second = time_utils.get_utc_now()

        assert second >= first


class TestGetUtcTimestamp:
    """Tests for get_utc_timestamp function."""

    def test_returns_datetime_object(self):
        """Should return a datetime object."""
        result = time_utils.get_utc_timestamp()
        assert isinstance(result, datetime)

    def test_returns_naive_datetime(self):
        """Should return a naive datetime (no timezone info)."""
        result = time_utils.get_utc_timestamp()
        assert result.tzinfo is None

    def test_returns_local_timestamp(self):
        """Should delegate to get_local_timestamp."""
        with patch.object(time_utils, 'get_local_timestamp') as mock_local:
            mock_dt = datetime(2023, 6, 15, 10, 30, 0)
            mock_local.return_value = mock_dt

            result = time_utils.get_utc_timestamp()

            mock_local.assert_called_once()
            assert result == mock_dt

    def test_returns_current_time(self):
        """Should return time close to current time."""
        before = datetime.now()
        result = time_utils.get_utc_timestamp()
        after = datetime.now()

        assert before <= result <= after


class TestGetLocalTimestamp:
    """Tests for get_local_timestamp function."""

    def test_returns_datetime_object(self):
        """Should return a datetime object."""
        result = time_utils.get_local_timestamp()
        assert isinstance(result, datetime)

    def test_returns_naive_datetime(self):
        """Should return a naive datetime (no timezone info)."""
        result = time_utils.get_local_timestamp()
        assert result.tzinfo is None

    def test_returns_current_local_time(self):
        """Should return time close to current local time."""
        before = datetime.now()
        result = time_utils.get_local_timestamp()
        after = datetime.now()

        assert before <= result <= after

    def test_has_all_datetime_components(self):
        """Should have all datetime components."""
        result = time_utils.get_local_timestamp()

        # Check that all components exist and are valid
        assert result.year >= 2000
        assert 1 <= result.month <= 12
        assert 1 <= result.day <= 31
        assert 0 <= result.hour <= 23
        assert 0 <= result.minute <= 59
        assert 0 <= result.second <= 59
        assert 0 <= result.microsecond <= 999999


class TestFormatDatetime:
    """Tests for format_datetime function."""

    def test_format_none_returns_none(self):
        """Should return None when input is None."""
        result = time_utils.format_datetime(None)
        assert result is None

    def test_format_naive_datetime(self):
        """Should format naive datetime and assume UTC."""
        dt = datetime(2023, 6, 15, 10, 30, 45)
        result = time_utils.format_datetime(dt)

        assert result == "2023-06-15T10:30:45+00:00"

    def test_format_utc_aware_datetime(self):
        """Should format UTC-aware datetime correctly."""
        dt = datetime(2023, 6, 15, 10, 30, 45, tzinfo=UTC)
        result = time_utils.format_datetime(dt)

        assert result == "2023-06-15T10:30:45+00:00"

    def test_format_datetime_with_microseconds(self):
        """Should preserve microseconds in formatted output."""
        dt = datetime(2023, 6, 15, 10, 30, 45, 123456, tzinfo=UTC)
        result = time_utils.format_datetime(dt)

        assert result == "2023-06-15T10:30:45.123456+00:00"

    def test_format_datetime_midnight(self):
        """Should handle midnight correctly."""
        dt = datetime(2023, 6, 15, 0, 0, 0, tzinfo=UTC)
        result = time_utils.format_datetime(dt)

        assert result == "2023-06-15T00:00:00+00:00"

    def test_format_datetime_end_of_day(self):
        """Should handle end of day correctly."""
        dt = datetime(2023, 6, 15, 23, 59, 59, tzinfo=UTC)
        result = time_utils.format_datetime(dt)

        assert result == "2023-06-15T23:59:59+00:00"

    def test_format_datetime_with_different_timezone(self):
        """Should preserve timezone information in output."""
        # Create datetime with different timezone offset
        tz = timezone(timedelta(hours=5, minutes=30))
        dt = datetime(2023, 6, 15, 10, 30, 45, tzinfo=tz)
        result = time_utils.format_datetime(dt)

        assert "+05:30" in result
        assert result == "2023-06-15T10:30:45+05:30"

    def test_format_leap_year_date(self):
        """Should handle leap year dates correctly."""
        dt = datetime(2024, 2, 29, 12, 0, 0, tzinfo=UTC)
        result = time_utils.format_datetime(dt)

        assert result == "2024-02-29T12:00:00+00:00"

    def test_format_year_boundary(self):
        """Should handle year boundary correctly."""
        dt = datetime(2023, 12, 31, 23, 59, 59, tzinfo=UTC)
        result = time_utils.format_datetime(dt)

        assert result == "2023-12-31T23:59:59+00:00"


class TestParseIsoDatetime:
    """Tests for parse_iso_datetime function."""

    def test_parse_empty_string_returns_none(self):
        """Should return None for empty string."""
        result = time_utils.parse_iso_datetime("")
        assert result is None

    def test_parse_iso_format_with_z_suffix(self):
        """Should parse ISO format with Z suffix."""
        result = time_utils.parse_iso_datetime("2023-06-15T10:30:45Z")

        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45
        assert result.tzinfo is not None

    def test_parse_iso_format_with_timezone_offset(self):
        """Should parse ISO format with timezone offset."""
        result = time_utils.parse_iso_datetime("2023-06-15T10:30:45+00:00")

        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45

    def test_parse_iso_format_with_positive_offset(self):
        """Should parse ISO format with positive timezone offset."""
        result = time_utils.parse_iso_datetime("2023-06-15T10:30:45+05:30")

        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30

    def test_parse_iso_format_with_negative_offset(self):
        """Should parse ISO format with negative timezone offset."""
        result = time_utils.parse_iso_datetime("2023-06-15T10:30:45-08:00")

        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30

    def test_parse_iso_format_without_timezone(self):
        """Should parse ISO format without timezone - returns naive datetime."""
        result = time_utils.parse_iso_datetime("2023-06-15T10:30:45")

        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45
        # Note: fromisoformat succeeds but doesn't add UTC, returns naive
        assert result.tzinfo is None

    def test_parse_space_separated_format(self):
        """Should parse space-separated datetime format."""
        result = time_utils.parse_iso_datetime("2023-06-15 10:30:45")

        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45
        # Note: fromisoformat succeeds but doesn't add UTC, returns naive
        assert result.tzinfo is None

    def test_parse_date_only_format(self):
        """Should parse date-only format."""
        result = time_utils.parse_iso_datetime("2023-06-15")

        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        # Note: fromisoformat succeeds but doesn't add UTC, returns naive
        assert result.tzinfo is None

    def test_parse_invalid_format_raises_error(self):
        """Should raise ValueError for invalid format."""
        with pytest.raises(ValueError, match="Could not parse datetime string"):
            time_utils.parse_iso_datetime("invalid-date")

    def test_parse_partial_date_raises_error(self):
        """Should raise ValueError for partial date."""
        with pytest.raises(ValueError, match="Could not parse datetime string"):
            time_utils.parse_iso_datetime("2023-06")

    def test_parse_with_microseconds(self):
        """Should parse datetime with microseconds."""
        result = time_utils.parse_iso_datetime("2023-06-15T10:30:45.123456+00:00")

        assert result.microsecond == 123456

    def test_parse_leap_year_date(self):
        """Should parse leap year date correctly."""
        result = time_utils.parse_iso_datetime("2024-02-29T12:00:00")

        assert result.year == 2024
        assert result.month == 2
        assert result.day == 29

    def test_parse_year_start(self):
        """Should parse start of year correctly."""
        result = time_utils.parse_iso_datetime("2023-01-01T00:00:00")

        assert result.month == 1
        assert result.day == 1

    def test_parse_year_end(self):
        """Should parse end of year correctly."""
        result = time_utils.parse_iso_datetime("2023-12-31T23:59:59")

        assert result.month == 12
        assert result.day == 31
        assert result.hour == 23
        assert result.minute == 59
        assert result.second == 59

    def test_parse_roundtrip_consistency(self):
        """Parsing and re-parsing should give consistent results."""
        original_str = "2023-06-15T10:30:45+00:00"
        parsed = time_utils.parse_iso_datetime(original_str)
        formatted = time_utils.format_datetime(parsed)
        reparsed = time_utils.parse_iso_datetime(formatted)

        assert parsed.year == reparsed.year
        assert parsed.month == reparsed.month
        assert parsed.day == reparsed.day
        assert parsed.hour == reparsed.hour
        assert parsed.minute == reparsed.minute
        assert parsed.second == reparsed.second

    def test_parse_handles_various_valid_formats(self):
        """Should successfully parse various valid datetime formats."""
        test_cases = [
            "2023-06-15T10:30:45Z",
            "2023-06-15T10:30:45+00:00",
            "2023-06-15T10:30:45-05:00",
            "2023-06-15T10:30:45",
            "2023-06-15 10:30:45",
            "2023-06-15",
        ]

        for dt_str in test_cases:
            result = time_utils.parse_iso_datetime(dt_str)
            assert isinstance(result, datetime), f"Failed for {dt_str}"
            assert result.year == 2023, f"Failed for {dt_str}"
            assert result.month == 6, f"Failed for {dt_str}"
            assert result.day == 15, f"Failed for {dt_str}"


class TestAddDays:
    """Tests for add_days function."""

    def test_add_days_to_none_returns_none(self):
        """Should return None when input datetime is None."""
        result = time_utils.add_days(None, 5)
        assert result is None

    def test_add_positive_days(self):
        """Should add positive days correctly."""
        dt = datetime(2023, 6, 15, 10, 30, 45)
        result = time_utils.add_days(dt, 5)

        assert result.day == 20
        assert result.month == 6
        assert result.year == 2023
        # Time should be preserved
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45

    def test_add_negative_days(self):
        """Should subtract days when negative."""
        dt = datetime(2023, 6, 15, 10, 30, 45)
        result = time_utils.add_days(dt, -5)

        assert result.day == 10
        assert result.month == 6
        assert result.year == 2023

    def test_add_zero_days(self):
        """Should return same datetime when adding zero days."""
        dt = datetime(2023, 6, 15, 10, 30, 45)
        result = time_utils.add_days(dt, 0)

        assert result == dt

    def test_add_days_crosses_month_boundary(self):
        """Should handle month boundary crossing."""
        dt = datetime(2023, 6, 28, 10, 30, 45)
        result = time_utils.add_days(dt, 5)

        assert result.day == 3
        assert result.month == 7
        assert result.year == 2023

    def test_add_days_crosses_year_boundary(self):
        """Should handle year boundary crossing."""
        dt = datetime(2023, 12, 28, 10, 30, 45)
        result = time_utils.add_days(dt, 5)

        assert result.day == 2
        assert result.month == 1
        assert result.year == 2024

    def test_add_days_preserves_timezone(self):
        """Should preserve timezone information."""
        dt = datetime(2023, 6, 15, 10, 30, 45, tzinfo=UTC)
        result = time_utils.add_days(dt, 5)

        assert result.tzinfo == UTC

    def test_add_large_number_of_days(self):
        """Should handle large number of days."""
        dt = datetime(2023, 6, 15, 10, 30, 45)
        result = time_utils.add_days(dt, 365)

        assert result.year == 2024
        assert result.month == 6
        assert result.day == 14  # 2024 is a leap year

    def test_subtract_to_previous_year(self):
        """Should handle subtracting days to previous year."""
        dt = datetime(2023, 1, 5, 10, 30, 45)
        result = time_utils.add_days(dt, -10)

        assert result.year == 2022
        assert result.month == 12
        assert result.day == 26

    def test_add_days_leap_year(self):
        """Should handle leap year correctly."""
        dt = datetime(2024, 2, 28, 10, 30, 45)
        result = time_utils.add_days(dt, 1)

        assert result.day == 29
        assert result.month == 2
        assert result.year == 2024

    def test_add_days_non_leap_year(self):
        """Should handle non-leap year correctly."""
        dt = datetime(2023, 2, 28, 10, 30, 45)
        result = time_utils.add_days(dt, 1)

        assert result.day == 1
        assert result.month == 3
        assert result.year == 2023


class TestDaysBetween:
    """Tests for days_between function."""

    def test_days_between_none_first_returns_none(self):
        """Should return None when first datetime is None."""
        dt2 = datetime(2023, 6, 20)
        result = time_utils.days_between(None, dt2)
        assert result is None

    def test_days_between_same_day(self):
        """Should return 0 for same day."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45)
        dt2 = datetime(2023, 6, 15, 14, 45, 30)
        result = time_utils.days_between(dt1, dt2)

        assert result == 0

    def test_days_between_positive_difference(self):
        """Should return positive days when dt2 is after dt1."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45)
        dt2 = datetime(2023, 6, 20, 14, 45, 30)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5

    def test_days_between_negative_difference(self):
        """Should return negative days when dt2 is before dt1."""
        dt1 = datetime(2023, 6, 20, 10, 30, 45)
        dt2 = datetime(2023, 6, 15, 14, 45, 30)
        result = time_utils.days_between(dt1, dt2)

        assert result == -5

    def test_days_between_without_second_datetime(self):
        """Should use current timestamp when dt2 is not provided."""
        # Use a date in the past
        dt1 = datetime(2020, 1, 1)
        result = time_utils.days_between(dt1)

        # Result should be positive and reasonably large
        assert result > 0
        assert isinstance(result, int)

    def test_days_between_with_timezone_aware_first(self):
        """Should handle timezone-aware first datetime."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45, tzinfo=UTC)
        dt2 = datetime(2023, 6, 20, 14, 45, 30)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5

    def test_days_between_with_timezone_aware_second(self):
        """Should handle timezone-aware second datetime."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45)
        dt2 = datetime(2023, 6, 20, 14, 45, 30, tzinfo=UTC)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5

    def test_days_between_both_timezone_aware(self):
        """Should handle both timezone-aware datetimes."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45, tzinfo=UTC)
        dt2 = datetime(2023, 6, 20, 14, 45, 30, tzinfo=UTC)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5

    def test_days_between_crosses_month_boundary(self):
        """Should handle month boundary correctly."""
        dt1 = datetime(2023, 6, 28)
        dt2 = datetime(2023, 7, 3)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5

    def test_days_between_crosses_year_boundary(self):
        """Should handle year boundary correctly."""
        dt1 = datetime(2023, 12, 28)
        dt2 = datetime(2024, 1, 2)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5

    def test_days_between_leap_year(self):
        """Should handle leap year correctly."""
        dt1 = datetime(2024, 2, 28)
        dt2 = datetime(2024, 3, 1)
        result = time_utils.days_between(dt1, dt2)

        assert result == 2  # Feb 28 -> Feb 29 -> Mar 1

    def test_days_between_non_leap_year(self):
        """Should handle non-leap year correctly."""
        dt1 = datetime(2023, 2, 28)
        dt2 = datetime(2023, 3, 1)
        result = time_utils.days_between(dt1, dt2)

        assert result == 1

    def test_days_between_large_difference(self):
        """Should handle large day differences."""
        dt1 = datetime(2020, 1, 1)
        dt2 = datetime(2023, 1, 1)
        result = time_utils.days_between(dt1, dt2)

        # 3 years with one leap year (2020)
        expected = 365 + 365 + 366  # 2020 is leap year
        assert result == expected

    def test_days_between_ignores_time_component(self):
        """Should calculate days based on dates, not times."""
        dt1 = datetime(2023, 6, 15, 23, 59, 59)
        dt2 = datetime(2023, 6, 16, 0, 0, 1)
        result = time_utils.days_between(dt1, dt2)

        # Should be 1 day, not 0 (based on date, not time difference)
        assert result == 1

    def test_days_between_microseconds_ignored(self):
        """Should ignore microseconds in calculation."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45, 999999)
        dt2 = datetime(2023, 6, 20, 14, 45, 30, 1)
        result = time_utils.days_between(dt1, dt2)

        assert result == 5


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_format_and_parse_roundtrip(self):
        """Should be able to format and parse back to same value."""
        original = datetime(2023, 6, 15, 10, 30, 45, tzinfo=UTC)
        formatted = time_utils.format_datetime(original)
        parsed = time_utils.parse_iso_datetime(formatted)

        assert parsed.year == original.year
        assert parsed.month == original.month
        assert parsed.day == original.day
        assert parsed.hour == original.hour
        assert parsed.minute == original.minute
        assert parsed.second == original.second

    def test_add_days_then_calculate_difference(self):
        """Adding days and calculating difference should match."""
        dt1 = datetime(2023, 6, 15, 10, 30, 45)
        dt2 = time_utils.add_days(dt1, 10)
        diff = time_utils.days_between(dt1, dt2)

        assert diff == 10

    def test_get_utc_now_can_be_formatted(self):
        """get_utc_now result can be formatted."""
        now = time_utils.get_utc_now()
        formatted = time_utils.format_datetime(now)

        assert isinstance(formatted, str)
        assert "T" in formatted
        assert "+00:00" in formatted

    def test_get_local_timestamp_can_be_used_in_days_between(self):
        """get_local_timestamp can be used in days_between calculation."""
        past = datetime(2020, 1, 1)
        local_now = time_utils.get_local_timestamp()
        diff = time_utils.days_between(past, local_now)

        assert diff > 0
        assert isinstance(diff, int)
