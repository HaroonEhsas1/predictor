#!/usr/bin/env python3
"""
Scheduler Module
Manages market session detection, timing, and module coordination
"""

import os
import sys
from datetime import datetime, time, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
import pytz
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MARKET_HOURS, SUPPRESSION_RULES

class MarketScheduler:
    """Manages market timing and session state"""
    
    def __init__(self):
        self.et_tz = pytz.timezone('US/Eastern')
        self.utc_tz = pytz.UTC
        self.holiday_calendar = USFederalHolidayCalendar()
        
    def get_current_times(self) -> Dict[str, Any]:
        """Get current time in both ET and UTC"""
        utc_now = datetime.now(self.utc_tz)
        et_now = utc_now.astimezone(self.et_tz)
        
        return {
            'utc': utc_now,
            'et': et_now,
            'utc_iso': utc_now.isoformat(),
            'et_formatted': et_now.strftime('%H:%M:%S %Z'),
            'date': et_now.date()
        }
    
    def is_market_day(self, date=None) -> bool:
        """Check if given date is a trading day"""
        if date is None:
            date = self.get_current_times()['date']
        
        # Check if weekend
        if date.weekday() > 4:  # Saturday=5, Sunday=6
            return False
        
        # Check if holiday
        holidays = self.holiday_calendar.holidays(
            start=date, end=date, return_name=True
        )
        return len(holidays) == 0
    
    def next_trading_day(self, date=None):
        """Get the next trading day from given date"""
        if date is None:
            date = self.get_current_times()['date']
        
        current_date = date
        while True:
            current_date += timedelta(days=1)
            if self.is_market_day(current_date):
                return current_date
    
    def is_evening_before_next_trading_day(self, now=None) -> bool:
        """Check if it's Sunday evening before next trading day (for Monday predictions)"""
        if now is None:
            times = self.get_current_times()
            now = times['et']
        
        current_date = now.date()
        current_time = now.time()
        
        # Check if it's Sunday evening (18:15 - 21:00 ET) and next trading day is Monday
        if current_date.weekday() == 6:  # Sunday
            next_trading = self.next_trading_day(current_date)
            # Only predict on Sunday evening if next trading day is within 2 days (Monday)
            days_to_next_trading = (next_trading - current_date).days
            
            if days_to_next_trading <= 2 and time(18, 15) <= current_time <= time(21, 0):
                return True
        
        return False
    
    def should_collect_weekend(self, now=None) -> bool:
        """Check if we should collect weekend data (news, sentiment, futures)"""
        if now is None:
            times = self.get_current_times()
            now = times['et']
        
        current_date = now.date()
        
        # Collect data on weekends and holidays when market is closed
        if not self.is_market_day(current_date):
            return True
        
        return False
    
    def should_run_sunday_prediction(self, now=None) -> bool:
        """Check if we should run Sunday prediction for Monday gaps"""
        if not self.is_evening_before_next_trading_day(now):
            return False
        
        # Check idempotence - only run once per target date
        if now is None:
            times = self.get_current_times()
            now = times['et']
        
        current_date = now.date()
        target_date = self.next_trading_day(current_date)
        
        # This would need to check if prediction already exists for target_date
        # For now, return True (idempotence check will be in main predictor)
        return True
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get comprehensive market state information"""
        times = self.get_current_times()
        et_time = times['et'].time()
        date = times['date']
        
        is_trading_day = self.is_market_day(date)
        
        # Market session states
        market_open = (
            is_trading_day and 
            MARKET_HOURS['open'] <= et_time <= MARKET_HOURS['close']
        )
        
        pre_market = (
            is_trading_day and 
            time(4, 0) <= et_time < MARKET_HOURS['open']
        )
        
        after_hours = (
            is_trading_day and 
            MARKET_HOURS['close'] < et_time <= time(20, 0)
        )
        
        # Calculate minutes to close/open
        minutes_to_close = None
        minutes_to_open = None
        
        if market_open:
            close_datetime = datetime.combine(date, MARKET_HOURS['close'])
            current_datetime = datetime.combine(date, et_time)
            minutes_to_close = int((close_datetime - current_datetime).total_seconds() / 60)
        
        if pre_market:
            open_datetime = datetime.combine(date, MARKET_HOURS['open'])
            current_datetime = datetime.combine(date, et_time)
            minutes_to_open = int((open_datetime - current_datetime).total_seconds() / 60)
        
        # Determine session phase
        if not is_trading_day:
            session_phase = 'WEEKEND_HOLIDAY'
        elif market_open:
            if minutes_to_close and minutes_to_close <= MARKET_HOURS['pre_close_window']:
                session_phase = 'APPROACHING_CLOSE'
            else:
                session_phase = 'MARKET_OPEN'
        elif pre_market:
            if minutes_to_open and minutes_to_open <= MARKET_HOURS['pre_open_window']:
                session_phase = 'PRE_OPEN'
            else:
                session_phase = 'PRE_MARKET'
        elif after_hours:
            session_phase = 'AFTER_HOURS'
        else:
            session_phase = 'MARKET_CLOSED'
        
        return {
            'times': times,
            'is_trading_day': is_trading_day,
            'market_open': market_open,
            'pre_market': pre_market,
            'after_hours': after_hours,
            'session_phase': session_phase,
            'minutes_to_close': minutes_to_close,
            'minutes_to_open': minutes_to_open,
            'should_run_intraday': market_open and is_trading_day,
            'should_show_approaching_close': (
                session_phase == 'APPROACHING_CLOSE' and 
                minutes_to_close is not None and 
                minutes_to_close <= MARKET_HOURS['pre_close_window']
            )
        }
    
    def should_suppress_section(self, section_type: str) -> bool:
        """Determine if a section should be suppressed based on market state"""
        market_state = self.get_market_state()
        
        suppressions = {
            'intraday': (
                not market_state['should_run_intraday'] and 
                SUPPRESSION_RULES['suppress_intraday_when_closed']
            ),
            'approaching_close': (
                not market_state['should_show_approaching_close'] and
                SUPPRESSION_RULES['suppress_approaching_close_when_invalid']
            ),
            'trade_signals': (
                not market_state['market_open'] and
                SUPPRESSION_RULES['suppress_trade_signals_on_fallback']
            ),
            'position_text': SUPPRESSION_RULES['suppress_position_text_when_hold']
        }
        
        return suppressions.get(section_type, False)
    
    def get_data_fetch_strategy(self) -> Dict[str, Any]:
        """Determine optimal data fetching strategy based on market state"""
        market_state = self.get_market_state()
        
        # NEW: Weekend data collection strategy
        if not market_state['is_trading_day']:
            should_collect = self.should_collect_weekend()
            should_predict = self.should_run_sunday_prediction()
            
            return {
                'fetch_intraday': False,
                'fetch_daily_only': True,
                'cache_preference': 'prefer_cache',
                'reason': 'Weekend/Holiday - collecting news/sentiment/futures data' if should_collect else 'Weekend/Holiday - no intraday trading',
                'extended_hours': False,
                'weekend_collectors': should_collect,
                'sunday_prediction': should_predict,
                'mode': 'weekend_active' if should_collect else 'weekend_idle'
            }
        
        if market_state['market_open']:
            return {
                'fetch_intraday': True,
                'fetch_daily_only': False,
                'cache_preference': 'prefer_fresh',
                'reason': 'Market open - need real-time data',
                'extended_hours': False
            }
        
        # NEW: Handle pre-market and after-hours sessions
        if market_state['pre_market'] or market_state['after_hours']:
            return {
                'fetch_intraday': True,  # Enable intraday for extended hours
                'fetch_daily_only': False,
                'cache_preference': 'prefer_fresh',
                'reason': f"Extended hours ({market_state['session_phase']}) - need pre/after market data",
                'extended_hours': True,
                'session_phase': market_state['session_phase']
            }
        
        return {
            'fetch_intraday': False,
            'fetch_daily_only': True,
            'cache_preference': 'allow_cache',
            'reason': 'Market closed - daily data sufficient',
            'extended_hours': False
        }

# Global scheduler instance
scheduler = MarketScheduler()