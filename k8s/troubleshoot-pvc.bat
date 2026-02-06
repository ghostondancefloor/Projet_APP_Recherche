@echo off
REM PVC Troubleshooting Script for Windows
REM Run this if MongoDB deployment fails with PVC issues

setlocal enabledelayedexpansion

echo ======================================
echo PVC Troubleshooting Script
echo ======================================
echo.

echo [1] Checking Kubernetes cluster...
kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Kubernetes is not running!
    echo Please enable Kubernetes in Docker Desktop:
    echo   Docker Desktop ^> Settings ^> Kubernetes ^> Enable Kubernetes
    pause
    exit /b 1
)
echo [OK] Cluster is running
echo.

echo [2] Checking namespace...
kubectl get namespace research-dashboard >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Namespace 'research-dashboard' does not exist
    echo Creating it now...
    kubectl apply -f namespace.yaml
)
echo [OK] Namespace exists
echo.

echo [3] Current PVC status:
kubectl get pvc -n research-dashboard
echo.

echo [4] Current PV status:
kubectl get pv
echo.

echo [5] Storage Classes available:
kubectl get storageclass
echo.

echo [6] PVC Details:
kubectl describe pvc mongodb-pvc -n research-dashboard 2>nul
echo.

echo [7] Recent events related to storage:
kubectl get events -n research-dashboard --sort-by=.lastTimestamp 2>nul | findstr /i "pvc\|volume\|provision\|mongodb" 
echo.

echo ======================================
echo QUICK FIXES
echo ======================================
echo.
echo Choose an option:
echo   1. Force delete stuck PVC and PV
echo   2. Check MongoDB pod status
echo   3. View MongoDB pod logs
echo   4. Full cleanup (delete all and redeploy)
echo   5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Deleting stuck PVC and PV...
    kubectl delete pvc mongodb-pvc -n research-dashboard --force --grace-period=0 2>nul
    kubectl delete pv mongodb-pv --force --grace-period=0 2>nul
    timeout /t 5 /nobreak >nul
    echo.
    echo Recreating PV and PVC...
    kubectl apply -f mongodb-pv.yaml
    echo Done! Try running deploy.bat again.
)

if "%choice%"=="2" (
    echo.
    echo MongoDB pod status:
    kubectl get pods -n research-dashboard -l app=mongodb -o wide
    echo.
    echo Pod details:
    kubectl describe pod -l app=mongodb -n research-dashboard
)

if "%choice%"=="3" (
    echo.
    echo MongoDB pod logs:
    kubectl logs -l app=mongodb -n research-dashboard --tail=50
)

if "%choice%"=="4" (
    echo.
    echo WARNING: This will delete everything in the research-dashboard namespace!
    set /p confirm="Are you sure? (yes/no): "
    if "!confirm!"=="yes" (
        echo Deleting namespace...
        kubectl delete namespace research-dashboard --timeout=60s
        echo Deleting PV...
        kubectl delete pv mongodb-pv --force --grace-period=0 2>nul
        timeout /t 10 /nobreak >nul
        echo.
        echo Cleanup complete! Run deploy.bat to redeploy.
    ) else (
        echo Cancelled.
    )
)

if "%choice%"=="5" (
    echo Exiting...
    exit /b 0
)

echo.
pause
endlocal
