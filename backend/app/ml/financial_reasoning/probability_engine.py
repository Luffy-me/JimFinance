"""
Probability Engine - Probabilistic financial analysis.
Monte Carlo simulations, distributions, and confidence intervals.
"""

import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from scipy import stats
from scipy.stats import norm, lognorm

logger = logging.getLogger(__name__)


@dataclass
class ProbabilityDistribution:
    """Probability distribution for financial variable."""
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_5: float  # 5th percentile (worst case)
    percentile_50: float  # Median
    percentile_95: float  # 95th percentile (best case)
    distribution_type: str  # 'normal', 'lognormal'


class ProbabilityEngine:
    """
    Probabilistic financial analysis using Monte Carlo methods.
    Generates probability distributions for financial outcomes.
    """
    
    def __init__(self, num_simulations: int = 10000):
        """
        Initialize probability engine.
        
        Args:
            num_simulations: Number of Monte Carlo simulations
        """
        self.logger = logger
        self.num_simulations = num_simulations
    
    def run_monte_carlo_simulation(
        self,
        initial_balance: float,
        monthly_income_mean: float,
        monthly_income_std: float,
        monthly_expenses_mean: float,
        monthly_expenses_std: float,
        months_to_simulate: int = 60,
        annual_inflation: float = 0.03,
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation to project financial outcomes.
        
        Args:
            initial_balance: Starting balance
            monthly_income_mean: Mean monthly income
            monthly_income_std: Std dev of monthly income
            monthly_expenses_mean: Mean monthly expenses
            monthly_expenses_std: Std dev of monthly expenses
            months_to_simulate: Number of months to simulate
            annual_inflation: Annual inflation rate for expenses
            
        Returns:
            Dictionary with simulation results and distributions
        """
        # Initialize simulation results
        end_balances = np.zeros(self.num_simulations)
        min_balances = np.zeros(self.num_simulations)
        negative_balance_count = 0
        
        # Monthly inflation
        monthly_inflation = annual_inflation / 12
        
        # Run simulations
        for sim_idx in range(self.num_simulations):
            balance = initial_balance
            min_balance = balance
            
            for month in range(months_to_simulate):
                # Generate income and expenses for this month
                income = np.random.normal(monthly_income_mean, monthly_income_std)
                income = max(0, income)  # Income can't be negative
                
                # Adjust expenses for inflation
                inflated_mean = monthly_expenses_mean * ((1 + monthly_inflation) ** month)
                expenses = np.random.normal(inflated_mean, monthly_expenses_std)
                expenses = max(0, expenses)  # Expenses can't be negative
                
                # Update balance
                balance += income - expenses
                min_balance = min(min_balance, balance)
                
                # Track if went negative
                if balance < 0:
                    negative_balance_count += 1
            
            end_balances[sim_idx] = balance
            min_balances[sim_idx] = min_balance
        
        # Calculate statistics
        return {
            "simulations": self.num_simulations,
            "months_simulated": months_to_simulate,
            "initial_balance": initial_balance,
            "ending_balance_distribution": self._calculate_distribution(end_balances),
            "minimum_balance_distribution": self._calculate_distribution(min_balances),
            "probability_positive_end": np.mean(end_balances > 0),
            "probability_never_negative": np.mean(min_balances >= 0),
            "probability_bankruptcy": negative_balance_count / self.num_simulations,
            "end_balance_samples": end_balances.tolist()[:100],  # Return sample
        }
    
    def estimate_income_distribution(
        self,
        income_history: List[float],
    ) -> ProbabilityDistribution:
        """
        Estimate income distribution from history.
        
        Args:
            income_history: List of historical monthly incomes
            
        Returns:
            ProbabilityDistribution object
        """
        if not income_history or len(income_history) < 3:
            # Default if insufficient data
            return ProbabilityDistribution(
                mean=0.0,
                std_dev=0.0,
                min_value=0.0,
                max_value=0.0,
                percentile_5=0.0,
                percentile_50=0.0,
                percentile_95=0.0,
                distribution_type="normal",
            )
        
        income_array = np.array(income_history)
        
        mean = np.mean(income_array)
        std_dev = np.std(income_array)
        min_val = np.min(income_array)
        max_val = np.max(income_array)
        
        # Calculate percentiles
        p5 = np.percentile(income_array, 5)
        p50 = np.percentile(income_array, 50)
        p95 = np.percentile(income_array, 95)
        
        return ProbabilityDistribution(
            mean=mean,
            std_dev=std_dev,
            min_value=min_val,
            max_value=max_val,
            percentile_5=p5,
            percentile_50=p50,
            percentile_95=p95,
            distribution_type="normal" if std_dev > 0 else "constant",
        )
    
    def estimate_expense_distribution(
        self,
        expense_history: List[float],
        category: str = "all",
    ) -> ProbabilityDistribution:
        """
        Estimate expense distribution from history.
        
        Args:
            expense_history: List of historical expenses
            category: Expense category for better modeling
            
        Returns:
            ProbabilityDistribution object
        """
        if not expense_history or len(expense_history) < 3:
            return ProbabilityDistribution(
                mean=0.0,
                std_dev=0.0,
                min_value=0.0,
                max_value=0.0,
                percentile_5=0.0,
                percentile_50=0.0,
                percentile_95=0.0,
                distribution_type="normal",
            )
        
        expense_array = np.array(expense_history)
        
        mean = np.mean(expense_array)
        std_dev = np.std(expense_array)
        min_val = np.min(expense_array)
        max_val = np.max(expense_array)
        
        # For expenses, lognormal might fit better (right-skewed)
        # But use normal for simplicity with adjustment
        p5 = np.percentile(expense_array, 5)
        p50 = np.percentile(expense_array, 50)
        p95 = np.percentile(expense_array, 95)
        
        # Detect if lognormal is better fit
        distribution_type = "normal"
        if std_dev > mean * 0.5:  # High variability
            distribution_type = "lognormal"
        
        return ProbabilityDistribution(
            mean=mean,
            std_dev=std_dev,
            min_value=min_val,
            max_value=max_val,
            percentile_5=p5,
            percentile_50=p50,
            percentile_95=p95,
            distribution_type=distribution_type,
        )
    
    def calculate_event_probability(
        self,
        event_threshold: float,
        mean: float,
        std_dev: float,
        direction: str = "above",  # 'above' or 'below'
    ) -> float:
        """
        Calculate probability of event (e.g., expenses > threshold).
        
        Args:
            event_threshold: Threshold value
            mean: Distribution mean
            std_dev: Distribution std dev
            direction: 'above' or 'below' threshold
            
        Returns:
            Probability (0-1)
        """
        if std_dev == 0:
            if direction == "above":
                return 1.0 if mean > event_threshold else 0.0
            else:
                return 1.0 if mean < event_threshold else 0.0
        
        z_score = (event_threshold - mean) / std_dev
        
        if direction == "above":
            probability = 1 - norm.cdf(z_score)
        else:
            probability = norm.cdf(z_score)
        
        return np.clip(probability, 0, 1)
    
    def runway_probability_distribution(
        self,
        current_balance: float,
        burn_rate_distribution: ProbabilityDistribution,
        months_ahead: int = 60,
    ) -> Dict[str, float]:
        """
        Calculate probability distribution of runway months.
        
        Args:
            current_balance: Current balance
            burn_rate_distribution: Distribution of monthly burn rate
            months_ahead: How far ahead to calculate
            
        Returns:
            Dictionary with probability of runway at key points
        """
        probabilities = {}
        
        # Calculate for key runway points
        thresholds = [1, 3, 6, 12, 24, 36]  # months
        
        for months in thresholds:
            if months > months_ahead:
                continue
            
            # Probability that runway lasts at least this many months
            # Runway = balance / burn_rate
            required_balance = burn_rate_distribution.percentile_95 * months
            
            # Probability of having enough balance
            prob = self.calculate_event_probability(
                event_threshold=required_balance,
                mean=current_balance,
                std_dev=current_balance * 0.1,  # 10% uncertainty
                direction="above",
            )
            
            probabilities[f"runway_at_least_{months}_months"] = prob
        
        return probabilities
    
    def probability_of_affordability(
        self,
        purchase_price: float,
        current_balance: float,
        balance_std_dev: float,
        emergency_fund: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculate probability of being able to afford a purchase.
        
        Args:
            purchase_price: Price of item
            current_balance: Current account balance (mean)
            balance_std_dev: Std dev of balance (uncertainty)
            emergency_fund: Emergency fund to preserve
            
        Returns:
            Dictionary with affordability probabilities
        """
        # Available balance
        available_mean = current_balance - emergency_fund
        available_std = balance_std_dev
        
        # Probability of being able to afford
        prob_afford_lump = self.calculate_event_probability(
            event_threshold=purchase_price,
            mean=available_mean,
            std_dev=available_std,
            direction="above",
        )
        
        # Probability if they're aggressive (ignore emergency fund)
        prob_afford_aggressive = self.calculate_event_probability(
            event_threshold=purchase_price,
            mean=current_balance,
            std_dev=balance_std_dev,
            direction="above",
        )
        
        return {
            "probability_can_afford_conservative": prob_afford_lump,
            "probability_can_afford_aggressive": prob_afford_aggressive,
            "probability_can_afford_balanced": (prob_afford_lump + prob_afford_aggressive) / 2,
        }
    
    def confidence_score_from_data_quality(
        self,
        data_points: int,
        data_span_days: int,
        data_freshness_days: int = 0,
    ) -> float:
        """
        Calculate confidence score based on data quality.
        
        Args:
            data_points: Number of data points (transactions, samples)
            data_span_days: How many days the data spans
            data_freshness_days: How old the newest data is
            
        Returns:
            Confidence score 0-1
        """
        confidence = 0.5  # Base confidence
        
        # More data points = higher confidence (logarithmic)
        data_confidence = min(0.30, np.log(max(1, data_points)) / 10)
        
        # Longer spans = higher confidence (more patterns)
        span_confidence = min(0.35, data_span_days / 365)
        
        # Fresh data = higher confidence
        freshness_confidence = min(0.25, 1.0 - (data_freshness_days / 90))
        
        confidence = min(0.95, data_confidence + span_confidence + freshness_confidence)
        
        return np.clip(confidence, 0.1, 0.95)
    
    def _calculate_distribution(self, samples: np.ndarray) -> ProbabilityDistribution:
        """Calculate distribution from sample array."""
        return ProbabilityDistribution(
            mean=float(np.mean(samples)),
            std_dev=float(np.std(samples)),
            min_value=float(np.min(samples)),
            max_value=float(np.max(samples)),
            percentile_5=float(np.percentile(samples, 5)),
            percentile_50=float(np.percentile(samples, 50)),
            percentile_95=float(np.percentile(samples, 95)),
            distribution_type="empirical",
        )
    
    def to_dict(self, dist: ProbabilityDistribution) -> Dict:
        """Convert distribution to dictionary."""
        return {
            "mean": dist.mean,
            "std_dev": dist.std_dev,
            "min_value": dist.min_value,
            "max_value": dist.max_value,
            "percentile_5": dist.percentile_5,
            "percentile_50": dist.percentile_50,
            "percentile_95": dist.percentile_95,
            "distribution_type": dist.distribution_type,
        }
