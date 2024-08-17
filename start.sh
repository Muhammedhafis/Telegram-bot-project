#!/bin/bash
# Install dependencies
pip install -r requirements.txt
# Start Flask application
gunicorn -w 4 -b 0.0.0.0:8080 app:app
