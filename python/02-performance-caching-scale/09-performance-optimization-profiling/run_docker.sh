#!/bin/bash
# Helper script for running profiling examples in Docker
# Usage: ./run_docker.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service name in docker-compose
SERVICE="profiling-examples"

# Detect docker compose command (v2 or v1)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}✗${NC} Neither 'docker compose' nor 'docker-compose' found"
    exit 1
fi

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if docker compose is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
}

# Main commands
case "$1" in
    build)
        print_info "Building profiling examples image..."
        cd ../.. && $DOCKER_COMPOSE build $SERVICE
        print_success "Image built successfully"
        ;;
    
    start|up)
        print_info "Starting profiling examples container..."
        cd ../.. && $DOCKER_COMPOSE up -d $SERVICE
        print_success "Container started"
        print_info "Run './run_docker.sh basic' to execute basic profiling examples"
        ;;
    
    stop)
        print_info "Stopping profiling examples container..."
        cd ../.. && $DOCKER_COMPOSE stop $SERVICE
        print_success "Container stopped"
        ;;
    
    restart)
        print_info "Restarting profiling examples container..."
        cd ../.. && $DOCKER_COMPOSE restart $SERVICE
        print_success "Container restarted"
        ;;
    
    down)
        print_info "Removing profiling examples container..."
        cd ../.. && $DOCKER_COMPOSE down $SERVICE
        print_success "Container removed"
        ;;
    
    logs)
        print_info "Showing logs (press Ctrl+C to exit)..."
        cd ../.. && $DOCKER_COMPOSE logs -f $SERVICE
        ;;
    
    status)
        print_info "Checking container status..."
        cd ../.. && $DOCKER_COMPOSE ps $SERVICE
        ;;
    
    shell|bash)
        print_info "Opening shell in container..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE /bin/bash
        ;;
    
    # Run profiling examples
    basic)
        print_info "Running basic profiling examples..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python profiling_example.py
        ;;
    
    advanced)
        print_info "Running advanced profiling examples..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python advanced_profiling.py
        ;;
    
    line)
        print_info "Running line profiling examples..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python line_profiling_example.py
        ;;
    
    all)
        print_info "Running all profiling examples..."
        echo ""
        print_info "=== Basic Profiling Examples ==="
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python profiling_example.py
        echo ""
        print_info "=== Advanced Profiling Examples ==="
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python advanced_profiling.py
        echo ""
        print_info "=== Line Profiling Examples ==="
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python line_profiling_example.py
        print_success "All examples completed!"
        ;;
    
    # Profile a custom script
    profile)
        if [ -z "$2" ]; then
            print_error "Please provide a Python file to profile"
            echo "Usage: ./run_docker.sh profile <script.py>"
            exit 1
        fi
        print_info "Profiling $2 with pyinstrument..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE pyinstrument "$2"
        ;;
    
    # Run cProfile on a script
    cprofile)
        if [ -z "$2" ]; then
            print_error "Please provide a Python file to profile"
            echo "Usage: ./run_docker.sh cprofile <script.py>"
            exit 1
        fi
        print_info "Profiling $2 with cProfile..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python -m cProfile -s cumtime "$2"
        ;;
    
    # View generated HTML profiles
    profiles)
        print_info "Generated profile files:"
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE ls -lh *.html *.prof 2>/dev/null || print_warning "No profile files found"
        print_info "To view HTML profiles, copy them to your local machine:"
        echo "  $DOCKER_COMPOSE cp $SERVICE:/app/profile.html ."
        ;;
    
    # Clean up generated files
    clean)
        print_info "Cleaning up generated profile files..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE sh -c "rm -f *.prof *.lprof *.html" || true
        print_success "Profile files cleaned"
        ;;
    
    # Quick test
    test)
        print_info "Running quick profiling test..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python -c "
from pyinstrument import Profiler
import time

profiler = Profiler()
profiler.start()

# Quick test
total = sum(i**2 for i in range(100000))

profiler.stop()
print(profiler.output_text(unicode=True, color=True))
print('\n✓ Profiling tools are working correctly!')
"
        ;;
    
    # Interactive Python shell with profiling tools
    python)
        print_info "Starting interactive Python shell with profiling tools..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE python
        ;;
    
    # Install additional profiling tools
    install)
        if [ -z "$2" ]; then
            print_error "Please provide a package name"
            echo "Usage: ./run_docker.sh install <package-name>"
            exit 1
        fi
        print_info "Installing $2..."
        cd ../.. && $DOCKER_COMPOSE exec $SERVICE pip install "$2"
        print_success "$2 installed"
        ;;
    
    # Show help
    help|--help|-h|"")
        echo ""
        echo "Performance Profiling Examples - Docker Helper Script"
        echo ""
        echo "Usage: ./run_docker.sh [command]"
        echo ""
        echo "Container Management:"
        echo "  build       Build the Docker image"
        echo "  start       Start the container"
        echo "  stop        Stop the container"
        echo "  restart     Restart the container"
        echo "  down        Remove the container"
        echo "  status      Show container status"
        echo "  logs        Show container logs (follow mode)"
        echo "  shell       Open bash shell in container"
        echo ""
        echo "Run Examples:"
        echo "  basic       Run basic profiling examples (cProfile, pyinstrument, yappi)"
        echo "  advanced    Run advanced profiling examples (API, threading, async)"
        echo "  line        Run line profiling examples"
        echo "  all         Run all examples"
        echo ""
        echo "Profiling Tools:"
        echo "  profile <file>     Profile a Python file with pyinstrument"
        echo "  cprofile <file>    Profile a Python file with cProfile"
        echo "  profiles           List generated profile files"
        echo "  clean              Remove generated profile files"
        echo "  test               Quick test to verify profiling tools work"
        echo ""
        echo "Development:"
        echo "  python             Open interactive Python shell"
        echo "  install <pkg>      Install additional Python package"
        echo ""
        echo "Examples:"
        echo "  ./run_docker.sh start"
        echo "  ./run_docker.sh basic"
        echo "  ./run_docker.sh profile my_script.py"
        echo "  ./run_docker.sh shell"
        echo ""
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run './run_docker.sh help' for usage information"
        exit 1
        ;;
esac

