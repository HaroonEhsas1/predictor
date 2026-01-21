#!/usr/bin/env python3
"""
Financial Modeling Prep (FMP) API Integration
Provides institutional-grade fundamental data, analyst estimates, and earnings calendars
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger(__name__)

class FMPDataProvider:
    """Financial Modeling Prep API integration for fundamental data"""
    
    def __init__(self):
        self.api_key = os.getenv('FMP_API_KEY', '')
        self.base_url = 'https://financialmodelingprep.com/api/v3'
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info("✅ FMP API: Connected")
        else:
            logger.warning("⚠️ FMP API: Disabled (no API key)")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.enabled:
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            
            # Add API key to params
            if params is None:
                params = {}
            params['apikey'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"FMP API timeout for {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"FMP API error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected FMP error: {e}")
            return None
    
    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive company profile
        Returns: market cap, sector, industry, CEO, employees, etc.
        """
        data = self._make_request(f"profile/{symbol}")
        
        if data and isinstance(data, list) and len(data) > 0:
            profile = data[0]
            return {
                'symbol': symbol,
                'company_name': profile.get('companyName', ''),
                'sector': profile.get('sector', ''),
                'industry': profile.get('industry', ''),
                'market_cap': profile.get('mktCap', 0),
                'price': profile.get('price', 0),
                'beta': profile.get('beta', 1.0),
                'volume_avg': profile.get('volAvg', 0),
                'description': profile.get('description', ''),
                'ceo': profile.get('ceo', ''),
                'employees': profile.get('fullTimeEmployees', 0),
                'website': profile.get('website', ''),
                'source': 'fmp'
            }
        
        return None
    
    def get_analyst_estimates(self, symbol: str, limit: int = 4) -> Optional[Dict[str, Any]]:
        """
        Get analyst estimates for revenue and EPS
        Returns: consensus estimates, number of analysts, estimated growth
        """
        data = self._make_request(f"analyst-estimates/{symbol}", {'limit': limit})
        
        if data and isinstance(data, list) and len(data) > 0:
            latest = data[0]
            
            return {
                'symbol': symbol,
                'date': latest.get('date', ''),
                'estimated_revenue_avg': latest.get('estimatedRevenueAvg', 0),
                'estimated_revenue_low': latest.get('estimatedRevenueLow', 0),
                'estimated_revenue_high': latest.get('estimatedRevenueHigh', 0),
                'estimated_eps_avg': latest.get('estimatedEpsAvg', 0),
                'estimated_eps_low': latest.get('estimatedEpsLow', 0),
                'estimated_eps_high': latest.get('estimatedEpsHigh', 0),
                'number_analyst_estimated_revenue': latest.get('numberAnalystEstimatedRevenue', 0),
                'number_analysts_estimated_eps': latest.get('numberAnalystsEstimatedEps', 0),
                'source': 'fmp'
            }
        
        return None
    
    def get_price_target(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get analyst price targets
        Returns: target high, target low, target mean, number of analysts
        """
        data = self._make_request(f"price-target/{symbol}")
        
        if data and isinstance(data, list) and len(data) > 0:
            latest = data[0]
            
            return {
                'symbol': symbol,
                'target_high': latest.get('priceTargetHigh', 0),
                'target_low': latest.get('priceTargetLow', 0),
                'target_mean': latest.get('priceTargetAverage', 0),
                'target_median': latest.get('priceTargetMedian', 0),
                'number_of_analysts': latest.get('numberOfAnalysts', 0),
                'published_date': latest.get('publishedDate', ''),
                'source': 'fmp'
            }
        
        return None
    
    def get_earnings_calendar(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get upcoming and past earnings dates
        Returns: earnings dates, EPS estimates, revenue estimates
        """
        data = self._make_request(f"historical/earning_calendar/{symbol}")
        
        if data and isinstance(data, list):
            earnings = []
            for item in data[:4]:  # Last 4 earnings
                earnings.append({
                    'date': item.get('date', ''),
                    'symbol': symbol,
                    'eps': item.get('eps', 0),
                    'eps_estimated': item.get('epsEstimated', 0),
                    'revenue': item.get('revenue', 0),
                    'revenue_estimated': item.get('revenueEstimated', 0),
                    'fiscal_date_ending': item.get('fiscalDateEnding', ''),
                    'source': 'fmp'
                })
            return earnings
        
        return None
    
    def get_key_metrics(self, symbol: str, limit: int = 4) -> Optional[Dict[str, Any]]:
        """
        Get key financial metrics and ratios
        Returns: P/E, P/B, ROE, debt ratios, margins, etc.
        """
        data = self._make_request(f"key-metrics/{symbol}", {'limit': limit})
        
        if data and isinstance(data, list) and len(data) > 0:
            latest = data[0]
            
            return {
                'symbol': symbol,
                'date': latest.get('date', ''),
                'revenue_per_share': latest.get('revenuePerShareTTM', 0),
                'net_income_per_share': latest.get('netIncomePerShareTTM', 0),
                'operating_cash_flow_per_share': latest.get('operatingCashFlowPerShareTTM', 0),
                'free_cash_flow_per_share': latest.get('freeCashFlowPerShareTTM', 0),
                'book_value_per_share': latest.get('bookValuePerShareTTM', 0),
                'tangible_book_value_per_share': latest.get('tangibleBookValuePerShareTTM', 0),
                'pe_ratio': latest.get('peRatioTTM', 0),
                'price_to_sales_ratio': latest.get('priceToSalesRatioTTM', 0),
                'pb_ratio': latest.get('pbRatioTTM', 0),
                'roe': latest.get('roeTTM', 0),
                'roa': latest.get('roaTTM', 0),
                'debt_to_equity': latest.get('debtToEquityTTM', 0),
                'current_ratio': latest.get('currentRatioTTM', 0),
                'enterprise_value_over_ebitda': latest.get('enterpriseValueOverEBITDATTM', 0),
                'source': 'fmp'
            }
        
        return None
    
    def get_institutional_ownership(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get institutional ownership data
        Returns: institutional holders, shares held, ownership percentage
        """
        data = self._make_request(f"institutional-holder/{symbol}")
        
        if data and isinstance(data, list):
            total_shares = 0
            top_holders = []
            
            for holder in data[:10]:  # Top 10 holders
                shares = holder.get('shares', 0)
                total_shares += shares
                
                top_holders.append({
                    'holder': holder.get('holder', ''),
                    'shares': shares,
                    'date_reported': holder.get('dateReported', ''),
                    'change': holder.get('change', 0)
                })
            
            return {
                'symbol': symbol,
                'total_institutional_shares': total_shares,
                'number_of_holders': len(data),
                'top_10_holders': top_holders,
                'source': 'fmp'
            }
        
        return None
    
    def get_insider_trading(self, symbol: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent insider trading activity
        Returns: insider name, transaction type, shares, price, date
        """
        data = self._make_request(f"insider-trading", {'symbol': symbol, 'limit': limit})
        
        if data and isinstance(data, list):
            trades = []
            for trade in data:
                trades.append({
                    'filing_date': trade.get('filingDate', ''),
                    'transaction_date': trade.get('transactionDate', ''),
                    'reporting_name': trade.get('reportingName', ''),
                    'transaction_type': trade.get('transactionType', ''),
                    'securities_owned': trade.get('securitiesOwned', 0),
                    'securities_transacted': trade.get('securitiesTransacted', 0),
                    'price': trade.get('price', 0),
                    'source': 'fmp'
                })
            return trades
        
        return None
    
    def get_financial_score(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get FMP's proprietary stock quality score
        Returns: overall score and component scores
        """
        data = self._make_request(f"score/{symbol}")
        
        if data and isinstance(data, list) and len(data) > 0:
            score = data[0]
            
            return {
                'symbol': symbol,
                'overall_score': score.get('score', 0),
                'altman_z_score': score.get('altmanZScore', 0),
                'piotroski_score': score.get('piotroskiScore', 0),
                'working_capital': score.get('workingCapital', 0),
                'total_assets': score.get('totalAssets', 0),
                'retained_earnings': score.get('retainedEarnings', 0),
                'source': 'fmp'
            }
        
        return None
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get all available fundamental data for a symbol
        Returns: combined data from all FMP endpoints
        """
        if not self.enabled:
            return {'enabled': False, 'source': 'fmp'}
        
        logger.info(f"📊 FMP: Fetching comprehensive analysis for {symbol}")
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'source': 'fmp',
            'enabled': True
        }
        
        # Fetch all data with slight delays to avoid rate limits
        result['profile'] = self.get_company_profile(symbol)
        time.sleep(0.1)
        
        result['analyst_estimates'] = self.get_analyst_estimates(symbol)
        time.sleep(0.1)
        
        result['price_target'] = self.get_price_target(symbol)
        time.sleep(0.1)
        
        result['earnings_calendar'] = self.get_earnings_calendar(symbol)
        time.sleep(0.1)
        
        result['key_metrics'] = self.get_key_metrics(symbol)
        time.sleep(0.1)
        
        result['institutional_ownership'] = self.get_institutional_ownership(symbol)
        time.sleep(0.1)
        
        result['insider_trading'] = self.get_insider_trading(symbol)
        time.sleep(0.1)
        
        result['financial_score'] = self.get_financial_score(symbol)
        
        logger.info(f"✅ FMP: Analysis complete for {symbol}")
        
        return result


# Global instance
fmp_provider = FMPDataProvider()


if __name__ == "__main__":
    # Test the integration
    logging.basicConfig(level=logging.INFO)
    
    symbol = "AMD"
    data = fmp_provider.get_comprehensive_analysis(symbol)
    
    print(f"\n📊 FMP Analysis for {symbol}:")
    print(f"Enabled: {data.get('enabled')}")
    
    if data.get('profile'):
        print(f"\nCompany: {data['profile']['company_name']}")
        print(f"Sector: {data['profile']['sector']}")
        print(f"Market Cap: ${data['profile']['market_cap']:,.0f}")
    
    if data.get('analyst_estimates'):
        est = data['analyst_estimates']
        print(f"\nAnalyst Estimates:")
        print(f"  EPS Estimate: ${est['estimated_eps_avg']:.2f}")
        print(f"  Revenue Estimate: ${est['estimated_revenue_avg']:,.0f}")
        print(f"  Number of Analysts: {est['number_analysts_estimated_eps']}")
    
    if data.get('price_target'):
        pt = data['price_target']
        print(f"\nPrice Target:")
        print(f"  Mean: ${pt['target_mean']:.2f}")
        print(f"  High: ${pt['target_high']:.2f}")
        print(f"  Low: ${pt['target_low']:.2f}")
