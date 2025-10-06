#!/bin/bash
# Quick helper script to run streaming examples with Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$PROJECT_ROOT"

show_usage() {
    cat << EOF

          Streaming/Chunked Responses - Docker Helper                 


Usage: ./run_docker.sh [COMMAND]

Commands:
  start       Start the streaming API server
  stop        Stop the streaming API server
  restart     Restart the streaming API server
  logs        View server logs
  client      Run client examples
  test        Test the API endpoints
  build       Rebuild the Docker image
  status      Check service status
  shell       Open shell in the server container
  help        Show this help message

Examples:
  ./run_docker.sh start       # Start the server
  ./run_docker.sh test        # Test endpoints
  ./run_docker.sh client      # Run client examples
  ./run_docker.sh logs        # View logs

After starting, visit:
  • http://localhost:8000/docs - Interactive API docs
  • http://localhost:8000/stream/stock-ticker - Stock ticker
  • http://localhost:8000/ai/chat-stream?prompt=Hello - AI streaming

EOF
}

start_server() {
    echo " Starting streaming API server..."
    docker compose up -d streaming-api
    echo ""
    echo " Server started!"
    echo ""
    echo "   API: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs: ./run_docker.sh logs"
    echo "Run tests: ./run_docker.sh test"
}

stop_server() {
    echo "⏹  Stopping streaming API server..."
    docker compose stop streaming-api
    echo " Server stopped!"
}

restart_server() {
    echo " Restarting streaming API server..."
    docker compose restart streaming-api
    echo " Server restarted!"
}

view_logs() {
    echo " Viewing server logs (Ctrl+C to exit)..."
    echo ""
    docker compose logs -f streaming-api
}

run_client() {
    echo "  Running client examples..."
    echo ""
    
    # Make sure server is running
    if ! docker compose ps streaming-api | grep -q "Up"; then
        echo "  Server is not running. Starting it first..."
        start_server
        echo "Waiting for server to be ready..."
        sleep 5
    fi
    
    docker compose exec streaming-api python client_examples.py
}

test_endpoints() {
    echo " Testing API endpoints..."
    echo ""
    
    # Make sure server is running
    if ! docker compose ps streaming-api | grep -q "Up"; then
        echo "  Server is not running. Please start it first with: ./run_docker.sh start"
        exit 1
    fi
    
    echo "1. Testing health endpoint..."
    curl -s http://localhost:8000/health | python -m json.tool
    echo ""
    
    echo "2. Testing root endpoint..."
    curl -s http://localhost:8000/ | python -m json.tool | head -20
    echo "..."
    echo ""
    
    echo "3. Testing AI streaming (5 seconds)..."
    timeout 5 curl -N "http://localhost:8000/ai/chat-stream?prompt=Hello" || true
    echo ""
    echo ""
    
    echo "4. Testing stock ticker (5 seconds)..."
    echo "(Showing real-time stock updates via SSE)"
    timeout 5 curl -N http://localhost:8000/stream/stock-ticker || true
    echo ""
    echo ""
    
    echo " Basic tests complete!"
    echo ""
    echo "For more examples, run: ./run_docker.sh client"
}

build_image() {
    echo " Building Docker image..."
    docker compose build streaming-api
    echo " Build complete!"
}

check_status() {
    echo " Service Status:"
    echo ""
    docker compose ps streaming-api
    echo ""
    
    if docker compose ps streaming-api | grep -q "Up"; then
        echo " Server is running"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
    else
        echo "  Server is not running"
        echo "Start with: ./run_docker.sh start"
    fi
}

open_shell() {
    echo " Opening shell in server container..."
    docker compose exec streaming-api /bin/bash
}

# Main command dispatcher
case "${1:-help}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    logs)
        view_logs
        ;;
    client)
        run_client
        ;;
    test)
        test_endpoints
        ;;
    build)
        build_image
        ;;
    status)
        check_status
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo " Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac

