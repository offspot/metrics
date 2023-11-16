from sqlalchemy.orm import Session

from offspot_metrics_backend.business.indicators import ALL_INDICATORS
from offspot_metrics_backend.business.indicators.processor import (
    Processor as IndicatorProcessor,
)
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.kpis import ALL_KPIS
from offspot_metrics_backend.business.kpis.processor import Processor as KpiProcessor
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.db import dbsession


class Processor:
    """A processor is responsible for managing underlying business logic processor

    DB session are created high level in this class methods to commit all modifications
    (record creation, deletion, update) at once, and only when they are all in success.
    It makes no sense to commit only few inconsistent data. It makes no sense to make
    some inconsistent data visible to a another reader (e.g. API) which could come at
    the same time. Pending modifications are  in any case visible to the running code
    which is inside the same DB session."""

    @dbsession
    def startup(self, current_period: Period, session: Session):
        """Start the processing logic and restore data from DB to memory"""

        # Create underlying processors
        self.indicator_processor = IndicatorProcessor(current_period=current_period)
        self.kpi_processor = KpiProcessor(current_period=current_period)

        # Assign existing indicators and kpis
        self.indicator_processor.indicators = ALL_INDICATORS
        self.kpi_processor.kpis = ALL_KPIS

        # Restore data from DB to memory
        self.indicator_processor.restore_from_db(
            current_period=current_period, session=session
        )
        self.kpi_processor.restore_from_db(session=session)

    @dbsession
    def process_tick(self, tick_period: Period, session: Session):
        """Process a tick (once per minute)"""
        self.indicator_processor.process_tick(
            tick_period=tick_period,
            session=session,
        )
        kpi_updated = self.kpi_processor.process_tick(
            tick_period=tick_period,
            session=session,
        )
        if kpi_updated:
            self.indicator_processor.post_process_tick(
                tick_period=tick_period,
                session=session,
            )

    def process_input(self, input_: Input):
        """Process one input"""
        self.indicator_processor.process_input(input_)
