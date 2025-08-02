#!/bin/bash

# Quick start script for Credit Approval System
echo "Starting Credit Approval System..."
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

echo "Docker is running"
echo "Building and starting services..."

# Build and start services
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "Services are running!"
    echo ""
    echo "Application URLs:"
    echo "   API Base:        http://localhost:8000/api/"
    echo "   API Docs:        http://localhost:8000/api/docs/"
    echo "   Django Admin:    http://localhost:8000/admin/"
    echo ""
    echo "Service Status:"
    docker-compose ps
    echo ""
    echo "To test the API, run:"
    echo "   python test_api.py"
    echo ""
    echo "To view logs:"
    echo "   docker-compose logs -f web"
    echo "   docker-compose logs -f celery"
    echo ""
    echo "To stop services:"
    echo "   docker-compose down"
else
    echo "Some services failed to start. Check logs:"
    echo "   docker-compose logs"
fi
