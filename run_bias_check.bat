@echo off
REM StockSense Bias Verification
REM Verifies the system can predict both UP and DOWN equally

title StockSense - Bias Verification

echo ================================================================================
echo              STOCKSENSE - BIAS VERIFICATION CHECK
echo ================================================================================
echo.
echo This will verify:
echo   - All scoring is symmetric (UP vs DOWN)
echo   - No hidden biases in the prediction logic
echo   - System can predict both directions equally
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

REM Run the bias check
python verify_no_bias.py

echo.
echo ================================================================================
echo Verification complete. Press any key to close...
pause >nul
