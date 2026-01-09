@echo off
echo Starting SquadSync server...
echo.
echo Make sure PostgreSQL and Redis are running!
echo.

set PYTHONPATH=%CD%
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
