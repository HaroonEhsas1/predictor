"""
WHEN TO RUN PREMARKET SYSTEM
Shows you exactly when 9:15 AM ET is in YOUR local time
"""

from datetime import datetime, time
import pytz

def show_trading_times():
    """Display US market times in both ET and your local timezone"""
    
    # Get timezones
    et_tz = pytz.timezone('US/Eastern')
    
    # Current times (both timezone-aware)
    now_et = datetime.now(et_tz)
    now_local = datetime.now().astimezone()
    
    print("\n" + "="*80)
    print("US STOCK MARKET SCHEDULE - TIME CONVERTER")
    print("="*80)
    
    print(f"\n🌍 YOUR LOCATION:")
    print(f"   Current Local Time: {now_local.strftime('%I:%M %p')}")
    print(f"   Your Timezone: {now_local.astimezone().tzinfo.tzname(None)}")
    
    print(f"\n🇺🇸 US EASTERN TIME:")
    print(f"   Current ET Time: {now_et.strftime('%I:%M %p ET')}")
    
    # Calculate time difference
    time_diff = (now_local.utcoffset() - now_et.utcoffset()).total_seconds() / 3600
    
    print(f"\n⏰ TIME DIFFERENCE:")
    print(f"   Your time is {time_diff:+.1f} hours vs ET")
    
    # Key trading times
    print(f"\n📊 KEY TRADING TIMES:")
    print(f"   {'ET Time':<20} {'Your Local Time':<20} {'Event'}")
    print(f"   {'-'*20} {'-'*20} {'-'*30}")
    
    # Create a reference date (today) with specific ET times
    ref_date = now_et.date()
    
    key_times = [
        ('04:00 AM', 'Premarket Opens'),
        ('09:15 AM', '⭐ RUN PREMARKET SYSTEM'),
        ('09:30 AM', 'Market Opens (Regular)'),
        ('12:00 PM', 'Midday'),
        ('03:50 PM', 'Run Overnight System'),
        ('04:00 PM', 'Market Closes'),
        ('08:00 PM', 'After Hours Closes'),
    ]
    
    for et_time_str, event in key_times:
        # Parse ET time
        et_time_obj = datetime.strptime(et_time_str, '%I:%M %p').time()
        et_datetime = datetime.combine(ref_date, et_time_obj)
        et_datetime = et_tz.localize(et_datetime)
        
        # Convert to local
        local_datetime = et_datetime.astimezone()
        
        # Format
        et_formatted = et_datetime.strftime('%I:%M %p ET')
        local_formatted = local_datetime.strftime('%I:%M %p')
        
        marker = '⭐' if 'RUN' in event else '  '
        print(f"{marker} {et_formatted:<20} {local_formatted:<20} {event}")
    
    # Special note for premarket
    print(f"\n" + "="*80)
    print("🎯 WHEN TO RUN PREMARKET SYSTEM:")
    print("="*80)
    
    # Calculate 9:15 AM ET in local time
    premarket_et = datetime.combine(ref_date, time(9, 15))
    premarket_et = et_tz.localize(premarket_et)
    premarket_local = premarket_et.astimezone()
    
    print(f"\n⭐ 9:15 AM ET = {premarket_local.strftime('%I:%M %p')} YOUR TIME")
    print(f"\n📱 Set alarm for: {premarket_local.strftime('%I:%M %p')}")
    print(f"   Then run: python premarket_multi_stock.py")
    
    # Also show overnight system time
    overnight_et = datetime.combine(ref_date, time(15, 50))  # 3:50 PM
    overnight_et = et_tz.localize(overnight_et)
    overnight_local = overnight_et.astimezone()
    
    print(f"\n⭐ 3:50 PM ET = {overnight_local.strftime('%I:%M %p')} YOUR TIME")
    print(f"\n📱 Set alarm for: {overnight_local.strftime('%I:%M %p')}")
    print(f"   Then run: python multi_stock_predictor.py")
    
    print(f"\n" + "="*80)
    
    # Quick reference
    print(f"\nQUICK REFERENCE:")
    print(f"   Your timezone is {time_diff:+.1f} hours from ET")
    if time_diff > 0:
        print(f"   You are AHEAD of US Eastern Time")
        print(f"   When it's 9:15 AM in New York, it's {premarket_local.strftime('%I:%M %p')} for you")
    elif time_diff < 0:
        print(f"   You are BEHIND US Eastern Time")
        print(f"   When it's 9:15 AM in New York, it's {premarket_local.strftime('%I:%M %p')} for you")
    else:
        print(f"   You are in the SAME timezone as ET!")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    show_trading_times()
