# RSI-EMA Strategy
# Converted from Pine Script v6
# Fixed parameters: RSI14, EMA9, WMA45

import numpy as np
import talib.abstract as ta
from pandas import DataFrame
from binancebot.strategy import IStrategy, IntParameter, DecimalParameter
from functools import reduce


class RSI_EMA(IStrategy):
    """
    RSI-EMA Strategy based on RSI14, EMA9, and WMA45
    Buy: RSI crosses above EMA during downtrend expansion
    Sell: RSI crosses below EMA during uptrend expansion
    """

    INTERFACE_VERSION = 3
    can_short = False  # Spot trading - only LONG positions

    # ========== HYPEROPT PARAMETERS ==========
    
    # A. LONG ENTRY (7 params)
    buy_rsi_oversold = IntParameter(20, 45, default=20, space='buy', optimize=True)
    distance_threshold = DecimalParameter(3, 25, default=13.3, decimals=1, space='buy', optimize=True)
    rsi_slope_min = DecimalParameter(0.2, 1.5, default=0.39, decimals=2, space='buy', optimize=True)
    ema_slope_min = DecimalParameter(0.05, 0.5, default=0.307, decimals=3, space='buy', optimize=True)
    buy_volume_factor = DecimalParameter(0.8, 2.0, default=1.95, decimals=2, space='buy', optimize=True)
    atr_mult = DecimalParameter(1.0, 1.8, default=1.19, decimals=2, space='buy', optimize=True)
    rsi_slope_length = IntParameter(2, 6, default=5, space='buy', optimize=True)
    
    # B. LONG EXIT (5 params)
    sell_rsi_overbought = IntParameter(55, 80, default=72, space='sell', optimize=True)
    sell_rsi_slope_min = DecimalParameter(-1.5, -0.2, default=-0.5, decimals=2, space='sell', optimize=True)
    sell_ema_slope_max = DecimalParameter(-0.5, -0.05, default=-0.252, decimals=3, space='sell', optimize=True)
    sell_volume_factor = DecimalParameter(0.8, 2.0, default=1.24, decimals=2, space='sell', optimize=True)
    sell_atr_mult = DecimalParameter(0.8, 2.0, default=1.18, decimals=2, space='sell', optimize=True)
    
    # C. SHORT ENTRY (4 params)
    short_rsi_threshold = IntParameter(50, 75, default=70, space='buy', optimize=True)
    short_volume_factor = DecimalParameter(0.8, 2.0, default=1.67, decimals=2, space='buy', optimize=True)
    short_rsi_slope_max = DecimalParameter(-1.5, -0.2, default=-1.26, decimals=2, space='buy', optimize=True)
    short_ema_slope_max = DecimalParameter(-0.5, -0.05, default=-0.441, decimals=3, space='buy', optimize=True)
    
    # D. RISK MANAGEMENT (2 params - stoploss optimized via --spaces stoploss)
    trailing_stop_positive = DecimalParameter(0.01, 0.15, default=0.05, decimals=3, space='stoploss', optimize=True)
    trailing_stop_positive_offset = DecimalParameter(0.03, 0.20, default=0.08, decimals=3, space='stoploss', optimize=True)
    
    # E. ADVANCED FILTERS (5 params)
    rsi_divergence_strength = DecimalParameter(0.1, 1.0, default=0.96, decimals=2, space='buy', optimize=True)
    rsi_divergence_window = IntParameter(5, 20, default=5, space='buy', optimize=True)
    volume_delta_min = DecimalParameter(1.0, 3.0, default=2.4, decimals=2, space='buy', optimize=True)
    ema_compression_level = DecimalParameter(0.1, 1.0, default=0.76, decimals=2, space='buy', optimize=True)
    
    # F. POSITION SIZING (2 params)
    kelly_multiplier = DecimalParameter(0.1, 1.0, default=0.1, decimals=2, space='buy', optimize=True)
    risk_per_trade = DecimalParameter(0.03, 0.07, default=0.032, decimals=3, space='buy', optimize=True)  # 3.2% risk per trade
    
    # Enable/disable advanced filters
    use_volume_delta = True
    use_rsi_divergence = True
    use_ema_compression = True
    use_dynamic_stake = True  # Enable dynamic position sizing

    # ROI table - Thực tế hơn
    minimal_roi = {
        "0": 0.20,     # 20% profit ngay lập tức
        "720": 0.15,   # 15% sau 3 ngày (720 phút / 60 / 24 = 0.5 ngày với 4h candle)
        "1440": 0.10,  # 10% sau 6 ngày
        "2880": 0.05   # 5% sau 12 ngày
    }

    # Stoploss - Cố định -12%
    stoploss = -0.12  # -12% hard stop

    # Trailing stop - Kích hoạt sớm hơn
    trailing_stop = True
    trailing_stop_positive = 0.10         # Trailing distance 10%
    trailing_stop_positive_offset = 0.15  # Kích hoạt tại 15% profit
    trailing_only_offset_is_reached = True
    use_custom_stoploss = False  # Dùng trailing stop standard

    # Timeframe
    timeframe = '4h'
    process_only_new_candles = True

    # Fixed parameters (from Pine Script) - removed distance_threshold (now hyperopt param)
    rsi_length = 14
    ema_length = 9
    wma_length = 45
    falling_length = 3
    expansion_length = 5

    startup_candle_count = 60

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate all indicators needed for the strategy
        """
        # Calculate RSI14, EMA9 of RSI, WMA45 of RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_length)
        dataframe['ema_rsi'] = ta.EMA(dataframe['rsi'], timeperiod=self.ema_length)
        dataframe['wma_rsi'] = ta.WMA(dataframe['rsi'], timeperiod=self.wma_length)
        
        # ATR for volatility filter
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        dataframe['atr_percent'] = (dataframe['atr'] / dataframe['close']) * 100
        
        # Volume indicators
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        
        # Volume Delta (ATR-weighted)
        if self.use_volume_delta:
            dataframe['atr_volume'] = dataframe['volume'] * dataframe['atr_percent']
            dataframe['atr_volume_mean'] = dataframe['atr_volume'].rolling(window=20).mean()
            dataframe['volume_delta'] = dataframe['atr_volume'] / dataframe['atr_volume_mean']
        
        # RSI Slope for different lengths
        for length in range(2, 7):
            dataframe[f'rsi_slope_{length}'] = dataframe['rsi'].diff(length)
        
        # EMA Slope (percentage)
        dataframe['ema_slope'] = ((dataframe['ema_rsi'] - dataframe['ema_rsi'].shift(1)) / dataframe['ema_rsi'].shift(1)) * 100
        
        # RSI Divergence detection
        if self.use_rsi_divergence:
            dataframe['price_low'] = dataframe['low'].rolling(window=20).min()
            dataframe['rsi_low'] = dataframe['rsi'].rolling(window=20).min()
            
            # Bullish divergence: price making lower lows, RSI making higher lows
            dataframe['price_lower_low'] = dataframe['low'] < dataframe['price_low'].shift(1)
            dataframe['rsi_higher_low'] = dataframe['rsi'] > dataframe['rsi_low'].shift(1)
            dataframe['bullish_divergence'] = dataframe['price_lower_low'] & dataframe['rsi_higher_low']
        
        # EMA Compression
        if self.use_ema_compression:
            dataframe['ema_distance'] = abs(dataframe['ema_rsi'] - dataframe['wma_rsi'])
            dataframe['ema_distance_mean'] = dataframe['ema_distance'].rolling(window=20).mean()
            dataframe['ema_compression'] = dataframe['ema_distance'] / dataframe['ema_distance_mean']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Buy signal: RSI crosses above EMA9 after downtrend expansion
        """
        # Detect downtrend (RSI < EMA9 < WMA45)
        dataframe['downtrend'] = (
            (dataframe['rsi'] < dataframe['ema_rsi']) & 
            (dataframe['ema_rsi'] < dataframe['wma_rsi'])
        )
        
        # Previous candle was in downtrend
        dataframe['was_downtrend'] = (
            (dataframe['rsi'].shift(1) < dataframe['ema_rsi'].shift(1)) &
            (dataframe['ema_rsi'].shift(1) < dataframe['wma_rsi'].shift(1))
        )
        
        # Falling indicators (3 consecutive candles falling)
        dataframe['falling_rsi'] = (
            (dataframe['rsi'] < dataframe['rsi'].shift(1)) &
            (dataframe['rsi'].shift(1) < dataframe['rsi'].shift(2)) &
            (dataframe['rsi'].shift(2) < dataframe['rsi'].shift(3))
        )
        
        dataframe['falling_ema'] = (
            (dataframe['ema_rsi'] < dataframe['ema_rsi'].shift(1)) &
            (dataframe['ema_rsi'].shift(1) < dataframe['ema_rsi'].shift(2)) &
            (dataframe['ema_rsi'].shift(2) < dataframe['ema_rsi'].shift(3))
        )
        
        dataframe['falling_wma'] = (
            (dataframe['wma_rsi'] < dataframe['wma_rsi'].shift(1)) &
            (dataframe['wma_rsi'].shift(1) < dataframe['wma_rsi'].shift(2)) &
            (dataframe['wma_rsi'].shift(2) < dataframe['wma_rsi'].shift(3))
        )
        
        # Expansion down (spread WMA-RSI is increasing)
        dataframe['spread_down'] = dataframe['wma_rsi'] - dataframe['rsi']
        dataframe['expansion_down'] = (
            dataframe['spread_down'].rolling(window=self.expansion_length).max() >
            dataframe['spread_down'].rolling(window=self.expansion_length).max().shift(1)
        )
        
        # Downtrend expanding condition
        dataframe['is_downtrend_expanding'] = (
            dataframe['downtrend'] &
            dataframe['falling_rsi'] &
            dataframe['falling_ema'] &
            dataframe['falling_wma'] &
            dataframe['expansion_down']
        )
        
        # Store previous downtrend expanding state (rolling max over 10 candles)
        dataframe['prev_downtrend_expanding'] = dataframe['is_downtrend_expanding'].rolling(window=10).max()
        
        # Distance calculations (used by original Pine Script logic)
        dataframe['distance'] = abs(dataframe['wma_rsi'] - dataframe['ema_rsi'])
        
        # EMA curling in (distance is decreasing)
        dataframe['ema_curling_in'] = dataframe['distance'] < dataframe['distance'].shift(1)
        
        # Build LONG ENTRY conditions
        conditions = []
        
        # Core Pine Script conditions (simplified for better signal generation)
        conditions.append((dataframe['rsi'] > dataframe['ema_rsi']) & (dataframe['rsi'].shift(1) <= dataframe['ema_rsi'].shift(1)))
        conditions.append(dataframe['volume'] > 0)
        
        # Hyperopt parameters (relaxed)
        # Check if RSI was oversold recently (within last 5 candles) instead of current candle
        was_oversold = (dataframe['rsi'].rolling(window=5).min() <= self.buy_rsi_oversold.value)
        conditions.append(was_oversold)
        conditions.append(dataframe['distance'] <= self.distance_threshold.value)
        
        # Optional: RSI slope for momentum confirmation
        rsi_slope_ok = dataframe[f'rsi_slope_{self.rsi_slope_length.value}'] >= self.rsi_slope_min.value
        # Optional: EMA slope
        ema_slope_ok = dataframe['ema_slope'] >= self.ema_slope_min.value
        # Optional: Volume filter
        volume_ok = dataframe['volume'] >= dataframe['volume_mean'] * self.buy_volume_factor.value
        
        # Combine with OR for at least one confirmation
        conditions.append(rsi_slope_ok | ema_slope_ok | volume_ok)
        
        # Combine all conditions
        dataframe.loc[reduce(lambda x, y: x & y, conditions), 'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sell signal: RSI crosses below EMA9 after uptrend expansion
        """
        # Detect uptrend (RSI > EMA9 > WMA45)
        dataframe['uptrend'] = (
            (dataframe['rsi'] > dataframe['ema_rsi']) & 
            (dataframe['ema_rsi'] > dataframe['wma_rsi'])
        )
        
        # Previous candle was in uptrend
        dataframe['was_uptrend'] = (
            (dataframe['rsi'].shift(1) > dataframe['ema_rsi'].shift(1)) &
            (dataframe['ema_rsi'].shift(1) > dataframe['wma_rsi'].shift(1))
        )
        
        # Rising indicators (3 consecutive candles rising)
        dataframe['rising_rsi'] = (
            (dataframe['rsi'] > dataframe['rsi'].shift(1)) &
            (dataframe['rsi'].shift(1) > dataframe['rsi'].shift(2)) &
            (dataframe['rsi'].shift(2) > dataframe['rsi'].shift(3))
        )
        
        dataframe['rising_ema'] = (
            (dataframe['ema_rsi'] > dataframe['ema_rsi'].shift(1)) &
            (dataframe['ema_rsi'].shift(1) > dataframe['ema_rsi'].shift(2)) &
            (dataframe['ema_rsi'].shift(2) > dataframe['ema_rsi'].shift(3))
        )
        
        dataframe['rising_wma'] = (
            (dataframe['wma_rsi'] > dataframe['wma_rsi'].shift(1)) &
            (dataframe['wma_rsi'].shift(1) > dataframe['wma_rsi'].shift(2)) &
            (dataframe['wma_rsi'].shift(2) > dataframe['wma_rsi'].shift(3))
        )
        
        # Expansion up (spread RSI-WMA is increasing)
        dataframe['spread_up'] = dataframe['rsi'] - dataframe['wma_rsi']
        dataframe['expansion_up'] = (
            dataframe['spread_up'].rolling(window=self.expansion_length).max() >
            dataframe['spread_up'].rolling(window=self.expansion_length).max().shift(1)
        )
        
        # Uptrend expanding condition
        dataframe['is_uptrend_expanding'] = (
            dataframe['uptrend'] &
            dataframe['rising_rsi'] &
            dataframe['rising_ema'] &
            dataframe['rising_wma'] &
            dataframe['expansion_up']
        )
        
        # Store previous uptrend expanding state
        dataframe['prev_uptrend_expanding'] = dataframe['is_uptrend_expanding'].rolling(window=10).max()
        
        # Distance for exit
        dataframe['distance_exit'] = abs(dataframe['wma_rsi'] - dataframe['ema_rsi'])
        dataframe['ema_curling_in_exit'] = dataframe['distance_exit'] < dataframe['distance_exit'].shift(1)
        
        # Build LONG EXIT conditions
        conditions = []
        
        # Core Pine Script conditions (simplified)
        conditions.append((dataframe['rsi'] < dataframe['ema_rsi']) & (dataframe['rsi'].shift(1) >= dataframe['ema_rsi'].shift(1)))
        conditions.append(dataframe['volume'] > 0)
        
        # Hyperopt parameters
        conditions.append(dataframe['rsi'] >= self.sell_rsi_overbought.value)
        conditions.append(dataframe['distance_exit'] <= self.distance_threshold.value)
        
        # Optional: RSI slope for momentum confirmation
        rsi_slope_ok = dataframe[f'rsi_slope_{self.rsi_slope_length.value}'] <= self.sell_rsi_slope_min.value
        # Optional: EMA slope
        ema_slope_ok = dataframe['ema_slope'] <= self.sell_ema_slope_max.value
        # Optional: Volume filter
        volume_ok = dataframe['volume'] >= dataframe['volume_mean'] * self.sell_volume_factor.value
        
        # Combine with OR for at least one confirmation
        conditions.append(rsi_slope_ok | ema_slope_ok | volume_ok)
        
        # Combine all conditions
        dataframe.loc[reduce(lambda x, y: x & y, conditions), 'exit_long'] = 1

        return dataframe

    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                           proposed_stake: float, min_stake: float, max_stake: float,
                           leverage: float, entry_tag, side: str, **kwargs) -> float:
        """
        Dynamic position sizing based on:
        1. Kelly Criterion (win rate & profit factor)
        2. Risk-based sizing (% of account per trade)
        3. ATR-based volatility adjustment
        """
        if not self.use_dynamic_stake:
            return proposed_stake
        
        # Get account balance
        try:
            total_balance = self.wallets.get_total_stake_amount()
        except:
            return proposed_stake
        
        # Method 1: Kelly Criterion
        # Based on backtest: 72.5% win, profit factor 2.01
        # Kelly = (Win% * ProfitFactor - 1) / (ProfitFactor - 1)
        win_rate = 0.725  # From backtest
        profit_factor = 2.01
        kelly_fraction = ((win_rate * profit_factor) - 1) / (profit_factor - 1)
        kelly_stake = total_balance * kelly_fraction * self.kelly_multiplier.value
        
        # Method 2: Fixed Risk % per trade
        # Risk% / Stoploss% = Position size
        stop_loss_percent = abs(self.stoploss)
        risk_stake = (total_balance * self.risk_per_trade.value) / stop_loss_percent
        
        # Use average of both methods
        calculated_stake = (kelly_stake + risk_stake) / 2
        
        # Ensure within min/max bounds
        calculated_stake = max(min_stake, min(calculated_stake, max_stake))
        
        # Ensure we don't exceed total balance
        calculated_stake = min(calculated_stake, total_balance * 0.33)  # Max 33% per trade
        
        return calculated_stake

