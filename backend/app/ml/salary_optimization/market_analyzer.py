"""
Market Analyzer - Analyze job market data and salary trends.

Provides:
- Market salary data by role/location
- Industry growth and trends
- Demand forecasting
- Skill premium analysis
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class JobMarketData:
    """Job market data for role."""
    job_title: str
    location: str
    median_salary: float
    salary_range_low: float
    salary_range_high: float
    cost_of_living_index: float
    job_growth_rate: float  # Annual growth %
    demand_level: str  # "low", "moderate", "high", "critical"
    number_of_openings: int
    average_experience_years: int


@dataclass
class SalaryTrend:
    """Salary trend analysis."""
    job_title: str
    current_median: float
    trend_direction: str  # "increasing", "stable", "declining"
    yoy_change: float  # Year-over-year %
    trending_skills: List[str]
    median_experience: int
    advancement_potential: str  # "high", "moderate", "low"
    confidence: float
    assumptions: List[str]


class MarketAnalyzer:
    """
    Analyzes job market trends and salary data.
    """
    
    # Sample market data by job title and location
    MARKET_DATA = {
        "Software Engineer": {
            "San Francisco": {
                "median": 180000,
                "low": 120000,
                "high": 250000,
                "cost_of_living": 1.85,
            },
            "New York": {
                "median": 165000,
                "low": 110000,
                "high": 240000,
                "cost_of_living": 1.70,
            },
            "Austin": {
                "median": 145000,
                "low": 95000,
                "high": 200000,
                "cost_of_living": 1.10,
            },
            "Remote": {
                "median": 155000,
                "low": 100000,
                "high": 220000,
                "cost_of_living": 1.00,
            },
        },
        "Data Scientist": {
            "San Francisco": {
                "median": 195000,
                "low": 130000,
                "high": 270000,
                "cost_of_living": 1.85,
            },
            "New York": {
                "median": 175000,
                "low": 120000,
                "high": 250000,
                "cost_of_living": 1.70,
            },
            "Remote": {
                "median": 165000,
                "low": 110000,
                "high": 230000,
                "cost_of_living": 1.00,
            },
        },
        "Product Manager": {
            "San Francisco": {
                "median": 200000,
                "low": 140000,
                "high": 280000,
                "cost_of_living": 1.85,
            },
            "New York": {
                "median": 185000,
                "low": 130000,
                "high": 260000,
                "cost_of_living": 1.70,
            },
        },
        "Financial Analyst": {
            "New York": {
                "median": 150000,
                "low": 100000,
                "high": 220000,
                "cost_of_living": 1.70,
            },
            "Chicago": {
                "median": 130000,
                "low": 85000,
                "high": 190000,
                "cost_of_living": 1.00,
            },
        },
    }
    
    # Job growth rates by role
    JOB_GROWTH_RATES = {
        "Software Engineer": 0.15,  # 15% annual growth
        "Data Scientist": 0.18,
        "Product Manager": 0.08,
        "Financial Analyst": 0.05,
    }
    
    # Trending skills and premiums
    SKILL_PREMIUMS = {
        "AI/ML": 0.25,  # +25% salary premium
        "Cloud": 0.15,
        "DevOps": 0.12,
        "Security": 0.10,
        "Full-stack": 0.08,
        "Leadership": 0.20,
        "Product Strategy": 0.15,
    }
    
    def __init__(self):
        """Initialize market analyzer."""
        self.logger = logger
    
    def get_market_salary(
        self,
        job_title: str,
        location: str,
    ) -> Optional[JobMarketData]:
        """
        Get current market salary data.
        
        Args:
            job_title: Job title
            location: Geographic location
            
        Returns:
            JobMarketData or None if not found
        """
        if job_title not in self.MARKET_DATA:
            return None
        
        if location not in self.MARKET_DATA[job_title]:
            return None
        
        data = self.MARKET_DATA[job_title][location]
        growth_rate = self.JOB_GROWTH_RATES.get(job_title, 0.05)
        
        # Determine demand level
        if growth_rate > 0.12:
            demand = "critical"
        elif growth_rate > 0.08:
            demand = "high"
        elif growth_rate > 0.03:
            demand = "moderate"
        else:
            demand = "low"
        
        return JobMarketData(
            job_title=job_title,
            location=location,
            median_salary=data["median"],
            salary_range_low=data["low"],
            salary_range_high=data["high"],
            cost_of_living_index=data["cost_of_living"],
            job_growth_rate=growth_rate,
            demand_level=demand,
            number_of_openings=int(1000 * growth_rate),  # Simplified
            average_experience_years=5,  # Default
        )
    
    def analyze_salary_trends(
        self,
        job_title: str,
        years_of_experience: int,
    ) -> Optional[SalaryTrend]:
        """
        Analyze salary trends for job role.
        
        Args:
            job_title: Job title
            years_of_experience: Years of experience
            
        Returns:
            SalaryTrend analysis
        """
        if job_title not in self.MARKET_DATA:
            return None
        
        # Get median from remote market as baseline
        if "Remote" in self.MARKET_DATA[job_title]:
            current_median = self.MARKET_DATA[job_title]["Remote"]["median"]
        else:
            current_median = list(self.MARKET_DATA[job_title].values())[0]["median"]
        
        # Trend direction (simplified)
        growth_rate = self.JOB_GROWTH_RATES.get(job_title, 0.05)
        if growth_rate > 0.10:
            trend = "increasing"
            yoy_change = growth_rate
        elif growth_rate > 0.03:
            trend = "stable"
            yoy_change = 0.02
        else:
            trend = "declining"
            yoy_change = -0.01
        
        # Trending skills
        trending = []
        for skill, premium in self.SKILL_PREMIUMS.items():
            if premium > 0.15:
                trending.append(skill)
        
        # Advancement potential
        if growth_rate > 0.12:
            potential = "high"
        elif growth_rate > 0.05:
            potential = "moderate"
        else:
            potential = "low"
        
        assumptions = [
            f"Data from major job market surveys",
            f"Based on {job_title} market trends",
            "Assumes stable economic conditions",
            "Skills premium based on current demand",
        ]
        
        return SalaryTrend(
            job_title=job_title,
            current_median=current_median,
            trend_direction=trend,
            yoy_change=yoy_change,
            trending_skills=trending,
            median_experience=5,
            advancement_potential=potential,
            confidence=0.80,
            assumptions=assumptions,
        )
    
    def calculate_salary_with_experience(
        self,
        base_market_salary: float,
        years_of_experience: int,
        experience_curve: str = "typical",
    ) -> float:
        """
        Adjust salary for experience level.
        
        Args:
            base_market_salary: Base market salary (e.g., 5 years exp)
            years_of_experience: Years of experience
            experience_curve: "aggressive", "typical", "conservative"
            
        Returns:
            Adjusted salary for experience
        """
        # Experience curve factors
        curves = {
            "aggressive": {  # Fast growth for early career
                1: 0.65,
                3: 0.85,
                5: 1.00,
                7: 1.15,
                10: 1.35,
                15: 1.55,
                20: 1.70,
            },
            "typical": {  # Normal progression
                1: 0.60,
                3: 0.80,
                5: 1.00,
                7: 1.10,
                10: 1.25,
                15: 1.40,
                20: 1.50,
            },
            "conservative": {  # Slower growth
                1: 0.55,
                3: 0.75,
                5: 1.00,
                7: 1.05,
                10: 1.15,
                15: 1.25,
                20: 1.35,
            },
        }
        
        curve = curves.get(experience_curve, curves["typical"])
        
        # Interpolate between years
        sorted_years = sorted(curve.keys())
        
        for i in range(len(sorted_years) - 1):
            y1, y2 = sorted_years[i], sorted_years[i + 1]
            if y1 <= years_of_experience <= y2:
                f1, f2 = curve[y1], curve[y2]
                # Linear interpolation
                factor = f1 + (f2 - f1) * (years_of_experience - y1) / (y2 - y1)
                return base_market_salary * factor
        
        # Extrapolate beyond max years
        if years_of_experience > sorted_years[-1]:
            return base_market_salary * curve[sorted_years[-1]] * 1.01 ** (years_of_experience - sorted_years[-1])
        
        return base_market_salary * curve[sorted_years[0]]
    
    def calculate_skill_premium(
        self,
        base_salary: float,
        skills: List[str],
    ) -> Dict[str, float]:
        """
        Calculate salary premium from skills.
        
        Args:
            base_salary: Base salary without premiums
            skills: List of skills possessed
            
        Returns:
            Adjusted salary with premiums
        """
        total_premium = 0
        skill_breakdown = {}
        
        for skill in skills:
            if skill in self.SKILL_PREMIUMS:
                premium = self.SKILL_PREMIUMS[skill]
                total_premium += premium
                skill_breakdown[skill] = base_salary * premium
        
        # Cap total premium at 50%
        total_premium = min(0.50, total_premium)
        adjusted_salary = base_salary * (1 + total_premium)
        
        return {
            "base_salary": base_salary,
            "total_premium_percent": total_premium * 100,
            "adjusted_salary": adjusted_salary,
            "skill_premiums": skill_breakdown,
        }
