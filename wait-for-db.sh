#!/bin/bash
# Wait for database to be ready

until pg_isready -h db -p 5432 -U edunerve; do
  echo "Waiting for database..."
  sleep 2
done

echo "Database is ready!"
