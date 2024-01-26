import datetime
import threading

from sqlalchemy.orm import Session

from offspot_metrics_backend.business.caddy_log_converter import ProcessingResult
from offspot_metrics_backend.business.indicators import ALL_INDICATORS
from offspot_metrics_backend.business.indicators.processor import (
    Processor as IndicatorProcessor,
)
from offspot_metrics_backend.business.inputs.clock_tick import ClockTick
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.kpis import ALL_KPIS
from offspot_metrics_backend.business.kpis.processor import Processor as KpiProcessor
from offspot_metrics_backend.business.period import Now, Period, Tick
from offspot_metrics_backend.constants import logger
from offspot_metrics_backend.db import dbsession

INACTIVITY_THRESHOLD_SECONDS = (
    10  # in seconds, inactivity threshold that will force processing
)


class Processor:
    """A processor is responsible for managing underlying business logic processor

    DB session are created high level in this class methods to commit all modifications
    (record creation, deletion, update) at once, and only when they are all in success.
    It makes no sense to commit only few inconsistent data. It makes no sense to make
    some inconsistent data visible to a another reader (e.g. API) which could come at
    the same time. Pending modifications are  in any case visible to the running code
    which is inside the same DB session."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.last_action: datetime.datetime | None = None
        self.last_tick_processed: Tick | None = None

    @dbsession
    def startup(self, session: Session):
        """Start the processing logic and restore data from DB to memory"""

        with self.lock:
            # Create underlying processors
            self.indicator_processor = IndicatorProcessor()
            self.kpi_processor = KpiProcessor()

            # Assign existing indicators and kpis
            self.indicator_processor.indicators = ALL_INDICATORS
            self.kpi_processor.kpis = ALL_KPIS

            # Restore data from DB to memory
            self.indicator_processor.restore_from_db(session=session)
            self.kpi_processor.restore_from_db(session=session)

    @dbsession
    def process_inputs(self, result: ProcessingResult, session: Session):
        """Process all inputs received from a log event

        This function also triggers a tick processing every time we changed
        from tick, i.e. every minutes, more or less.
        """

        with self.lock:
            # processing results are not valid
            if not result.ts:
                return

            now = Now().datetime

            # Update the last action moment
            self.last_action = now

            # Compute current tick
            current_tick = Tick(result.ts)

            # if we are just starting the app, let's set last_tick_processed to current
            # one as an approximation
            if not self.last_tick_processed:
                self.last_tick_processed = current_tick

            # if we changed tick, process one tick
            if current_tick != self.last_tick_processed:
                logger.debug(f"Natural tick at {current_tick.dt}")
                self._process_tick(now=current_tick.dt, session=session)

            # then in all cases, process inputs
            for input_ in result.inputs:
                logger.debug(f"Processing input: {input_}")
                try:
                    self.process_input(input_=input_)
                except Exception as exc:
                    logger.warn("Error processing input", exc_info=exc)

    @dbsession
    def check_for_inactivity(self, session: Session):
        """Check if the system did not received any logs for too long

        If the system did not received any log for too long, we start a new tick
        processing.
        """

        with self.lock:
            now = Now().datetime

            # If we just started the app and not received any log, this could happen
            if not self.last_action:
                self.last_action = now
            if not self.last_tick_processed:
                self.last_tick_processed = Tick(now)

            # If last action was less then 10 seconds ago, continue to wait
            if (now - self.last_action).total_seconds() < INACTIVITY_THRESHOLD_SECONDS:
                return

            # If last tick processed is too far in the past, let's force it to advance
            while Tick(now) != self.last_tick_processed:
                next_tick_dt = self.last_tick_processed.dt + datetime.timedelta(
                    minutes=1
                )
                logger.debug(f"Forcing a tick for inactivity at {next_tick_dt}")
                self._process_tick(now=next_tick_dt, session=session)
                self.last_action = now

    def _process_tick(self, now: datetime.datetime, session: Session):
        logger.info("Tick processing started")
        self.last_tick_processed = Tick(now)

        # Generate a ClockTick input
        try:
            logger.debug("Generating a clock tick")
            self.process_input(ClockTick(ts=now))
        except Exception as exc:
            logger.warn("Exception occured in clock tick", exc_info=exc)

        # Perform what needs to be done with indicators
        tick_period = Period(now)

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

        logger.debug("Tick processing completed")

    def process_input(self, input_: Input):
        """Process one input"""
        self.indicator_processor.process_input(input_)
