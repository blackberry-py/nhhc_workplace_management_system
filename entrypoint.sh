#!/bin/bash
# Activate Virtual VENV & Poetry Install
PYTHON=${VENV_ROOT}/bin/activate/python
VENV=${VENV_ROOT}/bin/activate
source $VENV

if make install; then
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

          bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"
