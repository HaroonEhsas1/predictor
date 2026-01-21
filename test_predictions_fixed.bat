@echo off
echo ================================================================================
echo FIXED PREDICTION SYSTEM - Test All Stocks
echo ================================================================================
echo.
echo This batch file tests the FIXED prediction system with:
echo   - Lower RSI thresholds (65/35 instead of 70/30)
echo   - Tighter options thresholds (0.8/1.2 instead of 0.7/1.3)
echo   - Reversal detection (contrarian logic)
echo   - Mean reversion detection
echo   - Extreme reading dampener
echo   - Reduced analyst weight
echo.
echo ================================================================================
echo.

echo Choose what to test:
echo.
echo 1. Test ORCL only (fast, 15-30 seconds)
echo 2. Test AMD only (fast, 15-30 seconds)
echo 3. Test AVGO only (fast, 15-30 seconds)
echo 4. Test ALL stocks (AMD, AVGO, ORCL) (slower, 1-2 minutes)
echo 5. Run diagnostic (check for biases)
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running ORCL prediction...
    python test_orcl_predictor.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running AMD prediction...
    python multi_stock_predictor.py --stocks AMD
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Running AVGO prediction...
    python multi_stock_predictor.py --stocks AVGO
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Running ALL stocks prediction...
    python multi_stock_predictor.py --stocks AMD AVGO ORCL
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Running diagnostic...
    python diagnose_prediction_bias.py
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Exiting...
    goto end
)

echo Invalid choice!
pause
goto end

:end
echo.
echo ================================================================================
echo.
echo To see what was fixed, read: BULLISH_BIAS_FIXES.md
echo.
pause
