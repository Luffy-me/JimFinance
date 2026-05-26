"""
Economic Data Pipeline - Fetch and manage economic indicators.

Provides:
- Historical economic data
- Indicator updates
- Data validation and normalization
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class IndicatorType(str, Enum):
    """Economic indicator types."""
    GDP_GROWTH = "gdp_growth"
    UNEMPLOYMENT = "unemployment"
    INFLATION = "inflation"
    INTEREST_RATE = "interest_rate"
    YIELD_CURVE = "yield_curve"
    CREDIT_SPREAD = "credit_spread"
    VIX_INDEX = "vix_index"
    JOBS_REPORT = "jobs_report"
    CONSUMER_CONFIDENCE = "consumer_confidence"
    ISM_MANUFACTURING = "ism_manufacturing"


@dataclass
class EconomicIndicator:
    """Economic indicator definition."""
    name: str
    indicator_type: IndicatorType
    country: str
    frequency: str  # "monthly", "quarterly", "annual"
    source: str
    

@dataclass
class IndicatorData:
    """Economic indicator data point."""
    indicator: EconomicIndicator
    timestamp: datetime
    value: float
    previous_value: Optional[float]
    percent_change: float
    is_forecast: bool
    confidence: float
    assumptions: List[str]


class DataPipeline:
    """
    Economic data pipeline for collecting and normalizing indicators.
    """
    
    # Historical indicator values (simplified)
    HISTORICAL_DATA = {
        IndicatorType.GDP_GROWTH: {
            2023: 0.025,  # 2.5%
            2022: 0.020,
            2021: 0.057,
            2020: -0.031,
        },
        IndicatorType.UNEMPLOYMENT: {
            2023: 0.038,  # 3.8%
            2022: 0.036,
            2021: 0.050,
            2020: 0.083,
        },
        IndicatorType.INFLATION: {
            2023: 0.0328,  # 3.28%
            2022: 0.0801,
            2021: 0.0470,
            2020: 0.0124,
        },
        IndicatorType.INTEREST_RATE: {
            2023: 0.053,  # 5.3%
            2022: 0.0167,
            2021: 0.0008,
            2020: 0.0038,
        },
    }
    
    # Forward guidance/forecasts
    FORWARD_GUIDANCE = {
        IndicatorType.GDP_GROWTH: {
            2024: 0.015,  # 1.5% expected
            2025: 0.020,
        },
        IndicatorType.UNEMPLOYMENT: {
            2024: 0.042,  # 4.2% expected
            2025: 0.043,
        },
        IndicatorType.INFLATION: {
            2024: 0.025,  # 2.5% expected
            2025: 0.025,
        },
    }
    
    def __init__(self, country: str = "US"):
        """
        Initialize data pipeline.
        
        Args:
            country: Country code for economic data
        """
        self.logger = logger
        self.country = country
    
    def get_indicator(
        self,
        indicator_type: IndicatorType,
        date: datetime,
    ) -> Optional[IndicatorData]:
        """
        Get economic indicator value for date.
        
        Args:
            indicator_type: Type of economic indicator
            date: Date to fetch data for
            
        Returns:
            IndicatorData or None if not available
        """
        year = date.year
        
        # Check if historical data exists
        if indicator_type in self.HISTORICAL_DATA:
            current_value = self.HISTORICAL_DATA[indicator_type].get(year)
            previous_value = self.HISTORICAL_DATA[indicator_type].get(year - 1)
            
            if current_value is not None:
                percent_change = 0
                if previous_value is not None:
                    percent_change = (current_value - previous_value) / abs(previous_value) if previous_value != 0 else 0
                
                indicator = EconomicIndicator(
                    name=indicator_type.value,
                    indicator_type=indicator_type,
                    country=self.country,
                    frequency="annual",
                    source="Federal Reserve",
                )
                
                return IndicatorData(
                    indicator=indicator,
                    timestamp=date,
                    value=current_value,
                    previous_value=previous_value,
                    percent_change=percent_change,
                    is_forecast=False,
                    confidence=0.90,
                    assumptions=[
                        f"Data from {self.country} federal statistics",
                        "Subject to future revision",
                        "Historical annual averages",
                    ],
                )
        
        return None
    
    def get_forecast(
        self,
        indicator_type: IndicatorType,
        year: int,
    ) -> Optional[float]:
        """
        Get forward guidance forecast for indicator.
        
        Args:
            indicator_type: Type of indicator
            year: Forecast year
            
        Returns:
            Forecast value or None
        """
        return self.FORWARD_GUIDANCE.get(indicator_type, {}).get(year)
    
    def get_indicator_series(
        self,
        indicator_type: IndicatorType,
        start_year: int,
        end_year: int,
    ) -> List[IndicatorData]:
        """
        Get time series of indicator values.
        
        Args:
            indicator_type: Type of indicator
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            List of IndicatorData for years
        """
        series = []
        
        if indicator_type not in self.HISTORICAL_DATA:
            return series
        
        historical = self.HISTORICAL_DATA[indicator_type]
        
        for year in range(start_year, end_year + 1):
            date = datetime(year, 12, 31)
            indicator_data = self.get_indicator(indicator_type, date)
            if indicator_data:
                series.append(indicator_data)
        
        return series
    
    def validate_indicator_data(self, indicator_data: IndicatorData) -> Tuple[bool, List[str]]:
        """
        Validate economic indicator data.
        
        Args:
            indicator_data: Indicator data to validate
            
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []
        
        # Check value ranges
        if indicator_data.indicator.indicator_type == IndicatorType.UNEMPLOYMENT:
            if not (0 <= indicator_data.value <= 0.30):
                errors.append("Unemployment rate outside 0-30% range")
        
        elif indicator_data.indicator.indicator_type == IndicatorType.INFLATION:
            if not (-0.05 <= indicator_data.value <= 0.15):
                errors.append("Inflation rate outside -5% to 15% range")
        
        elif indicator_data.indicator.indicator_type == IndicatorType.INTEREST_RATE:
            if not (-0.01 <= indicator_data.value <= 0.20):
                errors.append("Interest rate outside -1% to 20% range")
        
        # Check confidence range
        if not (0 <= indicator_data.confidence <= 1.0):
            errors.append("Confidence must be 0-1")
        
        return len(errors) == 0, errors
    
    def interpolate_quarterly(self, annual_value: float) -> List[float]:
        """
        Interpolate annual value to quarterly values.
        
        Args:
            annual_value: Annual indicator value
            
        Returns:
            List of 4 quarterly values
        """
        # Simple approach: distribute evenly
        quarterly = [annual_value / 4] * 4
        return quarterly
