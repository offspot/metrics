from sqlalchemy.orm import Session

from offspot_metrics_backend.business.indicators.indicator import Indicator
from offspot_metrics_backend.business.inputs.input import Input
from offspot_metrics_backend.business.period import Period
from offspot_metrics_backend.constants import logger
from offspot_metrics_backend.db.persister import Persister


class Processor:
    """A processor is responsible for transforming inputs into indicator records"""

    def __init__(self) -> None:
        self.indicators: list[Indicator] = []
        self.current_period: Period | None = None

    def process_input(self, input_: Input) -> None:
        """Update all indicators for a given input"""
        for indicator in self.indicators:
            try:
                indicator.process_input(input_=input_)
            except Exception as exc:
                logger.debug(
                    f"Error processing input for indicator {indicator.unique_id}",
                    exc_info=exc,
                )

    def reset_state(self) -> None:
        """Reset all indicators"""
        for indicator in self.indicators:
            indicator.reset_state()

    @property
    def has_records_for_our_indicators(self) -> bool:
        """Returns true if there is at least one indicator with a record"""
        for indicator in self.indicators:
            if next(indicator.get_records(), None):
                return True
        return False

    def process_tick(self, tick_period: Period, session: Session) -> None:
        """Process a clock tick"""

        # If we do not have a current period, then it means that we are starting from a
        # fresh DB, so let's set the current period to the tick one
        if not self.current_period:
            self.current_period = tick_period

        # check if something has happened, otherwise we do nothing except update the
        # current period, no need to persist something if nothing happened
        if not self.has_records_for_our_indicators:
            if self.current_period != tick_period:
                self.current_period = tick_period
            return

        # persist the current period in DB
        db_period = Persister.persist_period(
            period=self.current_period, session=session
        )

        # persist all indicators dimensions
        Persister.persist_indicator_dimensions(
            indicators=self.indicators, session=session
        )

        # clear former indicator states that have been saved previously
        Persister.clear_indicator_states(session)

        # check if we are still in the same period or not
        if self.current_period == tick_period:
            # if we are in the same period, simply persist new states
            Persister.persist_indicator_states(
                period=db_period, indicators=self.indicators, session=session
            )
        else:
            # otherwise, persist records and clear in-memory states
            Persister.persist_indicator_records(
                period=db_period, indicators=self.indicators, session=session
            )
            self.reset_state()
            self.current_period = tick_period

    def post_process_tick(self, tick_period: Period, session: Session):
        """Process a clock tick - cleanup after KPIs have been computed"""
        Persister.cleanup_obsolete_data(tick_period, session)

    def restore_from_db(self, session: Session) -> None:
        """Restore data from database, typically after a process restart"""

        # reset all internal states, just in case
        self.reset_state()

        # retrieve last known period from DB
        last_period = Persister.get_last_period(session)

        # if there is no last period, nothing to do
        if not last_period:
            return

        # check if we have indicator records for the last period ; if we have,
        # then it means that everything has been recorded, we do not need to restore
        # states (there are none anyway) and the current_period is the next after
        # last_period
        if Persister.has_indicator_records_for_period(
            period=last_period, session=session
        ):
            self.current_period = last_period.get_next()
            return

        # set current period as the last one and restore state from DB
        self.current_period = last_period
        for indicator in self.indicators:
            states = Persister.get_restore_data(
                last_period, indicator.unique_id, session
            )
            for state in states:
                recorder = indicator.get_new_recorder()
                recorder.restore_state(state.state)
                indicator.add_recorder(state.dimension.to_values(), recorder)
