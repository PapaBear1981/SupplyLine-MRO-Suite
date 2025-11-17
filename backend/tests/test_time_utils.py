from datetime import UTC, datetime, timedelta

import pytest

from time_utils import (
    add_days,
    days_between,
    format_datetime,
    get_local_timestamp,
    get_utc_now,
    get_utc_timestamp,
    parse_iso_datetime,
)


def test_get_utc_now_has_timezone():
    now = get_utc_now()
    assert now.tzinfo == UTC


def test_get_utc_timestamp_is_naive_and_recent():
    timestamp = get_utc_timestamp()
    assert timestamp.tzinfo is None
    # ensure timestamp is within a reasonable range of current time
    assert (datetime.now() - timestamp) < timedelta(seconds=5)


def test_format_datetime_handles_naive_and_aware():
    naive = datetime(2024, 1, 1, 12, 0, 0)
    aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    assert format_datetime(None) is None

    naive_formatted = format_datetime(naive)
    assert naive_formatted.endswith("+00:00")

    aware_formatted = format_datetime(aware)
    assert aware_formatted.endswith("+00:00")


def test_parse_iso_datetime_various_formats():
    iso_string = "2024-12-31T23:59:59Z"
    parsed = parse_iso_datetime(iso_string)
    assert parsed.tzinfo == UTC

    date_only = parse_iso_datetime("2024-12-31")
    assert date_only.tzinfo == UTC

    with pytest.raises(ValueError, match="Could not parse"):
        parse_iso_datetime("not-a-date")


def test_add_days_and_days_between():
    base = datetime(2024, 1, 1, 10, 30, 0)
    five_days_later = add_days(base, 5)
    assert five_days_later.date() == datetime(2024, 1, 6).date()

    # days_between should normalize to midnight and ignore tzinfo
    dt1 = datetime(2024, 1, 1, tzinfo=UTC)
    dt2 = datetime(2024, 1, 3, 12, 0, tzinfo=UTC)
    assert days_between(dt1, dt2) == 2

    assert days_between(None, dt2) is None


def test_get_local_timestamp_delegated_from_get_utc_timestamp(monkeypatch):
    sentinel = datetime(2024, 5, 17, 15, 0, 0)

    def fake_local_timestamp():
        return sentinel

    monkeypatch.setattr("time_utils.get_local_timestamp", fake_local_timestamp)
    assert get_utc_timestamp() == sentinel
