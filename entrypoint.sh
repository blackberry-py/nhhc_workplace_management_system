#!/bin/bash
# Activate Virtual VENV & Poetry Install
source .venv/bin/activate
pip install poetry
if poetry install; then
# Database Configuration
        echo "✅ Virtual Enviornment and Dependencies installed...Moving on to Database Configuration..."
        if python ./src/app/manage.py migrate; then
else 
        echo "❌ Unable to Install Dependencies..."
fi
# Create Superuser 
                if   python ./src/app/manage.py createsuperuser --noinput; then
                        echo "SUCCESSFULLY CONFIGURED SERVER! 🎊"
                        echo "🚀 Starting Application on port 8080..."
                        gunicorn --workers=2 src.app.nhhc.wsgi
                else
                        echo "❌ ERROR: Configure Enviornment"
                        exit 1;
                        fi 
        else
                echo "❌ ERROR: Unable to Intialized Database"
                exit 1;
        fi