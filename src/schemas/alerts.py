"""Alert classes and schema definitions."""

from __future__ import annotations
import re
from attrs import field, define, validators
from sanic_ext import openapi as doc


@define
class TradingViewAlert:
    id: int = field(validator=[validators.ge(0)])
    name: str = field(validator=[validators.min_len(1)])
    symbol: str = field(validator=[validators.min_len(1)])
    interval: int = field(validator=[validators.ge(1)])
    direction: str = field(
        validator=[validators.matches_re("(buy|sell|close.*)", flags=re.IGNORECASE)]
    )
    price: float = field(validator=[validators.gt(0.0)])
    timestamp: str = field(validator=[validators.min_len(10)])


class TradingViewAlertSchema:
    id = doc.Integer(description="Strategy identifier", required=True)
    name = doc.String(description="Strategy name", required=True)
    symbol = doc.String(description="Symbol for the alert", required=True)
    interval = doc.Integer(
        description="Strategy operational timeframe, minimum value 1",
        required=True,
        example=15,
    )
    direction = doc.String(
        enum=[
            "BUY",
            "buy",
            "SELL",
            "sell",
            "Close entry(s) order long",
            "Close entry(s) order short",
        ],
        description="Strategy direction",
        required=True,
    )
    price = doc.Float(
        description="The current price of the security",
        required=True,
        default=1.0,
        example=1.1,
    )
    timestamp = doc.DateTime(
        description="Timestamp of the alert in UTC time without milliseconds",
        required=True,
        example="2024-06-01T03:16:17Z",
    )
