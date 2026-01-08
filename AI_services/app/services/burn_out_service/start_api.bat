@echo off
echo ================================================================================
echo SENTRY AI - BURNOUT DETECTION API
echo ================================================================================
echo.

echo Starting FastAPI server...
echo.
echo Documentation will be available at:
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.

cd /d "%~dp0"
python -m api.main

pause
