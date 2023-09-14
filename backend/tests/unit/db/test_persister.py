import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from offspot_metrics_backend.db import dbsession, gen_dbsession
from offspot_metrics_backend.db.models import IndicatorRecord


def test_fk_missing(dbsession: Session):
    """test that missing foreign key raises an exception when using the fixture"""
    db_record = IndicatorRecord(1, 1)
    db_record.dimension_id = 1123
    db_record.period_id = 1123
    dbsession.add(db_record)

    with pytest.raises(IntegrityError):
        dbsession.flush()


@dbsession
def test_dbsession(session: Session):
    """test that missing foreign key raises an exception when using the annotation"""
    db_record = IndicatorRecord(1, 1)
    db_record.dimension_id = 1123
    db_record.period_id = 1123
    session.add(db_record)

    with pytest.raises(IntegrityError):
        session.flush()


def test_gen_dbsession():
    """test that missing foreign key raises an exception when using the generator"""
    session = gen_dbsession().__next__()
    db_record = IndicatorRecord(1, 1)
    db_record.dimension_id = 1123
    db_record.period_id = 1123
    session.add(db_record)

    with pytest.raises(IntegrityError):
        session.flush()
