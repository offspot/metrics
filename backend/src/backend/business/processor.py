from sqlalchemy.orm import Session

from ..db import dbsession
from .indicators.content_visit import ContentHomeVisit, ContentObjectVisit
from .indicators.processor import Processor as IndicatorProcessor
from .inputs.input import Input
from .kpis.content_popularity import ContentObjectPopularity, ContentPopularity
from .kpis.processor import Processor as KpiProcessor
from .period import Period


class Processor:
    """A processor is responsible to manage underlying business logic processor"""

    @dbsession
    def startup(self, now: Period, session: Session):
        """Start the processing logic and restore data from DB to memory"""

        # Create underlying processors
        self.indicator_processor = IndicatorProcessor(now=now)
        self.kpi_processor = KpiProcessor(now=now)

        # Assign existing indicators and kpis
        self.indicator_processor.indicators = [ContentHomeVisit(), ContentObjectVisit()]
        self.kpi_processor.kpis = [ContentPopularity(), ContentObjectPopularity()]

        # Restore data from DB to memory
        self.indicator_processor.restore_from_db(now=now, session=session)
        self.kpi_processor.restore_from_db(session=session)

    @dbsession
    def process_tick(self, now: Period, session: Session):
        """Process a tick (once per minute)"""
        self.indicator_processor.process_tick(
            now=now,
            session=session,
        )
        kpi_updated = self.kpi_processor.process_tick(
            now=now,
            session=session,
        )
        if kpi_updated:
            self.indicator_processor.process_tick_after(
                now=now,
                session=session,
            )

    def process_input(self, input: Input):
        """Process one input"""
        self.indicator_processor.process_input(input)