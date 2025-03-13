#!/bin/bash

# List of ports to check
PORTS=(5000 8000 8088 8900)

for PORT in "${PORTS[@]}"; do
    if ! lsof -i :$PORT > /dev/null; then
        echo "Starting Flask app on port $PORT..."
        export FLASK_APP=app.py
        export FLASK_ENV=development
        flask run --host=0.0.0.0 --port=$PORT
        exit 0
    fi
done

echo "All specified ports are in use. Please free up a port and try again."
exit 1

