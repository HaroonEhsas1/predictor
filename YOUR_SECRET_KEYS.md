# Your Active Secret Keys - Transfer to Local Machine

## ✅ Keys You HAVE Configured in Replit

These are the API keys currently active in your Replit system. You MUST transfer these to your local `.env` file:

### 1. Data Source APIs (Active)
```bash
POLYGON_API_KEY=<your_actual_key>        # ✅ CONFIGURED
ALPHA_VANTAGE_API_KEY=<your_actual_key>  # ✅ CONFIGURED
EODHD_API_KEY=<your_actual_key>          # ✅ CONFIGURED
FINNHUB_API_KEY=<your_actual_key>        # ✅ CONFIGURED
```

### 2. SMS Notifications - Twilio (Active)
```bash
TWILIO_ACCOUNT_SID=<your_actual_sid>     # ✅ CONFIGURED
TWILIO_AUTH_TOKEN=<your_actual_token>    # ✅ CONFIGURED
TWILIO_PHONE_NUMBER=<your_phone>         # ✅ CONFIGURED
```

### 3. Reddit Sentiment Analysis (Active)
```bash
REDDIT_CLIENT_ID=<your_client_id>        # ✅ CONFIGURED
REDDIT_CLIENT_SECRET=<your_secret>       # ✅ CONFIGURED
REDDIT_USERNAME=<your_username>          # ✅ CONFIGURED
REDDIT_PASSWORD=<your_password>          # ✅ CONFIGURED
```

### 4. Economic Data (Active)
```bash
FRED_API_KEY=<your_fred_key>             # ✅ CONFIGURED
```

### 5. Database (Active)
```bash
DATABASE_URL=<your_database_url>         # ✅ CONFIGURED
```

---

## 📋 How to Transfer Keys to Local Machine

### Step 1: Export Keys from Replit

In your Replit environment, run:

```bash
# Create a file with your actual keys (DO NOT COMMIT THIS!)
cat > my_keys.txt << 'EOF'
POLYGON_API_KEY=${POLYGON_API_KEY}
ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
EODHD_API_KEY=${EODHD_API_KEY}
FINNHUB_API_KEY=${FINNHUB_API_KEY}
TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
REDDIT_USERNAME=${REDDIT_USERNAME}
REDDIT_PASSWORD=${REDDIT_PASSWORD}
FRED_API_KEY=${FRED_API_KEY}
DATABASE_URL=${DATABASE_URL}
EOF

# Display your keys (copy these to local .env)
env | grep -E "POLYGON_API_KEY|ALPHA_VANTAGE_API_KEY|EODHD_API_KEY|FINNHUB_API_KEY|TWILIO|REDDIT|FRED_API_KEY|DATABASE_URL"
```

### Step 2: On Your Local Machine

1. **Navigate to your project folder**
   ```bash
   cd /path/to/your/project
   ```

2. **Create .env file** (if you used setup script, this already exists)
   ```bash
   cp .env.example .env
   ```

3. **Edit .env and paste your actual keys**
   ```bash
   # Mac/Linux
   nano .env
   
   # Or use Cursor AI editor
   code .env
   ```

4. **Paste all your keys from Replit** into the `.env` file

### Step 3: Verify Keys Loaded

```bash
# On local machine, test if keys load
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

keys = [
    'POLYGON_API_KEY',
    'ALPHA_VANTAGE_API_KEY', 
    'EODHD_API_KEY',
    'FINNHUB_API_KEY',
    'TWILIO_ACCOUNT_SID',
    'FRED_API_KEY',
    'DATABASE_URL'
]

for key in keys:
    value = os.getenv(key)
    status = '✅' if value else '❌'
    print(f'{status} {key}: {\"SET\" if value else \"NOT SET\"}')"
```

---

## 🚨 IMPORTANT Security Notes

1. **NEVER commit .env to Git** - It's already in .gitignore
2. **Keep keys secret** - Don't share in screenshots or logs
3. **Rotate keys if exposed** - Regenerate from provider if accidentally shared
4. **Use different keys** for local vs production (optional but recommended)

---

## 🔄 Database Setup on Local

Your Replit has `DATABASE_URL` configured. For local:

### Option 1: Use Same Database (Remote)
```bash
# Just copy the DATABASE_URL from Replit to local .env
DATABASE_URL=<same_url_from_replit>
```

### Option 2: Set Up Local PostgreSQL
```bash
# Install PostgreSQL locally
# Mac
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql
sudo service postgresql start

# Create local database
createdb stock_predictions_local

# Update .env
DATABASE_URL=postgresql://localhost:5432/stock_predictions_local
```

---

## ✅ Complete .env File Template (With YOUR Keys)

Copy this to your local `.env` file and replace `<your_xxx>` with actual values from Replit:

```bash
# ========== DATA SOURCES ==========
POLYGON_API_KEY=<copy_from_replit>
ALPHA_VANTAGE_API_KEY=<copy_from_replit>
EODHD_API_KEY=<copy_from_replit>
FINNHUB_API_KEY=<copy_from_replit>

# ========== SMS NOTIFICATIONS ==========
TWILIO_ACCOUNT_SID=<copy_from_replit>
TWILIO_AUTH_TOKEN=<copy_from_replit>
TWILIO_PHONE_NUMBER=<copy_from_replit>
SMS_ALERT_PHONE=<copy_from_replit>  # Same as TWILIO_PHONE_NUMBER

# ========== REDDIT SENTIMENT ==========
REDDIT_CLIENT_ID=<copy_from_replit>
REDDIT_CLIENT_SECRET=<copy_from_replit>
REDDIT_USERNAME=<copy_from_replit>
REDDIT_PASSWORD=<copy_from_replit>

# ========== ECONOMIC DATA ==========
FRED_API_KEY=<copy_from_replit>

# ========== DATABASE ==========
DATABASE_URL=<copy_from_replit>
# Or use local: postgresql://localhost:5432/stock_predictions_local

# ========== OPTIONAL (You don't have these) ==========
# QUANDL_API_KEY=
# IEX_CLOUD_API_KEY=
# BENZINGA_API_KEY=
# CBOE_API_KEY=
# TD_AMERITRADE_API_KEY=
```

---

## 📝 Quick Command to Export from Replit

Run this in Replit Shell to see all your keys at once:

```bash
echo "=== YOUR API KEYS TO COPY ==="
echo ""
echo "POLYGON_API_KEY=$POLYGON_API_KEY"
echo "ALPHA_VANTAGE_API_KEY=$ALPHA_VANTAGE_API_KEY"
echo "EODHD_API_KEY=$EODHD_API_KEY"
echo "FINNHUB_API_KEY=$FINNHUB_API_KEY"
echo "TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID"
echo "TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN"
echo "TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER"
echo "REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID"
echo "REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET"
echo "REDDIT_USERNAME=$REDDIT_USERNAME"
echo "REDDIT_PASSWORD=$REDDIT_PASSWORD"
echo "FRED_API_KEY=$FRED_API_KEY"
echo "DATABASE_URL=$DATABASE_URL"
echo ""
echo "=== COPY ALL ABOVE TO LOCAL .env ==="
```

Copy the output and paste directly into your local `.env` file!
