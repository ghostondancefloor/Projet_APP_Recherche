#!/bin/bash

# Kubernetes Deployment Script for Research Dashboard
# This script helps you deploy the application to Kubernetes step by step

set -e  # Exit on error

echo "======================================"
echo "Research Dashboard K8s Deployment"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if Kubernetes is running
echo -e "${YELLOW}Step 1: Checking Kubernetes cluster...${NC}"
if kubectl cluster-info &> /dev/null; then
    echo -e "${GREEN}Done - Kubernetes cluster is running${NC}"
else
    echo -e "${RED}Failed - Kubernetes cluster is not accessible${NC}"
    echo "Please enable Kubernetes in Docker Desktop"
    exit 1
fi
echo ""

# Step 2: Build Docker images
echo -e "${YELLOW}Step 2: Building Docker images...${NC}"
echo "This may take a few minutes..."
cd ..
docker-compose build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Done - Docker images built successfully${NC}"
else
    echo -e "${RED}Failed - Failed to build Docker images${NC}"
    exit 1
fi
cd k8s
echo ""

# Step 3: Create namespace
echo -e "${YELLOW}Step 3: Creating namespace...${NC}"
kubectl apply -f namespace.yaml
echo -e "${GREEN} Done - Namespace created${NC}"
echo ""

# Step 4: Create secrets
echo -e "${YELLOW}Step 4: Creating secrets...${NC}"
kubectl apply -f secrets.yaml -n research-dashboard
echo -e "${GREEN}Done - Secrets created${NC}"
echo ""

# Step 5: Create persistent volumes
echo -e "${YELLOW}Step 5: Creating persistent volumes...${NC}"

# Check if PV exists and is in Released state
PV_STATUS=$(kubectl get pv mongodb-pv -o jsonpath='{.status.phase}' 2>/dev/null || echo "NotFound")
if [ "$PV_STATUS" = "Released" ]; then
    echo "WARNING: Detected PersistentVolume in Released state. Cleaning up..."
    kubectl delete pv mongodb-pv
    echo "Old PersistentVolume deleted"
fi

# Check if PVC exists in wrong namespace
PVC_IN_DEFAULT=$(kubectl get pvc mongodb-pvc -n default -o name 2>/dev/null || echo "")
if [ -n "$PVC_IN_DEFAULT" ]; then
    echo "WARNING: Detected PVC in default namespace. Cleaning up..."
    kubectl delete pvc mongodb-pvc -n default
    echo "PVC removed from default namespace"
fi

kubectl apply -f mongodb-pv.yaml -n research-dashboard
echo -e "${GREEN}Done - Persistent volumes created${NC}"
echo ""

# Step 6: Deploy MongoDB
echo -e "${YELLOW}Step 6: Deploying MongoDB...${NC}"
kubectl apply -f mongodb-deployment.yaml -n research-dashboard
echo "Waiting for MongoDB to be ready (this may take 30-60 seconds)..."
kubectl wait --for=condition=ready pod -l app=mongodb -n research-dashboard --timeout=120s
echo -e "${GREEN}Done - MongoDB deployed${NC}"
echo ""

# Step 7: Deploy API
echo -e "${YELLOW}Step 7: Deploying FastAPI...${NC}"
kubectl apply -f api-deployment.yaml -n research-dashboard
echo "Waiting for API to be ready..."
kubectl wait --for=condition=ready pod -l app=api -n research-dashboard --timeout=120s
echo -e "${GREEN}Done - API deployed${NC}"
echo ""

# Step 8: Deploy Streamlit
echo -e "${YELLOW}Step 8: Deploying Streamlit dashboard...${NC}"
kubectl apply -f streamlit-deployment.yaml -n research-dashboard
echo "Waiting for Streamlit to be ready..."
kubectl wait --for=condition=ready pod -l app=streamlit -n research-dashboard --timeout=120s
echo -e "${GREEN}Done - Streamlit deployed${NC}"
echo ""

# Step 9: Show status
echo -e "${YELLOW}Step 9: Deployment status...${NC}"
echo ""
echo "Pods:"
kubectl get pods -n research-dashboard
echo ""
echo "Services:"
kubectl get services -n research-dashboard
echo ""

# Step 10: Get access URL
echo -e "${GREEN}======================================"
echo "✓ Deployment Complete!"
echo "======================================${NC}"
echo ""

# Get Mac IP address for network access
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "Access your dashboard:"
echo "  Local:   http://localhost:30501"
if [ -n "$MAC_IP" ]; then
    echo -e "  Network: ${GREEN}http://$MAC_IP:30501${NC}"
fi
echo ""
echo "Multi-host testing (from other devices on your network):"
if [ -n "$MAC_IP" ]; then
    echo "  1. From laptop/phone browser: http://$MAC_IP:30501"
fi
echo "  2. Test load balancing: for i in {1..10}; do curl -s http://$MAC_IP:30501 > /dev/null && echo \"Request \$i: OK\"; done"
echo "  3. View which pods handle requests: kubectl logs -n research-dashboard -l app=streamlit --tail=20"
echo ""
echo "Test high availability:"
echo "  kubectl delete pod -n research-dashboard -l app=streamlit --force | head -n 1"
echo "  (Dashboard should remain accessible during pod restart)"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n research-dashboard              # List all pods"
echo "  kubectl logs <pod-name> -n research-dashboard       # View pod logs"
echo "  kubectl describe pod <pod-name> -n research-dashboard # Pod details"
echo "  kubectl exec -it <pod-name> -n research-dashboard -- /bin/bash  # Enter pod shell"
echo ""
echo "To scale your application:"
echo "  kubectl scale deployment streamlit --replicas=5 -n research-dashboard"
echo ""
echo "To delete everything:"
echo "  kubectl delete namespace research-dashboard"
echo ""
