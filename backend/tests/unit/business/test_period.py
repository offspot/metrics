import datetime

from offspot_metrics_backend.business.period import Period


def test_period_now():
    expected_datetime = datetime.datetime.now()  # noqa: DTZ005
    now_period, now_datetime = Period.now()
    assert Period(expected_datetime) == now_period
    assert int((expected_datetime - now_datetime).total_seconds()) == 0
