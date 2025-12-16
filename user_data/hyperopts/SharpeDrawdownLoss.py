# Custom Loss Function: Sharpe + Drawdown + Win Rate
# Balanced multi-objective optimization for crypto trading

from datetime import datetime
from pandas import DataFrame
from binancebot.optimize.hyperopt import IHyperOptLoss


class SharpeDrawdownLoss(IHyperOptLoss):
    """
    Custom loss function combining:
    - Sharpe Ratio (40% weight) - Risk-adjusted returns
    - Max Drawdown (30% weight) - Capital preservation
    - Win Rate (20% weight) - Strategy consistency
    - Trade Count (10% weight) - Avoid overtrading/undertrading
    """
    
    @staticmethod
    def hyperopt_loss_function(
        results: DataFrame,
        trade_count: int,
        min_date: datetime,
        max_date: datetime,
        config: dict,
        *args,
        **kwargs
    ) -> float:
        """
        Calculate custom multi-objective loss
        Lower is better (minimize)
        """
        
        # Avoid division by zero
        if trade_count == 0:
            return 10000  # Worst possible score
        
        # 1. Sharpe Ratio calculation
        total_profit = results['profit_abs'].sum()
        profit_mean = results['profit_abs'].mean()
        profit_std = results['profit_abs'].std()
        
        if profit_std == 0 or profit_std is None:
            sharpe_ratio = 0
        else:
            sharpe_ratio = profit_mean / profit_std
        
        # 2. Max Drawdown (from cumulative profit)
        cumulative_profit = results['profit_abs'].cumsum()
        running_max = cumulative_profit.cummax()
        drawdown = running_max - cumulative_profit
        max_drawdown = drawdown.max()
        
        # Normalize drawdown (worse when larger)
        if max_drawdown == 0:
            drawdown_factor = 0
        else:
            drawdown_factor = max_drawdown / 100  # Normalize to percentage-like scale
        
        # 3. Win Rate
        winning_trades = len(results[results['profit_abs'] > 0])
        win_rate = winning_trades / trade_count
        
        # Optimal win rate is 55-65% (not too high = overfitting)
        win_rate_penalty = abs(win_rate - 0.60) * 100
        
        # 4. Trade Count optimization
        # Sweet spot: 50-200 trades (avoid overtrading and undertrading)
        if trade_count < 30:
            trade_penalty = (30 - trade_count) * 2  # Heavy penalty for too few trades
        elif trade_count > 300:
            trade_penalty = (trade_count - 300) * 0.5  # Light penalty for overtrading
        else:
            trade_penalty = 0
        
        # 5. Average trade duration (optional)
        avg_duration_minutes = results['trade_duration'].mean()
        avg_duration_days = avg_duration_minutes / 1440
        
        # Prefer trades that last 3-10 days (not too short/long)
        if avg_duration_days < 1:
            duration_penalty = (1 - avg_duration_days) * 5
        elif avg_duration_days > 15:
            duration_penalty = (avg_duration_days - 15) * 2
        else:
            duration_penalty = 0
        
        # Combined objective with weights
        objective = (
            -sharpe_ratio * 0.40 +           # 40% - Maximize Sharpe (negative = minimize)
            drawdown_factor * 0.30 +         # 30% - Minimize drawdown
            win_rate_penalty * 0.20 +        # 20% - Optimize win rate around 60%
            trade_penalty * 0.05 +           # 5% - Avoid extreme trade counts
            duration_penalty * 0.05          # 5% - Optimal trade duration
        )
        
        # Additional penalties for edge cases
        
        # Penalty for negative total profit (very bad!)
        if total_profit < 0:
            objective += abs(total_profit) * 2
        
        # Penalty for very high drawdown relative to profit
        if total_profit > 0 and max_drawdown > 0:
            dd_to_profit_ratio = max_drawdown / total_profit
            if dd_to_profit_ratio > 0.5:  # Drawdown > 50% of profit
                objective += dd_to_profit_ratio * 50
        
        return objective
