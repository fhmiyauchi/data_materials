#!/bin/bash
set -e

echo "Starting Superset initialization..."

# Upgrade the metadata database schema first
echo "Running database migrations..."
superset db upgrade

# Create admin user — credentials loaded from environment variables
echo "Creating admin user..."
superset fab create-admin \
              --username "${SUPERSET_ADMIN_USERNAME}" \
              --firstname Admin \
              --lastname User \
              --email "${SUPERSET_ADMIN_EMAIL}" \
              --password "${SUPERSET_ADMIN_PASSWORD}" || true

# Load default roles and permissions
echo "Initializing roles..."
superset init

echo "Superset initialization complete!"
