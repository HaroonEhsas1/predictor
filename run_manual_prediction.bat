@echo off
REM StockSense Manual Prediction Runner
REM Runs predictions immediately for all active stocks

title StockSense - Manual Prediction

echo ================================================================================
echo              STOCKSENSE - MANUAL PREDICTION (ALL STOCKS)
echo ================================================================================
echo.
echo Running predictions for: AMD, AVGO
echo This will take approximately 30-60 seconds...
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

REM Run multi-stock predictor
python multi_stock_predictor.py

echo.
echo ================================================================================
echo Prediction complete. Results saved to: data\multi_stock\
echo Press any key to close...
pause >nul
