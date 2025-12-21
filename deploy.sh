#!/bin/bash

# Deployment script for BinanceBot
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="/opt/binancebot"
BACKUP_DIR="/opt/backups/binancebot"

echo "========================================="
echo "Deploying BinanceBot - Environment: $ENVIRONMENT"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_warning "Running as root is not recommended"
fi

# Create backup directory
print_status "Creating backup..."
mkdir -p $BACKUP_DIR
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"

if [ -d "$PROJECT_DIR" ]; then
    tar -czf $BACKUP_DIR/$BACKUP_NAME \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        -C $(dirname $PROJECT_DIR) $(basename $PROJECT_DIR) 2>/dev/null || true
    print_status "Backup created: $BACKUP_NAME"
fi

# Navigate to project directory
print_status "Navigating to project directory..."
cd $PROJECT_DIR || {
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
}

# Pull latest code
print_status "Pulling latest code from Git..."
git fetch origin
git reset --hard origin/main || git reset --hard origin/master

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Pull latest Docker images
print_status "Pulling latest Docker images..."
$DOCKER_COMPOSE pull

# Stop existing containers
print_status "Stopping existing containers..."
$DOCKER_COMPOSE down

# Build and start containers
print_status "Building and starting containers..."
$DOCKER_COMPOSE up -d --build --force-recreate

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check container status
print_status "Checking container status..."
$DOCKER_COMPOSE ps

# Show logs
print_status "Recent logs:"
$DOCKER_COMPOSE logs --tail=50

# Clean up old Docker images
print_status "Cleaning up old Docker images..."
docker system prune -f

# Keep only last 5 backups
print_status "Cleaning up old backups..."
ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +6 | xargs -r rm

echo ""
echo "========================================="
print_status "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Useful commands:"
echo "  View logs:        $DOCKER_COMPOSE logs -f"
echo "  Stop services:    $DOCKER_COMPOSE down"
echo "  Restart services: $DOCKER_COMPOSE restart"
echo "  View status:      $DOCKER_COMPOSE ps"
echo ""
