#!/bin/bash

# Kubernetes Deployment Script for Research Dashboard
# This script helps you deploy the application to Kubernetes step by step

set -e  # Exit on error

echo "======================================"
echo "🚀 Research Dashboard K8s Deployment"
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
    echo -e "${GREEN}✓ Kubernetes cluster is running${NC}"
else
    echo -e "${RED}✗ Kubernetes cluster is not accessible${NC}"
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
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build Docker images${NC}"
    exit 1
fi
cd k8s
echo ""

# Step 3: Create namespace
echo -e "${YELLOW}Step 3: Creating namespace...${NC}"
kubectl apply -f namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Step 4: Create secrets
echo -e "${YELLOW}Step 4: Creating secrets...${NC}"
kubectl apply -f secrets.yaml -n research-dashboard
echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# Step 5: Create persistent volumes
echo -e "${YELLOW}Step 5: Creating persistent volumes...${NC}"
kubectl apply -f mongodb-pv.yaml -n research-dashboard
echo -e "${GREEN}✓ Persistent volumes created${NC}"
echo ""

# Step 6: Deploy MongoDB
echo -e "${YELLOW}Step 6: Deploying MongoDB...${NC}"
kubectl apply -f mongodb-deployment.yaml -n research-dashboard
echo "Waiting for MongoDB to be ready (this may take 30-60 seconds)..."
kubectl wait --for=condition=ready pod -l app=mongodb -n research-dashboard --timeout=120s
echo -e "${GREEN}✓ MongoDB deployed${NC}"
echo ""

# Step 7: Deploy API
echo -e "${YELLOW}Step 7: Deploying FastAPI...${NC}"
kubectl apply -f api-deployment.yaml -n research-dashboard
echo "Waiting for API to be ready..."
kubectl wait --for=condition=ready pod -l app=api -n research-dashboard --timeout=120s
echo -e "${GREEN}✓ API deployed${NC}"
echo ""

# Step 8: Deploy Streamlit
echo -e "${YELLOW}Step 8: Deploying Streamlit dashboard...${NC}"
kubectl apply -f streamlit-deployment.yaml -n research-dashboard
echo "Waiting for Streamlit to be ready..."
kubectl wait --for=condition=ready pod -l app=streamlit -n research-dashboard --timeout=120s
echo -e "${GREEN}✓ Streamlit deployed${NC}"
echo ""

# Step 9: Show status
echo -e "${YELLOW}Step 9: Deployment status...${NC}"
echo ""
echo "📊 Pods:"
kubectl get pods -n research-dashboard
echo ""
echo "🌐 Services:"
kubectl get services -n research-dashboard
echo ""

# Step 10: Get access URL
echo -e "${GREEN}======================================"
echo "✓ Deployment Complete!"
echo "======================================${NC}"
echo ""
echo "Access your dashboard at:"
echo "  http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n research-dashboard              # List all pods"
echo "  kubectl logs <pod-name> -n research-dashboard       # View pod logs"
echo "  kubectl describe pod <pod-name> -n research-dashboard # Pod details"
echo "  kubectl exec -it <pod-name> -n research-dashboard -- /bin/bash  # Enter pod shell"
echo ""
echo "To scale your application:"
echo "  kubectl scale deployment api --replicas=3 -n research-dashboard"
echo ""
echo "To delete everything:"
echo "  kubectl delete namespace research-dashboard"
echo ""
