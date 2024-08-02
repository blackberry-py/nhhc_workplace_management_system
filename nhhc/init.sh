#!/bin/bash

    if python ./src/app/manage.py collectstatic --no-input; then
        if python ./src/app/manage.py migrate && python ./src/app/manage.py createsuperuser --noinput; then
            echo "SUCCESSFULLY CONFIGURED SERVER! 🎊"
        else
            echo "ERROR: Unable to Intialized Database"
        fi
    else
        echo "ERROR: Unable to Collect Static"
    fi
    echo "ERROR: Unable to Install App Requirements"
