#!/bin/sh

echo 'Creating python virtual environment "backend/backend_env"'
python3 -m venv backend/backend_env

echo ""
echo "Restoring backend python packages"
echo ""

cd backend
./backend_env/bin/python -m pip install -r requirements.txt --pre
if [ $? -ne 0 ]; then
    echo "Failed to restore backend python packages"
    exit $?
fi

echo ""
echo "Restoring frontend npm packages"
echo ""

cd ../frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to restore frontend npm packages"
    exit $?
fi

echo ""
echo "Building frontend"
echo ""

npm run build
if [ $? -ne 0 ]; then
    echo "Failed to build frontend"
    exit $?
fi

echo ""
echo "Starting backend"
echo ""

cd ../backend
./backend_env/bin/python -m quart --app main:app run --port 8000 --reload
if [ $? -ne 0 ]; then
    echo "Failed to start backend"
    exit $?
fi
