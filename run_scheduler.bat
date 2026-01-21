@echo off
REM StockSense Daily Prediction Scheduler
REM Runs automatically at 3:50 PM ET on weekdays (10 min before close)

title StockSense - Daily 3:50 PM Scheduler

echo ================================================================================
echo              STOCKSENSE PREDICTION SYSTEM - SCHEDULER
echo ================================================================================
echo.
echo Schedule: Daily at 3:50 PM Eastern Time (10 min before close)
echo Stocks: AMD, AVGO
echo Press Ctrl+C to stop the scheduler
echo.
echo ================================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run the scheduler
python new_scheduled_predictor.py

REM If scheduler exits, pause so user can see any error messages
echo.
echo ================================================================================
echo Scheduler stopped. Press any key to close...
pause >nul
