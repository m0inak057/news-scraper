#!/bin/bash

# Build script for Vercel deployment
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Create staticfiles_build directory for Vercel
mkdir -p staticfiles_build
cp -r staticfiles/* staticfiles_build/
