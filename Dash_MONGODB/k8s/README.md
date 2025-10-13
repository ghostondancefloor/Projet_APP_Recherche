# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Research Dashboard application.

## 📚 What You'll Learn

By deploying this application to Kubernetes, you'll learn:

1. **Pods** - The smallest deployable units (containers)
2. **Deployments** - Managing multiple pod replicas
3. **Services** - Networking and load balancing
4. **PersistentVolumes** - Storage management
5. **Secrets** - Managing sensitive data
6. **ConfigMaps** - Managing configuration
7. **Namespaces** - Resource organization
8. **Scaling** - Horizontal pod autoscaling
9. **Health Checks** - Liveness and readiness probes
10. **Resource Limits** - CPU and memory management

---

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** with Kubernetes enabled
2. **kubectl** CLI installed (comes with Docker Desktop)
3. Docker images built: `docker-compose build`

### Deploy Everything (Easy Mode)

```bash
cd k8s
./deploy.sh
```

This script will:
- ✅ Check if Kubernetes is running
- ✅ Build Docker images
- ✅ Create namespace
- ✅ Deploy MongoDB with persistent storage
- ✅ Deploy FastAPI (2 replicas)
- ✅ Deploy Streamlit (2 replicas)
- ✅ Wait for all pods to be ready

### Access the Dashboard

Once deployed, access at: **http://localhost:8501**

---

## 📁 File Structure

```
k8s/
├── namespace.yaml              # Creates 'research-dashboard' namespace
├── secrets.yaml                # Stores JWT secrets and passwords
├── mongodb-pv.yaml            # Persistent Volume for MongoDB data
├── mongodb-deployment.yaml    # MongoDB Deployment + Service
├── api-deployment.yaml        # FastAPI Deployment + Service
├── streamlit-deployment.yaml  # Streamlit Deployment + Service
├── deploy.sh                  # Automated deployment script
└── README.md                  # This file
```

---

## 🎓 Manual Deployment (Learning Mode)

If you want to learn by doing each step manually:

### Step 1: Create Namespace

```bash
kubectl apply -f namespace.yaml
```

**What this does:** Creates a logical partition for your app resources.

**Verify:**
```bash
kubectl get namespaces
```

### Step 2: Create Secrets

```bash
kubectl apply -f secrets.yaml -n research-dashboard
```

**What this does:** Stores sensitive data (passwords, keys) securely.

**Verify:**
```bash
kubectl get secrets -n research-dashboard
kubectl describe secret app-secrets -n research-dashboard
```

### Step 3: Create Persistent Storage

```bash
kubectl apply -f mongodb-pv.yaml -n research-dashboard
```

**What this does:** Creates storage for MongoDB data that persists even if pods restart.

**Verify:**
```bash
kubectl get pv
kubectl get pvc -n research-dashboard
```

### Step 4: Deploy MongoDB

```bash
kubectl apply -f mongodb-deployment.yaml -n research-dashboard
```

**What this does:** 
- Creates 1 MongoDB pod
- Creates a Service to allow other pods to connect
- Mounts persistent storage

**Verify:**
```bash
kubectl get pods -n research-dashboard
kubectl get services -n research-dashboard
kubectl logs <mongodb-pod-name> -n research-dashboard
```

**Wait for MongoDB to be ready:**
```bash
kubectl wait --for=condition=ready pod -l app=mongodb -n research-dashboard --timeout=120s
```

### Step 5: Deploy FastAPI

```bash
kubectl apply -f api-deployment.yaml -n research-dashboard
```

**What this does:**
- Creates 2 API pods (for load balancing)
- Creates a Service
- Sets up health checks

**Verify:**
```bash
kubectl get pods -n research-dashboard -l app=api
kubectl logs <api-pod-name> -n research-dashboard
```

### Step 6: Deploy Streamlit

```bash
kubectl apply -f streamlit-deployment.yaml -n research-dashboard
```

**What this does:**
- Creates 2 Streamlit pods
- Creates a LoadBalancer Service (accessible from your machine)

**Verify:**
```bash
kubectl get pods -n research-dashboard -l app=streamlit
kubectl get services -n research-dashboard
```

### Step 7: Access the Application

```bash
# Get the service URL
kubectl get service streamlit-service -n research-dashboard

# Should show:
# TYPE: LoadBalancer
# EXTERNAL-IP: localhost
# PORT: 8501
```

Open: **http://localhost:8501**

---

## 🔍 Monitoring & Debugging

### View All Resources

```bash
kubectl get all -n research-dashboard
```

### Check Pod Status

```bash
# List all pods
kubectl get pods -n research-dashboard

# Detailed pod information
kubectl describe pod <pod-name> -n research-dashboard

# View pod logs
kubectl logs <pod-name> -n research-dashboard

# Follow logs in real-time
kubectl logs -f <pod-name> -n research-dashboard

# View logs from all replicas of a deployment
kubectl logs -f deployment/api -n research-dashboard
```

### Check Services

```bash
# List services
kubectl get services -n research-dashboard

# Service details
kubectl describe service api-service -n research-dashboard
```

### Check Resource Usage

