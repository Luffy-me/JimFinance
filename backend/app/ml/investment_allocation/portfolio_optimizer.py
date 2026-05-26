"""
Portfolio Optimizer - Modern Portfolio Theory implementation.
Calculates efficient frontier and optimal asset allocations.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


@dataclass
class AssetClass:
    """Asset class definition."""
    name: str
    expected_return: float  # Annual return, e.g., 0.07 = 7%
    volatility: float  # Annual volatility, e.g., 0.15 = 15%
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics."""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    allocation: Dict[str, float]  # {asset_class: weight}
    assumptions: List[str]
    timestamp: datetime
    
    def to_dict(self):
        return {
            "expected_return": self.expected_return,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "allocation": self.allocation,
            "assumptions": self.assumptions,
            "timestamp": self.timestamp.isoformat(),
        }


class PortfolioOptimizer:
    """
    Modern Portfolio Theory optimizer.
    Calculates efficient frontier and optimal allocations.
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer.
        
        Args:
            risk_free_rate: Risk-free rate (Treasury yield), default 2%
        """
        self.logger = logger
        self.risk_free_rate = risk_free_rate
    
    def optimize_portfolio(
        self,
        asset_classes: List[AssetClass],
        correlation_matrix: np.ndarray,
        target_return: Optional[float] = None,
        target_volatility: Optional[float] = None,
    ) -> PortfolioMetrics:
        """
        Optimize portfolio for maximum Sharpe ratio or target return/volatility.
        
        Args:
            asset_classes: List of asset classes with returns and volatilities
            correlation_matrix: Correlation matrix between assets
            target_return: Target return (optional)
            target_volatility: Target volatility (optional)
            
        Returns:
            PortfolioMetrics with optimal allocation
        """
        n_assets = len(asset_classes)
        
        # Extract returns and volatilities
        returns = np.array([ac.expected_return for ac in asset_classes])
        volatilities = np.array([ac.volatility for ac in asset_classes])
        names = [ac.name for ac in asset_classes]
        
        # Build covariance matrix from correlation and volatilities
        cov_matrix = correlation_matrix * np.outer(volatilities, volatilities)
        
        # Objective: Minimize negative Sharpe ratio (maximize Sharpe ratio)
        def objective(weights):
            portfolio_return = np.sum(weights * returns)
            portfolio_volatility = np.sqrt(weights @ cov_matrix @ weights)
            sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_volatility + 1e-8)
            return -sharpe  # Negative for minimization
        
        # Constraints: weights sum to 1
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        
        # Add return constraint if specified
        if target_return is not None:
            constraints = [
                constraints,
                {"type": "eq", "fun": lambda w: np.sum(w * returns) - target_return},
            ]
        
        # Bounds: 0 <= weight <= 1 (no short selling)
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weight
        x0 = np.array([1 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        
        if not result.success:
            self.logger.warning(f"Optimization failed: {result.message}")
        
        # Calculate metrics for optimal portfolio
        opt_weights = result.x
        opt_return = np.sum(opt_weights * returns)
        opt_volatility = np.sqrt(opt_weights @ cov_matrix @ opt_weights)
        opt_sharpe = (opt_return - self.risk_free_rate) / (opt_volatility + 1e-8)
        
        allocation = {name: float(weight) for name, weight in zip(names, opt_weights)}
        
        assumptions = [
            "No short selling allowed",
            f"Risk-free rate: {self.risk_free_rate*100:.1f}%",
            "Historical correlations assumed stable",
            "Past returns predictive of future returns",
        ]
        
        return PortfolioMetrics(
            expected_return=opt_return,
            volatility=opt_volatility,
            sharpe_ratio=opt_sharpe,
            allocation=allocation,
            assumptions=assumptions,
            timestamp=datetime.utcnow(),
        )
    
    def calculate_efficient_frontier(
        self,
        asset_classes: List[AssetClass],
        correlation_matrix: np.ndarray,
        num_portfolios: int = 100,
    ) -> Tuple[List[float], List[float], List[Dict]]:
        """
        Calculate efficient frontier by optimizing for different target returns.
        
        Args:
            asset_classes: List of asset classes
            correlation_matrix: Correlation matrix
            num_portfolios: Number of portfolios to generate
            
        Returns:
            Tuple of (volatilities, returns, allocations)
        """
        returns = np.array([ac.expected_return for ac in asset_classes])
        
        # Generate target returns from min to max
        min_return = np.min(returns)
        max_return = np.max(returns)
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        volatilities = []
        frontier_returns = []
        allocations = []
        
        for target_return in target_returns:
            try:
                metrics = self.optimize_portfolio(
                    asset_classes,
                    correlation_matrix,
                    target_return=target_return,
                )
                volatilities.append(metrics.volatility)
                frontier_returns.append(metrics.expected_return)
                allocations.append(metrics.allocation)
            except Exception as e:
                self.logger.warning(f"Failed to optimize for return {target_return}: {e}")
        
        return volatilities, frontier_returns, allocations
    
    def calculate_min_variance_portfolio(
        self,
        asset_classes: List[AssetClass],
        correlation_matrix: np.ndarray,
    ) -> PortfolioMetrics:
        """
        Calculate minimum variance portfolio (lowest risk).
        
        Args:
            asset_classes: List of asset classes
            correlation_matrix: Correlation matrix
            
        Returns:
            PortfolioMetrics for minimum variance portfolio
        """
        n_assets = len(asset_classes)
        volatilities = np.array([ac.volatility for ac in asset_classes])
        cov_matrix = correlation_matrix * np.outer(volatilities, volatilities)
        names = [ac.name for ac in asset_classes]
        returns = np.array([ac.expected_return for ac in asset_classes])
        
        # Minimize variance (volatility squared)
        def objective(weights):
            return weights @ cov_matrix @ weights
        
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        x0 = np.array([1 / n_assets] * n_assets)
        
        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        
        opt_weights = result.x
        opt_return = np.sum(opt_weights * returns)
        opt_volatility = np.sqrt(opt_weights @ cov_matrix @ opt_weights)
        opt_sharpe = (opt_return - self.risk_free_rate) / (opt_volatility + 1e-8)
        
        allocation = {name: float(weight) for name, weight in zip(names, opt_weights)}
        
        assumptions = [
            "Minimizes portfolio volatility",
            "No short selling",
            "Historical volatilities and correlations assumed stable",
        ]
        
        return PortfolioMetrics(
            expected_return=opt_return,
            volatility=opt_volatility,
            sharpe_ratio=opt_sharpe,
            allocation=allocation,
            assumptions=assumptions,
            timestamp=datetime.utcnow(),
        )
    
    def calculate_sharpe_optimal_portfolio(
        self,
        asset_classes: List[AssetClass],
        correlation_matrix: np.ndarray,
    ) -> PortfolioMetrics:
        """
        Calculate portfolio with maximum Sharpe ratio.
        
        Args:
            asset_classes: List of asset classes
            correlation_matrix: Correlation matrix
            
        Returns:
            PortfolioMetrics for maximum Sharpe ratio portfolio
        """
        return self.optimize_portfolio(asset_classes, correlation_matrix)
    
    def calculate_default_correlation_matrix(
        self,
        num_assets: int,
        default_correlation: float = 0.3,
    ) -> np.ndarray:
        """
        Generate default correlation matrix with specified correlation.
        
        Args:
            num_assets: Number of assets
            default_correlation: Default correlation between assets
            
        Returns:
            Correlation matrix (num_assets x num_assets)
        """
        corr = np.full((num_assets, num_assets), default_correlation)
        np.fill_diagonal(corr, 1.0)  # Diagonal is 1
        return corr
