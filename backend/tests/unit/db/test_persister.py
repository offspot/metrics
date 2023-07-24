import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.db.models import IndicatorRecord


def test_fk_missing(dbsession: Session):
    dbRecord = IndicatorRecord(1, 1)
    dbRecord.dimension_id = 1123
    dbRecord.period_id = 1123
    dbsession.add(dbRecord)

    with pytest.raises(IntegrityError):
        dbsession.flush()
