#!/bin/bash

# ============================================================================
# Monitoring Stack Deployment Script
# Deploys Prometheus + Grafana + MongoDB Exporter to Kubernetes
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="research-dashboard"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    print_success "kubectl is available"
}

# Check if namespace exists
check_namespace() {
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_success "Namespace '$NAMESPACE' exists"
    else
        print_warning "Namespace '$NAMESPACE' does not exist"
        print_info "Creating namespace..."
        kubectl create namespace "$NAMESPACE"
        print_success "Namespace '$NAMESPACE' created"
    fi
}

# Deploy monitoring components
deploy_monitoring() {
    print_header "Deploying Monitoring Stack"

    # Step 1: RBAC and Secrets
    print_info "Step 1/5: Deploying RBAC and Secrets..."
    kubectl apply -f "$SCRIPT_DIR/rbac.yaml"
    kubectl apply -f "$SCRIPT_DIR/secrets.yaml"
    print_success "RBAC and Secrets deployed"

    # Step 2: MongoDB Exporter
    print_info "Step 2/5: Deploying MongoDB Exporter..."
    kubectl apply -f "$SCRIPT_DIR/mongodb-exporter.yaml"
    print_success "MongoDB Exporter deployed"

    # Step 3: Prometheus ConfigMap and Deployment
    print_info "Step 3/5: Deploying Prometheus..."
    kubectl apply -f "$SCRIPT_DIR/prometheus-configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/prometheus-deployment.yaml"
    print_success "Prometheus deployed"

    # Step 4: Grafana ConfigMaps and Deployment
    print_info "Step 4/5: Deploying Grafana..."
    kubectl apply -f "$SCRIPT_DIR/grafana-configmap.yaml"
    kubectl apply -f "$SCRIPT_DIR/grafana-deployment.yaml"
    print_success "Grafana deployed"

    # Step 5: Alerting Rules (optional)
    if [ -f "$SCRIPT_DIR/alerting-rules.yaml" ]; then
        print_info "Step 5/5: Deploying Alerting Rules..."
        kubectl apply -f "$SCRIPT_DIR/alerting-rules.yaml"
        print_success "Alerting Rules deployed"
    else
        print_warning "Step 5/5: Alerting Rules file not found, skipping..."
    fi
}

# Wait for deployments to be ready
wait_for_deployments() {
    print_header "Waiting for Deployments"

    print_info "Waiting for MongoDB Exporter..."
    kubectl rollout status deployment/mongodb-exporter -n "$NAMESPACE" --timeout=120s || true

    print_info "Waiting for Prometheus..."
    kubectl rollout status deployment/prometheus -n "$NAMESPACE" --timeout=120s || true

    print_info "Waiting for Grafana..."
    kubectl rollout status deployment/grafana -n "$NAMESPACE" --timeout=120s || true

    print_success "All monitoring components are ready!"
}

# Get service URLs
get_service_urls() {
    print_header "Monitoring Access Information"

    # Prometheus URL
    PROMETHEUS_PORT=$(kubectl get svc prometheus-service -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "9090")
    PROMETHEUS_LB=$(kubectl get svc prometheus-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
    
    # Grafana URL
    GRAFANA_PORT=$(kubectl get svc grafana-service -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "3000")
    GRAFANA_LB=$(kubectl get svc grafana-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")

    echo -e "${GREEN}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${GREEN}│                  MONITORING STACK DEPLOYED                   │${NC}"
    echo -e "${GREEN}├─────────────────────────────────────────────────────────────┤${NC}"
    echo -e "${GREEN}│                                                             │${NC}"
    echo -e "${GREEN}│  📊 Prometheus:                                             │${NC}"
    echo -e "${GREEN}│     URL: http://${PROMETHEUS_LB}:9090                           │${NC}"
    echo -e "${GREEN}│     Purpose: Metrics collection & querying                  │${NC}"
    echo -e "${GREEN}│                                                             │${NC}"
    echo -e "${GREEN}│  📈 Grafana:                                                │${NC}"
    echo -e "${GREEN}│     URL: http://${GRAFANA_LB}:3000                              │${NC}"
    echo -e "${GREEN}│     Username: admin                                         │${NC}"
    echo -e "${GREEN}│     Password: admin123 (change in production!)              │${NC}"
    echo -e "${GREEN}│                                                             │${NC}"
    echo -e "${GREEN}│  📋 Available Dashboards:                                   │${NC}"
    echo -e "${GREEN}│     - FastAPI Dashboard (API metrics)                       │${NC}"
    echo -e "${GREEN}│     - MongoDB Dashboard (Database metrics)                  │${NC}"
    echo -e "${GREEN}│                                                             │${NC}"
    echo -e "${GREEN}└─────────────────────────────────────────────────────────────┘${NC}"
    
    echo ""
    print_info "For local access with Docker Desktop or Minikube, use:"
    echo -e "  ${YELLOW}kubectl port-forward svc/prometheus-service 9090:9090 -n $NAMESPACE &${NC}"
    echo -e "  ${YELLOW}kubectl port-forward svc/grafana-service 3000:3000 -n $NAMESPACE &${NC}"
}

# Delete monitoring stack
delete_monitoring() {
    print_header "Deleting Monitoring Stack"
    
    print_warning "This will delete all monitoring components!"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        kubectl delete -f "$SCRIPT_DIR/grafana-deployment.yaml" --ignore-not-found
        kubectl delete -f "$SCRIPT_DIR/grafana-configmap.yaml" --ignore-not-found
        kubectl delete -f "$SCRIPT_DIR/prometheus-deployment.yaml" --ignore-not-found
        kubectl delete -f "$SCRIPT_DIR/prometheus-configmap.yaml" --ignore-not-found
        kubectl delete -f "$SCRIPT_DIR/mongodb-exporter.yaml" --ignore-not-found
        kubectl delete -f "$SCRIPT_DIR/alerting-rules.yaml" --ignore-not-found 2>/dev/null || true
        kubectl delete -f "$SCRIPT_DIR/secrets.yaml" --ignore-not-found
        kubectl delete -f "$SCRIPT_DIR/rbac.yaml" --ignore-not-found
        
        print_success "Monitoring stack deleted"
    else
        print_info "Deletion cancelled"
    fi
}

# Show status
show_status() {
    print_header "Monitoring Stack Status"
    
    echo -e "${BLUE}Pods:${NC}"
    kubectl get pods -n "$NAMESPACE" -l 'app in (prometheus,grafana,mongodb-exporter)' -o wide
    
    echo -e "\n${BLUE}Services:${NC}"
    kubectl get svc -n "$NAMESPACE" -l 'app in (prometheus,grafana,mongodb-exporter)'
    
    echo -e "\n${BLUE}PVCs:${NC}"
    kubectl get pvc -n "$NAMESPACE" -l 'app in (prometheus,grafana)'
}

# Main function
main() {
    case "${1:-deploy}" in
        deploy)
            print_header "Monitoring Stack Deployment"
            check_kubectl
            check_namespace
            deploy_monitoring
            wait_for_deployments
            get_service_urls
            ;;
        delete|remove|uninstall)
            delete_monitoring
            ;;
        status)
            show_status
            ;;
        urls|info)
            get_service_urls
            ;;
        *)
            echo "Usage: $0 {deploy|delete|status|urls}"
            echo ""
            echo "Commands:"
            echo "  deploy  - Deploy the monitoring stack (default)"
            echo "  delete  - Remove the monitoring stack"
            echo "  status  - Show current status of monitoring components"
            echo "  urls    - Show access URLs for Prometheus and Grafana"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
