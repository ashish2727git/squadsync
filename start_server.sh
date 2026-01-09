#!/bin/bash

echo "Starting SquadSync server..."
echo ""
echo "Make sure PostgreSQL and Redis are running!"
echo ""

export PYTHONPATH=$(pwd)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
