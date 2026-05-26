"""FX/Currency intelligence and analysis.

Modules:
- rate_tracker: Exchange rate data management
- exposure_calculator: FX exposure aggregation
- forecasting_model: Currency movement predictions
"""

from .rate_tracker import (
    ExchangeRate,
    CurrencyData,
    RateTracker,
)
from .exposure_calculator import (
    FXExposure,
    ExposureReport,
    ExposureCalculator,
)
from .forecasting_model import (
    ForecastDirection,
    CurrencyForecast,
    ForecastingModel,
)

__all__ = [
    "ExchangeRate",
    "CurrencyData",
    "RateTracker",
    "FXExposure",
    "ExposureReport",
    "ExposureCalculator",
    "ForecastDirection",
    "CurrencyForecast",
    "ForecastingModel",
]
