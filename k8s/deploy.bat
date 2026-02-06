@echo off
REM Kubernetes Deployment Script for Research Dashboard (Windows)
REM This script helps you deploy the application to Kubernetes step by step

setlocal enabledelayedexpansion

echo ======================================
echo Research Dashboard K8s Deployment
echo ======================================
echo.

REM Step 1: Check if Kubernetes is running
echo Step 1: Checking Kubernetes cluster...
kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Kubernetes cluster is not accessible
    echo Please enable Kubernetes in Docker Desktop
    exit /b 1
)
echo [OK] Kubernetes cluster is running
echo.

REM Step 2: Build Docker images
echo Step 2: Building Docker images...
echo This may take a few minutes...
cd ..
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Docker images
    exit /b 1
)
echo [OK] Docker images built successfully
cd k8s
echo.

REM Step 3: Create namespace
echo Step 3: Creating namespace...
kubectl apply -f namespace.yaml
echo [OK] Namespace created
echo.

REM Step 4: Create secrets
echo Step 4: Creating secrets...
kubectl apply -f secrets.yaml
echo [OK] Secrets created
echo.

REM Step 5: Create persistent volumes
echo Step 5: Creating persistent volumes...
kubectl apply -f mongodb-pv.yaml
echo [OK] Persistent volumes created
echo.

REM Step 6: Deploy MongoDB
echo Step 6: Deploying MongoDB...
kubectl apply -f mongodb-deployment.yaml
echo Waiting for MongoDB to be ready (this may take 30-60 seconds)...
kubectl wait --for=condition=ready pod -l app=mongodb -n research-dashboard --timeout=120s
if %errorlevel% neq 0 (
    echo [WARNING] MongoDB may not be ready yet. Check with: kubectl get pods -n research-dashboard
) else (
    echo [OK] MongoDB deployed
)
echo.

REM Step 7: Deploy FastAPI
echo Step 7: Deploying FastAPI...
kubectl apply -f api-deployment.yaml
echo Waiting for API to be ready...
kubectl wait --for=condition=ready pod -l app=api -n research-dashboard --timeout=90s
if %errorlevel% neq 0 (
    echo [WARNING] API may not be ready yet. Check with: kubectl get pods -n research-dashboard
) else (
    echo [OK] API deployed
)
echo.

REM Step 8: Deploy Streamlit
echo Step 8: Deploying Streamlit dashboard...
kubectl apply -f streamlit-deployment.yaml
echo Waiting for Streamlit to be ready...
kubectl wait --for=condition=ready pod -l app=streamlit -n research-dashboard --timeout=90s
if %errorlevel% neq 0 (
    echo [WARNING] Streamlit may not be ready yet. Check with: kubectl get pods -n research-dashboard
) else (
    echo [OK] Streamlit deployed
)
echo.

REM Step 9: Show status
echo Step 9: Deployment status...
echo.
echo Pods:
kubectl get pods -n research-dashboard
echo.
echo Services:
kubectl get services -n research-dashboard
echo.

REM Step 10: Get access URL
echo ======================================
echo Deployment Complete!
echo ======================================
echo.

REM Get Windows IP address for network access
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    goto :found_ip
)
:found_ip

echo Access your dashboard:
echo   Local:   http://localhost:30501
if defined IP (
    echo   Network: http://!IP!:30501
)
echo.
echo Multi-host testing (from other devices on your network):
if defined IP (
    echo   1. From laptop/phone browser: http://!IP!:30501
)
echo   2. View pods: kubectl get pods -n research-dashboard
echo   3. View logs: kubectl logs -n research-dashboard -l app=streamlit --tail=20
echo.
echo Useful commands:
echo   kubectl get pods -n research-dashboard              # List all pods
echo   kubectl logs ^<pod-name^> -n research-dashboard       # View pod logs
echo   kubectl describe pod ^<pod-name^> -n research-dashboard # Pod details
echo.
echo To scale your application:
echo   kubectl scale deployment streamlit --replicas=5 -n research-dashboard
echo.
echo To delete everything:
echo   kubectl delete namespace research-dashboard
echo.

endlocal