```bash
# CPU and Memory usage
kubectl top pods -n research-dashboard
kubectl top nodes
```

### Enter a Pod (Shell Access)

```bash
# Enter MongoDB pod
kubectl exec -it <mongodb-pod-name> -n research-dashboard -- mongosh

# Enter API pod
kubectl exec -it <api-pod-name> -n research-dashboard -- /bin/bash
```

---

## 📊 Scaling Your Application

### Scale API Pods

```bash
# Scale up to 5 replicas
kubectl scale deployment api --replicas=5 -n research-dashboard

# Scale down to 1 replica
kubectl scale deployment api --replicas=1 -n research-dashboard

# Verify
kubectl get pods -n research-dashboard -l app=api
```

### Scale Streamlit Pods

```bash
# Scale to 3 replicas
kubectl scale deployment streamlit --replicas=3 -n research-dashboard

# Watch pods being created
kubectl get pods -n research-dashboard -w
```

### Auto-scaling (Advanced)

Create a Horizontal Pod Autoscaler:

```bash
# Auto-scale API based on CPU usage (50% threshold)
kubectl autoscale deployment api --cpu-percent=50 --min=2 --max=10 -n research-dashboard

# Check autoscaler status
kubectl get hpa -n research-dashboard
```

---

## 🔄 Rolling Updates

Update your application without downtime:

### Update API Image

```bash
# Rebuild image with changes
docker-compose build api

# Update deployment
kubectl rollout restart deployment/api -n research-dashboard

# Watch the rollout
kubectl rollout status deployment/api -n research-dashboard

# Check rollout history
kubectl rollout history deployment/api -n research-dashboard

# Rollback if needed
kubectl rollout undo deployment/api -n research-dashboard
```

---

## 🧹 Cleanup

### Delete Everything

```bash
# Delete the entire namespace (removes all resources)
kubectl delete namespace research-dashboard
```

### Delete Specific Resources

```bash
# Delete just one deployment
kubectl delete deployment api -n research-dashboard

# Delete a service
kubectl delete service api-service -n research-dashboard
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n research-dashboard

# Common issues:
# - ImagePullBackOff: Image not found (build images first)
# - CrashLoopBackOff: Container keeps crashing (check logs)
# - Pending: Not enough resources
```

### Can't Access Dashboard

```bash
# Check if service is running
kubectl get service streamlit-service -n research-dashboard

# Check if pods are ready
kubectl get pods -n research-dashboard -l app=streamlit

# Check service endpoint
kubectl get endpoints streamlit-service -n research-dashboard
```

### Database Issues

```bash
# Check MongoDB logs
kubectl logs <mongodb-pod-name> -n research-dashboard

# Enter MongoDB and check data
kubectl exec -it <mongodb-pod-name> -n research-dashboard -- mongosh
> use research_db_structure
> db.users.countDocuments()
```

---

## 📖 Learning Resources

### Essential Commands Cheat Sheet

```bash
# Get resources
kubectl get pods -n research-dashboard
kubectl get services -n research-dashboard
kubectl get deployments -n research-dashboard
kubectl get all -n research-dashboard

# Describe (detailed info)
kubectl describe pod <name> -n research-dashboard
kubectl describe service <name> -n research-dashboard

# Logs
kubectl logs <pod-name> -n research-dashboard
kubectl logs -f <pod-name> -n research-dashboard  # Follow
kubectl logs <pod-name> --previous -n research-dashboard  # Previous crash

# Execute commands
kubectl exec -it <pod-name> -n research-dashboard -- /bin/bash

# Port forwarding (access internal services)
kubectl port-forward service/api-service 8000:8000 -n research-dashboard

# Copy files
kubectl cp <pod-name>:/path/to/file ./local-file -n research-dashboard

# Delete
kubectl delete pod <name> -n research-dashboard
kubectl delete deployment <name> -n research-dashboard
```

### Key Concepts

1. **Pod** = One or more containers running together
2. **Deployment** = Manages multiple pod replicas
3. **Service** = Stable network endpoint for pods
4. **ReplicaSet** = Ensures desired number of pods running
5. **Label** = Key-value pair for organizing resources
6. **Selector** = Queries resources by labels
7. **Namespace** = Virtual cluster for isolation

---

## 🎯 Next Steps

After getting comfortable, try:

1. **Add Ingress** - Single entry point for multiple services
2. **Setup Monitoring** - Prometheus + Grafana
3. **Add CI/CD** - GitHub Actions → Kubernetes
4. **Multi-environment** - Dev, Staging, Production namespaces
5. **StatefulSets** - For database clustering
6. **Network Policies** - Control traffic between pods
7. **Resource Quotas** - Limit resource usage per namespace

---

## 💡 Tips

- Use `-n research-dashboard` in all commands (or set default namespace)
- Watch resources with `-w` flag: `kubectl get pods -w`
- Use `kubectl explain <resource>` for documentation
- Tab completion: `kubectl completion zsh` (add to .zshrc)

---

**Questions?** Check the main README.md or Kubernetes documentation:
- https://kubernetes.io/docs/
- https://kubectl.docs.kubernetes.io/

Happy Learning! 🚀
