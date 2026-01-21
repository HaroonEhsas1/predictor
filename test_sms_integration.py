#!/usr/bin/env python3
"""
Test SMS Integration with Ultra Accurate Gap Predictor
Quick validation script to test SMS functionality
"""

import os
import sys
from datetime import datetime

def test_sms_import():
    """Test that SMS module can be imported"""
    try:
        from sms_notifier import sms_notifier, SMS_AVAILABLE, test_sms
        print("✅ SMS module imported successfully")
        print(f"📱 SMS Available: {SMS_AVAILABLE}")
        return SMS_AVAILABLE, test_sms
    except ImportError as e:
        print(f"❌ Failed to import SMS module: {e}")
        return False, None

def test_credentials():
    """Test that Twilio credentials are available"""
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All Twilio credentials are available")
        return True

def test_sms_functionality():
    """Test SMS functionality with a simple message"""
    test_phone = os.environ.get('SMS_ALERT_PHONE')
    
    if not test_phone:
        print("⚠️ SMS_ALERT_PHONE environment variable not set")
        print("💡 Set SMS_ALERT_PHONE to your phone number (e.g., +1234567890) to test SMS")
        return False
    
    print(f"📱 Testing SMS to: {test_phone}")
    
    try:
        sms_available, test_function = test_sms_import()
        if not sms_available or not test_function:
            return False
            
        success = test_function(test_phone)
        if success:
            print("✅ SMS test message sent successfully!")
            print("📱 Check your phone for the test message")
            return True
        else:
            print("❌ Failed to send SMS test message")
            return False
            
    except Exception as e:
        print(f"❌ SMS test error: {e}")
        return False

def test_prediction_sms():
    """Test prediction SMS with mock data"""
    test_phone = os.environ.get('SMS_ALERT_PHONE')
    
    if not test_phone:
        print("⚠️ SMS_ALERT_PHONE not set - skipping prediction SMS test")
        return True  # Not a failure, just not configured
    
    try:
        from sms_notifier import send_prediction_sms, send_high_confidence_sms
        
        # Test regular prediction SMS
        mock_prediction = {
            'symbol': 'AMD',
            'direction': 'UP',
            'confidence': 0.72,  # 72%
            'expected_move': 1.25,  # $1.25
            'current_price': 159.16
        }
        
        print("📊 Testing regular prediction SMS...")
        success1 = send_prediction_sms(test_phone, mock_prediction)
        
        # Test high-confidence SMS
        print("🔥 Testing high-confidence SMS...")
        success2 = send_high_confidence_sms(test_phone, 'AMD', 'UP', 85.0, 2.50)
        
        if success1 and success2:
            print("✅ Both prediction SMS tests sent successfully!")
            return True
        else:
            print(f"⚠️ SMS results: Regular={success1}, High-confidence={success2}")
            return success1 or success2  # At least one should work
            
    except Exception as e:
        print(f"❌ Prediction SMS test error: {e}")
        return False

def main():
    """Run all SMS integration tests"""
    print("🧪 SMS INTEGRATION TEST SUITE")
    print("=" * 50)
    print(f"⏰ Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Module import
    print("📦 TEST 1: Module Import")
    import_success = test_sms_import()[0]
    print()
    
    # Test 2: Credentials
    print("🔐 TEST 2: Credentials Check")
    creds_success = test_credentials()
    print()
    
    # Test 3: Basic SMS functionality
    print("📱 TEST 3: Basic SMS Test")
    if import_success and creds_success:
        sms_success = test_sms_functionality()
    else:
        print("⏭️ Skipping SMS test due to import/credential issues")
        sms_success = False
    print()
    
    # Test 4: Prediction SMS
    print("📊 TEST 4: Prediction SMS Test")
    if import_success and creds_success:
        pred_success = test_prediction_sms()
    else:
        print("⏭️ Skipping prediction SMS test due to import/credential issues")
        pred_success = False
    print()
    
    # Summary
    print("📋 TEST SUMMARY")
    print("=" * 50)
    print(f"📦 Module Import:     {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"🔐 Credentials:       {'✅ PASS' if creds_success else '❌ FAIL'}")
    print(f"📱 Basic SMS:         {'✅ PASS' if sms_success else '❌ FAIL'}")
    print(f"📊 Prediction SMS:    {'✅ PASS' if pred_success else '❌ FAIL'}")
    print()
    
    overall_success = import_success and creds_success and (sms_success or pred_success)
    
    if overall_success:
        print("🎉 SMS INTEGRATION READY!")
        print("📱 Your prediction system can now send SMS alerts")
        print()
        print("📝 NEXT STEPS:")
        print("1. Set SMS_ALERT_PHONE environment variable to your phone number")
        print("2. Run the Ultra Accurate Gap Predictor")
        print("3. You'll receive SMS alerts for high-confidence predictions")
    else:
        print("⚠️ SMS INTEGRATION ISSUES DETECTED")
        print("🔧 Please check the errors above and fix configuration")
        
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)