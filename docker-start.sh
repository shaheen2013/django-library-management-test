#!/bin/bash

echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "Services are running!"
echo ""
echo "API Documentation: http://localhost:8000/swagger/"
echo "Admin Panel: http://localhost:8000/admin/"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
