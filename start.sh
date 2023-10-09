#!/bin/sh

echo ""
echo "Starting backend"
echo ""

cd backend/
./backend_env/bin/python -m quart --app main:app run --host 0.0.0.0 --port 8000 --reload
if [ $? -ne 0 ]; then
    echo "Failed to start backend"
    exit $?
fi
