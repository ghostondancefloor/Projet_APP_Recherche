# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Research Dashboard application with MongoDB, FastAPI, and Streamlit components.

## Documentation

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** (this file) | Deployment guide, operations, troubleshooting |
| **[Deployment Explained](docs/DEPLOYMENT_EXPLAINED.md)** | Technical architecture & networking deep-dive |
| **[Architecture Diagrams](docs/ARCHITECTURE.md)** | Visual system design with Mermaid diagrams |
| **[Documentation Index](docs/)** | Complete documentation overview |

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Network Access](#network-access)
- [File Structure](#file-structure)
- [Manual Deployment](#manual-deployment)
- [Operations](#operations)
- [Testing Kubernetes Features](#testing-kubernetes-features)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

---

## Overview

This Kubernetes deployment demonstrates:

- **Container Orchestration**: Multi-container application management
- **High Availability**: Multiple pod replicas with automatic failover
- **Load Balancing**: Traffic distribution across pod replicas
- **Persistent Storage**: Data retention across pod restarts
- **Secrets Management**: Secure handling of sensitive configuration
- **Resource Management**: CPU and memory limits/requests
- **Health Monitoring**: Liveness and readiness probes
- **Network Access**: Multi-host connectivity via NodePort

### Architecture

- **MongoDB**: 1 replica with 5Gi persistent storage
- **FastAPI**: 2 replicas for API load balancing
- **Streamlit**: 2 replicas for dashboard high availability
- **Service Type**: NodePort for network accessibility (port 30501)

---

## Prerequisites

1. **Docker Desktop** with Kubernetes enabled
   - macOS/Linux: [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. **kubectl** CLI (included with Docker Desktop)
3. **Docker Compose** for building images

**For Windows users:**
- Use `deploy.bat` instead of `deploy.sh`
- Or use Git Bash/WSL to run the bash script

**Verify installation:**
```bash
kubectl version --client
kubectl cluster-info
```

---

## Quick Start

### Automated Deployment

**For macOS/Linux:**
```bash
cd k8s
./deploy.sh
```

**For Windows:**
```cmd
cd k8s
deploy.bat
```

The script performs the following:
1. Validates Kubernetes cluster connectivity
2. Builds Docker images for all services
3. Creates the `research-dashboard` namespace
4. Configures secrets for authentication
5. Provisions persistent storage for MongoDB
6. Deploys MongoDB, API, and Streamlit services
7. Waits for all pods to reach ready state
8. Displays access URLs and network information

### Access URLs

**Local Access:**
```
http://localhost:30501
```

**Network Access (from other devices):**
```
http://<YOUR_IP>:30501
```

The deployment script automatically displays your network IP address.

---

## Network Access

### Multi-Host Configuration

This deployment uses **NodePort** service type, exposing the application on port 30501 across all cluster nodes. This enables access from any device on the same network.

### Finding Your IP Address

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Alternative:**
Check the output of `./deploy.sh` which automatically displays your IP.

### Accessing from Other Devices

Ensure all devices are on the same network, then access:
```
http://192.168.1.100:30501  # Replace with your actual IP
```

**Supported Devices:**
- Laptops (Windows, macOS, Linux)
- Mobile devices (iOS, Android)
- Tablets
- Any device with a web browser

---

## File Structure

```
k8s/
├── namespace.yaml              # Namespace definition
├── secrets.yaml                # JWT secrets and credentials
├── mongodb-pv.yaml            # PersistentVolume and PVC
├── mongodb-deployment.yaml    # MongoDB deployment and service
├── api-deployment.yaml        # FastAPI deployment and service
├── streamlit-deployment.yaml  # Streamlit deployment and service
├── deploy.sh                  # Automated deployment script
├── ARCHITECTURE.md            # Architecture diagrams
└── README.md                  # This file
```

---

## Manual Deployment

For learning purposes, you can deploy each component individually:

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
kubectl get namespaces
```

Creates the `research-dashboard` namespace for resource isolation.

### 2. Configure Secrets

```bash
kubectl apply -f secrets.yaml -n research-dashboard
kubectl get secrets -n research-dashboard
```

Stores JWT tokens and database credentials securely.

### 3. Provision Storage

```bash
kubectl apply -f mongodb-pv.yaml -n research-dashboard
kubectl get pv
kubectl get pvc -n research-dashboard
```

Creates a 5Gi persistent volume for MongoDB data.

### 4. Deploy MongoDB

```bash
kubectl apply -f mongodb-deployment.yaml -n research-dashboard
kubectl wait --for=condition=ready pod -l app=mongodb -n research-dashboard --timeout=120s
```

Deploys MongoDB with persistent storage and internal ClusterIP service.

### 5. Deploy API Service

```bash
kubectl apply -f api-deployment.yaml -n research-dashboard
kubectl wait --for=condition=ready pod -l app=api -n research-dashboard --timeout=120s
```

Deploys 2 FastAPI replicas with load balancing.

### 6. Deploy Dashboard

```bash
kubectl apply -f streamlit-deployment.yaml -n research-dashboard
kubectl wait --for=condition=ready pod -l app=streamlit -n research-dashboard --timeout=120s
```

Deploys 2 Streamlit replicas with NodePort service on port 30501.

### 7. Verify Deployment

```bash
kubectl get all -n research-dashboard
kubectl get service streamlit-service -n research-dashboard
```

Expected output:
```
TYPE: NodePort
PORT(S): 8501:30501/TCP
```

---

## Operations

### Viewing Resources

```bash
# All resources in namespace
kubectl get all -n research-dashboard

# Specific resource types
kubectl get pods -n research-dashboard
kubectl get services -n research-dashboard
kubectl get deployments -n research-dashboard

# Detailed information
kubectl describe pod <pod-name> -n research-dashboard
kubectl describe service <service-name> -n research-dashboard
```

### Viewing Logs

```bash
# Single pod logs
kubectl logs <pod-name> -n research-dashboard

# Follow logs in real-time
kubectl logs -f <pod-name> -n research-dashboard

# All replicas of a deployment
kubectl logs -f deployment/api -n research-dashboard

# Previous container (after crash)
kubectl logs <pod-name> --previous -n research-dashboard
```

### Resource Monitoring

```bash
# Pod resource usage
kubectl top pods -n research-dashboard

# Node resource usage
kubectl top nodes
```

### Shell Access

```bash
# MongoDB shell
kubectl exec -it <mongodb-pod-name> -n research-dashboard -- mongosh

# Bash shell (API/Streamlit pods)
kubectl exec -it <pod-name> -n research-dashboard -- /bin/bash
```

### Scaling

```bash
# Scale deployment
kubectl scale deployment streamlit --replicas=5 -n research-dashboard

# Watch scaling progress
kubectl get pods -n research-dashboard -w

# Auto-scaling (HPA)
kubectl autoscale deployment api --cpu-percent=50 --min=2 --max=10 -n research-dashboard
kubectl get hpa -n research-dashboard
```

### Rolling Updates

```bash
# Rebuild image (from repository root)
cd ..
docker-compose build api
cd k8s

# Restart deployment
kubectl rollout restart deployment/api -n research-dashboard

# Monitor rollout
kubectl rollout status deployment/api -n research-dashboard

# View history
kubectl rollout history deployment/api -n research-dashboard

# Rollback
kubectl rollout undo deployment/api -n research-dashboard
```

### Cleanup

```bash
# Delete entire namespace (all resources)
kubectl delete namespace research-dashboard

# Delete specific resources
kubectl delete deployment <name> -n research-dashboard
kubectl delete service <name> -n research-dashboard
```

---

## Testing Kubernetes Features

### Load Balancing

Test traffic distribution across 2 Streamlit replicas:

```bash
# Send multiple requests
for i in {1..10}; do
  curl -s http://YOUR_IP:30501 > /dev/null && echo "Request $i: OK"
done

# View which pods handled requests
kubectl logs -n research-dashboard -l app=streamlit --tail=20
```

### High Availability

Test zero-downtime during pod failures:

**Terminal 1 (Simulate failure):**
```bash
kubectl delete pod -n research-dashboard -l app=streamlit --force | head -n 1
```

**Terminal 2 (Continuous access test):**
```bash
while true; do
  curl -s http://YOUR_IP:30501 > /dev/null && echo "Success" || echo "Failed"
  sleep 1
done
```

Expected result: No failed requests. Traffic automatically routes to healthy pods.

### Horizontal Scaling

```bash
# Scale up
kubectl scale deployment streamlit --replicas=5 -n research-dashboard

# Verify distribution
kubectl get pods -n research-dashboard -l app=streamlit

# Generate load from multiple devices
ab -n 1000 -c 10 http://YOUR_IP:30501/
```

---

## Troubleshooting

### Pod Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n research-dashboard
kubectl logs <pod-name> -n research-dashboard
```

**Common errors:**
- `ImagePullBackOff`: Run `docker-compose build` from repository root first
- `CrashLoopBackOff`: Check logs for application errors
- `Pending`: Insufficient resources or PVC binding issues

**PersistentVolume issues:**
```bash
# Check PV status
kubectl get pv

# Check PVC status
kubectl get pvc -n research-dashboard

# If PV is in "Released" state, delete and recreate
kubectl delete pv mongodb-pv
kubectl apply -f mongodb-pv.yaml -n research-dashboard
```

### Service Access Issues

**Cannot access locally:**
```bash
# Verify service
kubectl get service streamlit-service -n research-dashboard

# Check endpoints
kubectl get endpoints streamlit-service -n research-dashboard

# Test connectivity
curl http://localhost:30501
```

**Cannot access from network:**
```bash
# Verify NodePort service type
kubectl get service streamlit-service -n research-dashboard
# Should show: TYPE=NodePort, PORT(S)=8501:30501/TCP

# Check macOS firewall
sudo pfctl -s rules | grep 30501

# Temporarily disable firewall (testing only)
sudo pfctl -d

# Verify network connectivity
ping <OTHER_DEVICE_IP>

# Test from local machine with network IP
curl http://<YOUR_MAC_IP>:30501
```

### Database Issues

```bash
# Check MongoDB logs
kubectl logs <mongodb-pod-name> -n research-dashboard

# Verify data
kubectl exec -it <mongodb-pod-name> -n research-dashboard -- mongosh
> use research_db_structure
> show collections
> db.users.countDocuments()
```

---

## Reference

### Essential Commands

```bash
# Resource Management
kubectl get <resource> -n research-dashboard
kubectl describe <resource> <name> -n research-dashboard
kubectl delete <resource> <name> -n research-dashboard

# Pod Management
kubectl exec -it <pod-name> -n research-dashboard -- <command>
kubectl logs <pod-name> -n research-dashboard
kubectl port-forward <pod-name> <local-port>:<pod-port> -n research-dashboard

# File Operations
kubectl cp <pod-name>:/remote/path ./local/path -n research-dashboard

# Deployment Operations
kubectl scale deployment <name> --replicas=<count> -n research-dashboard
kubectl rollout restart deployment/<name> -n research-dashboard
kubectl rollout status deployment/<name> -n research-dashboard
kubectl rollout undo deployment/<name> -n research-dashboard
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Pod** | Smallest deployable unit containing one or more containers |
| **Deployment** | Manages pod replicas and rolling updates |
| **Service** | Stable network endpoint for pod access |
| **ReplicaSet** | Ensures specified number of pod replicas are running |
| **Namespace** | Virtual cluster for resource isolation |
| **Label** | Key-value pairs for resource organization |
| **Selector** | Query mechanism for labels |
| **NodePort** | Service type exposing pods on static port (30000-32767) |
| **PersistentVolume** | Storage resource independent of pod lifecycle |
| **PersistentVolumeClaim** | Request for storage by a pod |

### Service Types

| Type | Description | Use Case |
|------|-------------|----------|
| **ClusterIP** | Internal cluster access only | API, MongoDB |
| **NodePort** | Exposed on static port on all nodes | Dashboard (development/testing) |
| **LoadBalancer** | Cloud provider load balancer | Production external access |

### Best Practices

- Always specify namespace in commands
- Use resource requests and limits
- Implement health checks (liveness/readiness probes)
- Store sensitive data in Secrets
- Use labels for resource organization
- Monitor resource usage regularly
- Test backups and restore procedures
- Document custom configurations

### Additional Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **kubectl Reference**: https://kubectl.docs.kubernetes.io/
- **Architecture Deep-Dive**: [docs/DEPLOYMENT_EXPLAINED.md](docs/DEPLOYMENT_EXPLAINED.md)
- **Visual Diagrams**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Main Project README**: [../README.md](../README.md)

---

**Navigation:**
- [← Back to Main Project](../README.md)
- [Architecture Explanation →](docs/DEPLOYMENT_EXPLAINED.md)
- [Visual Diagrams →](docs/ARCHITECTURE.md)
- [Documentation Index →](docs/)

**Version**: v1.1-multi-host  
**Last Updated**: December 2025
