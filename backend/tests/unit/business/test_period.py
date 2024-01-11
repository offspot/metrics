import datetime

from offspot_metrics_backend.business.period import Now, Period, Tick


def test_period_now():
    expected_datetime = datetime.datetime.now()  # noqa: DTZ005
    now = Now()
    assert Period(expected_datetime) == now.period
    assert Tick(expected_datetime) == now.tick
    assert int((expected_datetime - now.datetime).total_seconds()) == 0
