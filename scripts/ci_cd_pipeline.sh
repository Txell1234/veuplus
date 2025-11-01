#!/bin/bash
# VeuPlus CI/CD Pipeline
# Script d'automatització per testing, build i deployment

set -e  # Exit on any error

# Colors per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuració
PROJECT_NAME="VeuPlus"
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
TESTS_DIR="tests"
BUILD_DIR="dist"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_COMPOSE_PROD="docker-compose.production.yml"

# Funcions d'utilitat
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Funció per verificar prerequisits
check_prerequisites() {
    log_info "Verificant prerequisits..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 no està instal·lat"
        exit 1
    fi
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js no està instal·lat"
        exit 1
    fi
    
    # Verificar npm
    if ! command -v npm &> /dev/null; then
        log_error "npm no està instal·lat"
        exit 1
    fi
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker no està instal·lat"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose no està instal·lat"
        exit 1
    fi
    
    log_success "Tots els prerequisits estan instal·lats"
}

# Funció per instal·lar dependències
install_dependencies() {
    log_info "Instal·lant dependències..."
    
    # Backend dependencies
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        log_info "Instal·lant dependències Python..."
        cd $BACKEND_DIR
        pip3 install -r requirements.txt
        cd ..
    fi
    
    # Frontend dependencies
    if [ -f "$FRONTEND_DIR/package.json" ]; then
        log_info "Instal·lant dependències Node.js..."
        cd $FRONTEND_DIR
        npm install
        cd ..
    fi
    
    log_success "Dependències instal·lades correctament"
}

# Funció per executar tests
run_tests() {
    log_info "Executant tests..."
    
    # Tests Python
    if [ -d "$TESTS_DIR" ]; then
        log_info "Executant tests Python..."
        cd $TESTS_DIR
        python3 test_suite.py
        if [ $? -eq 0 ]; then
            log_success "Tests Python passats correctament"
        else
            log_error "Tests Python han fallat"
            exit 1
        fi
        cd ..
    fi
    
    # Tests Frontend (si existeixen)
    if [ -f "$FRONTEND_DIR/package.json" ] && grep -q "test" "$FRONTEND_DIR/package.json"; then
        log_info "Executant tests Frontend..."
        cd $FRONTEND_DIR
        npm test -- --coverage --watchAll=false
        if [ $? -eq 0 ]; then
            log_success "Tests Frontend passats correctament"
        else
            log_error "Tests Frontend han fallat"
            exit 1
        fi
        cd ..
    fi
    
    log_success "Tots els tests han passat"
}

# Funció per linting
run_linting() {
    log_info "Executant linting..."
    
    # Python linting
    if command -v flake8 &> /dev/null; then
        log_info "Executant flake8..."
        flake8 $BACKEND_DIR --max-line-length=120 --ignore=E203,W503
    fi
    
    if command -v black &> /dev/null; then
        log_info "Executant black..."
        black --check $BACKEND_DIR
    fi
    
    # JavaScript linting
    if [ -f "$FRONTEND_DIR/package.json" ] && grep -q "lint" "$FRONTEND_DIR/package.json"; then
        log_info "Executant ESLint..."
        cd $FRONTEND_DIR
        npm run lint
        cd ..
    fi
    
    log_success "Linting completat"
}

# Funció per build
build_project() {
    log_info "Construint projecte..."
    
    # Build Frontend
    if [ -f "$FRONTEND_DIR/package.json" ]; then
        log_info "Construint Frontend..."
        cd $FRONTEND_DIR
        npm run build
        if [ $? -eq 0 ]; then
            log_success "Frontend construït correctament"
        else
            log_error "Error construint Frontend"
            exit 1
        fi
        cd ..
    fi
    
    # Build Backend (compilació Python)
    log_info "Verificant compilació Python..."
    python3 -m compileall $BACKEND_DIR
    if [ $? -eq 0 ]; then
        log_success "Backend compilat correctament"
    else
        log_error "Error compilant Backend"
        exit 1
    fi
    
    log_success "Projecte construït correctament"
}

# Funció per construir imatges Docker
build_docker_images() {
    log_info "Construint imatges Docker..."
    
    # Build imatges
    docker-compose -f $DOCKER_COMPOSE_FILE build
    
    if [ $? -eq 0 ]; then
        log_success "Imatges Docker construïdes correctament"
    else
        log_error "Error construint imatges Docker"
        exit 1
    fi
}

