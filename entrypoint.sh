#!/bin/bash

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h db -p 5432; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL is up - executing command"

# Run migrations
python manage.py migrate

# Create default superuser
python manage.py create_superuser

# Load initial data if it doesn't exist
python manage.py load_data

# Execute the main command
exec "$@"
