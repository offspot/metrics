import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from offspot_metrics_backend.db.models import IndicatorRecord


def test_fk_missing(dbsession: Session):
    db_record = IndicatorRecord(1, 1)
    db_record.dimension_id = 1123
    db_record.period_id = 1123
    dbsession.add(db_record)

    with pytest.raises(IntegrityError):
        dbsession.flush()