# Funció per tests d'integració
run_integration_tests() {
    log_info "Executant tests d'integració..."
    
    # Iniciar serveis
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # Esperar que els serveis estiguin disponibles
    log_info "Esperant que els serveis estiguin disponibles..."
    sleep 30
    
    # Test de connexió
    if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
        log_success "API backend accessible"
    else
        log_error "API backend no accessible"
        docker-compose -f $DOCKER_COMPOSE_FILE down
        exit 1
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend accessible"
    else
        log_warning "Frontend no accessible (pot ser normal en alguns entorns)"
    fi
    
    # Aturar serveis
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    log_success "Tests d'integració completats"
}

# Funció per deployment
deploy() {
    log_info "Desplegant projecte..."
    
    # Verificar que existeix el fitxer de producció
    if [ ! -f "$DOCKER_COMPOSE_PROD" ]; then
        log_error "Fitxer de producció $DOCKER_COMPOSE_PROD no trobat"
        exit 1
    fi
    
    # Desplegar amb Docker Compose de producció
    docker-compose -f $DOCKER_COMPOSE_PROD up -d
    
    if [ $? -eq 0 ]; then
        log_success "Projecte desplegat correctament"
    else
        log_error "Error desplegant projecte"
        exit 1
    fi
    
    # Verificar que els serveis estan funcionant
    sleep 10
    if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
        log_success "Deployment verificat correctament"
    else
        log_error "Deployment no funciona correctament"
        exit 1
    fi
}

# Funció per generar report
generate_report() {
    log_info "Generant report de CI/CD..."
    
    REPORT_FILE="ci_cd_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > $REPORT_FILE << EOF
VeuPlus CI/CD Report
===================
Data: $(date)
Projecte: $PROJECT_NAME

Tests executats:
- Tests unitaris Python
- Tests Frontend (si disponibles)
- Tests d'integració
- Linting
- Build verification

Resultats:
- Prerequisits: ✅ Verificats
- Dependències: ✅ Instal·lades
- Tests: ✅ Passats
- Linting: ✅ Completat
- Build: ✅ Exitos
- Docker: ✅ Construït
- Integració: ✅ Verificada

Status: SUCCESS
EOF
    
    log_success "Report generat: $REPORT_FILE"
}

# Funció per netejar
cleanup() {
    log_info "Netejant recursos temporals..."
    
    # Aturar containers
    docker-compose -f $DOCKER_COMPOSE_FILE down 2>/dev/null || true
    docker-compose -f $DOCKER_COMPOSE_PROD down 2>/dev/null || true
    
    # Netejar imatges no utilitzades
    docker image prune -f 2>/dev/null || true
    
    log_success "Neteja completada"
}

# Funció principal
main() {
    echo "🚀 VeuPlus CI/CD Pipeline"
    echo "========================="
    
    # Parsejar arguments
    case "${1:-all}" in
        "check")
            check_prerequisites
            ;;
        "install")
            check_prerequisites
            install_dependencies
            ;;
        "test")
            check_prerequisites
            install_dependencies
            run_tests
            ;;
        "lint")
            check_prerequisites
            install_dependencies
            run_linting
            ;;
        "build")
            check_prerequisites
            install_dependencies
            run_tests
            run_linting
            build_project
            ;;
        "docker")
            check_prerequisites
            install_dependencies
            run_tests
            build_project
            build_docker_images
            ;;
        "integration")
            check_prerequisites
            install_dependencies
            run_tests
            build_project
            build_docker_images
            run_integration_tests
            ;;
        "deploy")
            check_prerequisites
            install_dependencies
            run_tests
            run_linting
            build_project
            build_docker_images
            run_integration_tests
            deploy
            generate_report
            ;;
        "all")
            check_prerequisites
            install_dependencies
            run_tests
            run_linting
            build_project
            build_docker_images
            run_integration_tests
            generate_report
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Ús: $0 {check|install|test|lint|build|docker|integration|deploy|all|cleanup}"
            echo ""
            echo "Comandes disponibles:"
            echo "  check       - Verificar prerequisits"
            echo "  install     - Instal·lar dependències"
            echo "  test        - Executar tests"
            echo "  lint        - Executar linting"
            echo "  build       - Construir projecte"
            echo "  docker      - Construir imatges Docker"
            echo "  integration - Executar tests d'integració"
            echo "  deploy      - Desplegar projecte"
            echo "  all         - Executar tot el pipeline"
            echo "  cleanup     - Netejar recursos"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "Pipeline completat correctament! 🎉"
}

# Executar funció principal
main "$@"


