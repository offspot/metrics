import datetime

from offspot_metrics_backend.business.period import Period


def test_period_now():
    assert Period(datetime.datetime.now()) == Period.now()  # noqa: DTZ005
