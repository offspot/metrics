from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio.session import AsyncSession

from backend.business.indicators.indicator import Indicator
from backend.business.indicators.period import Period
from backend.business.inputs.input import Input
from backend.db import dbsession
from backend.db.persister import Persister


class Processor:
    """A processor is responsible for transforming inputs into indicator records"""

    def __init__(self, now: datetime) -> None:
        self.indicators: List[Indicator] = []
        self.current_period = Period(now)

    def process_input(self, input: Input) -> None:
        """Update all indicators for a given input"""
        for indicator in self.indicators:
            indicator.process_input(input=input)

    def reset_state(self) -> None:
        """Reset all indicators"""
        for indicator in self.indicators:
            indicator.reset_state()

    @dbsession
    async def process_tick(self, now: datetime, session: AsyncSession) -> None:
        """Process a clock tick"""
        await Persister.persist_indicators(
            period=self.current_period, indicators=self.indicators, session=session
        )
        now_period = Period(now)
        if self.current_period != now_period:
            self.reset_state()
            self.current_period = now_period
