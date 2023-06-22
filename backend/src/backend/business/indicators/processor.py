from typing import List

from sqlalchemy.orm import Session

from backend.business.indicators.indicator import Indicator
from backend.business.inputs.input import Input
from backend.business.period import Period
from backend.db.persister import Persister


class Processor:
    """A processor is responsible for transforming inputs into indicator records"""

    def __init__(self, now: Period) -> None:
        self.indicators: List[Indicator] = []
        self.current_period = now

    def process_input(self, input: Input) -> None:
        """Update all indicators for a given input"""
        for indicator in self.indicators:
            indicator.process_input(input=input)

    def reset_state(self) -> None:
        """Reset all indicators"""
        for indicator in self.indicators:
            indicator.reset_state()

    def process_tick_has_something_to_do(self) -> bool:
        for indicator in self.indicators:
            if len(list(indicator.get_records())) > 0:
                return True
        return False

    def process_tick(
        self, now: Period, session: Session, force_period_persistence: bool = False
    ) -> None:
        """Process a clock tick"""

        # check if something has happened, otherwise we do nothing except update the
        # current period, no need to persist something if nothing happened
        if not force_period_persistence and not self.process_tick_has_something_to_do():
            if self.current_period != now:
                self.current_period = now
            return

        # persist the current period in DB
        dbPeriod = Persister.persist_period(period=self.current_period, session=session)

        # persist all indicators dimensions
        Persister.persist_indicator_dimensions(
            indicators=self.indicators, session=session
        )

        # clear indicator states that have been saved
        Persister.clear_indicator_states(session)

        # check if we are still in the same period or not
        if self.current_period == now:
            # if we are in the same period, simply persist new states
            Persister.persist_indicator_states(
                period=dbPeriod, indicators=self.indicators, session=session
            )
        else:
            # otherwise, persist records and clear in-memory states
            Persister.persist_indicator_records(
                period=dbPeriod, indicators=self.indicators, session=session
            )
            self.reset_state()
            self.current_period = now

    def process_tick_after(self, now: Period, session: Session):
        """Process a clock tick - cleanup after KPIs have been computed"""
        Persister.cleanup_old_stuff(now, session)

    def restore_from_db(self, now: Period, session: Session) -> None:
        """Restore data from database, typically after a process restart"""

        # reset all internal states, just in case
        self.reset_state()

        # retrieve last known period from DB
        lastPeriod = Persister.get_last_current_period(session)

        # if there is no last period, nothing to do except set current period
        if not lastPeriod:
            self.current_period = now
            return

        # set current period as the last one and restore state from DB
        self.current_period = lastPeriod
        for indicator in self.indicators:
            states = Persister.get_restore_data(
                lastPeriod, indicator.unique_id, session
            )
            for state in states:
                recorder = indicator.create_new_recorder()
                recorder.restore_state(state.state)
                indicator.add_recorder(state.dimension.to_values(), recorder)

        # process a tick to do what has to be done
        self.process_tick(now=now, session=session)
