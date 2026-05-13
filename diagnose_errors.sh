#!/bin/bash

# Comprehensive Django Project Error Detection & Fix

echo "=================================="
echo "Django Project Error Detection"
echo "=================================="
echo ""

cd Django-Project/config

# Test 1: Check settings import
echo "1. Testing Django Settings Import..."
python manage.py check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "OK: Django settings OK"
else
    echo "ERROR: Django settings has issues"
fi

# Test 2: Check migrations
echo "2. Testing Migration Plan..."
python manage.py migrate --plan > /tmp/migrations.log 2>&1
if [ $? -eq 0 ]; then
    echo "OK: Migrations OK"
else
    echo "ERROR: Migrations have issues"
    cat /tmp/migrations.log | head -20
fi

# Test 3: Check static files
echo "3. Testing Static Files Collection..."
python manage.py collectstatic --noinput > /tmp/static.log 2>&1
if [ $? -eq 0 ]; then
    echo "OK: Static files OK"
else
    echo "ERROR: Static files have issues"
    cat /tmp/static.log | head -20
fi

# Test 4: Check app imports
echo "4. Testing App Imports..."
export DJANGO_SETTINGS_MODULE=config.settings
python << 'PYTEST' > /tmp/imports.log 2>&1
import sys
import django
django.setup()

problems = []

try:
    from accounts.models import CustomUser
    print("OK: accounts")
except Exception as e:
    problems.append(f"accounts: {e}")

try:
    from students.models import Student
    print("OK: students")
except Exception as e:
    problems.append(f"students: {e}")

try:
    from analytics.models import Prediction
    print("OK: analytics")
except Exception as e:
    problems.append(f"analytics: {e}")

try:
    from messaging.models import Message
    print("OK: messaging")
except Exception as e:
    problems.append(f"messaging: {e}")

try:
    from complaints.models import Complaint
    print("OK: complaints")
except Exception as e:
    problems.append(f"complaints: {e}")

try:
    from documents.models import Document
    print("OK: documents")
except Exception as e:
    problems.append(f"documents: {e}")

try:
    from timetable.models import TimeSlot
    print("OK: timetable")
except Exception as e:
    problems.append(f"timetable: {e}")

if problems:
    print("\nPROBLEMS FOUND:")
    for p in problems:
        print(f"  ERROR: {p}")
    sys.exit(1)
PYTEST

if [ $? -eq 0 ]; then
    echo "OK: All app imports successful"
else
    echo "ERROR: Some app imports failed:"
    cat /tmp/imports.log
fi

# Test 5: Check database configuration
echo "5. Testing Database Configuration..."
python << 'PYTEST'
import os
import django
from django.conf import settings

django.setup()

db_url = os.getenv("DATABASE_URL")
if db_url:
    print(f"Database URL configured: {db_url[:50]}...")
else:
    print("No DATABASE_URL - using SQLite")

print(f"Database Engine: {settings.DATABASES['default']['ENGINE']}")
PYTEST

echo ""
echo "=================================="
echo "Error Detection Complete"
echo "=================================="
