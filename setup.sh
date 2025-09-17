#!/bin/bash

# NIST Compliance Workflow Setup Script
# This script helps set up and deploy the NIST compliance workflow

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="nist-compliance-workflow"
DOCKER_IMAGE_NAME="nist-workflow"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists curl; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_status "Please install the missing dependencies and run this script again."
        
        print_status "Installation instructions:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Docker Compose: https://docs.docker.com/compose/install/"
        
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your actual API keys and configuration"
            print_status "Required variables:"
            echo "  - OPENAI_API_KEY: Your OpenAI API key"
            echo "  - GITHUB_TOKEN: GitHub personal access token"
            echo "  - GITHUB_REPO: Target repository (org/repo-name)"
            
            read -p "Do you want to edit the .env file now? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env
            fi
        else
            print_error ".env.example file not found!"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
}

# Function to validate environment file
validate_environment() {
    print_status "Validating environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found! Run setup first."
        exit 1
    fi
    
    source .env
    
    local missing_vars=()
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        missing_vars+=("OPENAI_API_KEY")
    fi
    
    if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your_github_personal_access_token_here" ]; then
        missing_vars+=("GITHUB_TOKEN")
    fi
    
    if [ -z "$GITHUB_REPO" ] || [ "$GITHUB_REPO" = "your-org/nist-compliance-reports" ]; then
        missing_vars+=("GITHUB_REPO")
    fi
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing or invalid environment variables: ${missing_vars[*]}"
        print_status "Please update your .env file with valid values"
        exit 1
    fi
    
    print_success "Environment configuration is valid!"
}

# Function to build Docker image
build_docker() {
    print_status "Building Docker image..."
    
    if docker build -t $DOCKER_IMAGE_NAME . ; then
        print_success "Docker image built successfully!"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if [ -f "requirements.txt" ]; then
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            print_status "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        print_status "Installing dependencies..."
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -f "venv/Scripts/activate" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
        pip install -r requirements.txt
        
        if [ -f "test_workflow.py" ]; then
            print_status "Running unit tests..."
            python -m pytest test_workflow.py -v
            print_success "Tests completed!"
        else
            print_warning "Test file not found, skipping tests"
        fi
        
        deactivate
    else
        print_warning "requirements.txt not found, skipping tests"
    fi
}

# Function to start services
start_services() {
    print_status "Starting services with Docker Compose..."
    
    if docker-compose up -d; then
        print_success "Services started successfully!"
        print_status "API available at: http://localhost:8000"
        print_status "API documentation at: http://localhost:8000/docs"
        
        # Wait for service to be ready
        print_status "Waiting for service to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/health >/dev/null 2>&1; then
                print_success "Service is ready!"
                break
            fi
            sleep 2
            if [ $i -eq 30 ]; then
                print_warning "Service may not be ready yet. Check logs with: docker-compose logs"
            fi
        done
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if docker-compose down; then
        print_success "Services stopped successfully!"
    else
        print_error "Failed to stop services"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing service logs..."
    docker-compose logs -f nist-workflow
}

# Function to run workflow once
run_workflow() {
    local topic="${1:-}"
    local max_articles="${2:-10}"
    
    validate_environment
    
    print_status "Running NIST compliance workflow..."
    print_status "Topic: ${topic:-"default NIST search terms"}"
    print_status "Max articles: $max_articles"
    
    if [ -n "$topic" ]; then
        docker run --rm --env-file .env $DOCKER_IMAGE_NAME python main.py --topic "$topic" --max-articles "$max_articles"
    else
        docker run --rm --env-file .env $DOCKER_IMAGE_NAME python main.py --max-articles "$max_articles"
    fi
}

# Function to test API
test_api() {
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Health endpoint working!"
    else
        print_error "Health endpoint failed!"
        return 1
    fi
    
    # Test workflow endpoint with sample data
    print_status "Testing workflow endpoint..."
    response=$(curl -s -X POST "http://localhost:8000/workflow/run" \
        -H "Content-Type: application/json" \
        -d '{"topic": "test", "max_articles": 2}' || echo "failed")
    
    if [[ "$response" == *"failed"* ]] || [[ "$response" == *"error"* ]]; then
        print_warning "Workflow endpoint test failed (this may be expected without valid API keys)"
        echo "Response: $response"
    else
        print_success "Workflow endpoint responding!"
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    print_status "Docker Images:"
    docker images | grep $DOCKER_IMAGE_NAME || echo "No images found"
    
    print_status "API Health Check:"
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        curl -s http://localhost:8000/health | python3 -m json.tool
    else
        echo "API not accessible at http://localhost:8000"
    fi
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop containers
    docker-compose down 2>/dev/null || true
    
    # Remove images
    docker rmi $DOCKER_IMAGE_NAME 2>/dev/null || true
    
    # Remove volumes (optional)
    read -p "Remove Docker volumes? This will delete persistent data (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v 2>/dev/null || true
    fi
    
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    cat << EOF
NIST Compliance Workflow Setup Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    setup                 Set up environment and configuration files
    build                 Build Docker image
    test                  Run unit tests
    start                 Start services with Docker Compose
    stop                  Stop all services
    logs                  Show service logs
    status               Show current service status
    run [TOPIC] [COUNT]  Run workflow once (e.g., run "secure development" 5)
    test-api             Test API endpoints
    cleanup              Clean up Docker resources
    help                 Show this help message

Examples:
    $0 setup                              # Initial setup
    $0 build                              # Build Docker image
    $0 start                              # Start services
    $0 run "cybersecurity framework" 10   # Run workflow with specific topic
    $0 test-api                           # Test API endpoints
    $0 logs                               # View logs
    $0 stop                               # Stop services

Environment Variables (set in .env):
    OPENAI_API_KEY      - Your OpenAI API key (required)
    GITHUB_TOKEN        - GitHub personal access token (required)
    GITHUB_REPO         - Target repository for reports (required)
    GOOGLE_API_KEY      - Google Custom Search API key (optional)
    SEARCH_ENGINE_ID    - Google Custom Search Engine ID (optional)

For more information, see README.md
EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        "setup")
            check_prerequisites
            setup_environment
            print_success "Setup completed! Next steps:"
            echo "  1. Edit .env with your API keys"
            echo "  2. Run: $0 build"
            echo "  3. Run: $0 start"
            ;;
        "build")
            check_prerequisites
            validate_environment
            build_docker
            ;;
        "test")
            run_tests
            ;;
        "start")
            check_prerequisites
            validate_environment
            build_docker
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "run")
            run_workflow "$2" "$3"
            ;;
        "test-api")
            test_api
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Check if running with sudo (not recommended)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root is not recommended for Docker operations"
    print_status "Consider adding your user to the docker group instead"
fi

# Run main function with all arguments
main "$@"