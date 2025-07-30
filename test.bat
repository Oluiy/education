@echo off
REM EduNerve Test Suite Runner for Windows
REM Usage: test.bat [options]
REM Options: --quick, --structure-only, --api-only, --integration-only

echo 🚀 EduNerve Comprehensive Test Suite
echo ======================================

cd /d "%~dp0"

if not exist "tests\run_tests.py" (
    echo ❌ Test runner not found. Please ensure tests\run_tests.py exists.
    exit /b 1
)

python tests\run_tests.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 Tests completed successfully!
) else (
    echo.
    echo 💥 Some tests failed. Check the reports for details.
    exit /b 1
)
