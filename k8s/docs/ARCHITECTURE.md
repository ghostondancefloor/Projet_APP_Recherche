# Kubernetes Architecture - Research Dashboard

This document provides visual diagrams of the Kubernetes deployment architecture for the Research Dashboard application.

> **Deployment Guide**: See [README.md](../README.md) for setup instructions.  
> **Technical Details**: See [DEPLOYMENT_EXPLAINED.md](DEPLOYMENT_EXPLAINED.md) for architecture explanation.

---

## Table of Contents
- [Overview Diagram](#overview-diagram)
- [Network Architecture](#network-architecture)
- [Deployment Flow](#deployment-flow)
- [Data Flow](#data-flow)
- [Resource Hierarchy](#resource-hierarchy)

---

## Overview Diagram

This diagram shows the complete Kubernetes architecture with all components:

```mermaid
graph TB
    subgraph "External Access"
        User[👤 User Browser]
    end
    
    subgraph "Kubernetes Cluster - research-dashboard namespace"
        subgraph "LoadBalancer Service"
            LB[streamlit-service<br/>Type: LoadBalancer<br/>Port: 8501]
        end
        
        subgraph "Streamlit Pods"
            ST1[streamlit-pod-1<br/>CPU: 1.5 cores<br/>RAM: 1.5GB]
            ST2[streamlit-pod-2<br/>CPU: 1.5 cores<br/>RAM: 1.5GB]
        end
        
        subgraph "API Service"
            APISVC[api-service<br/>Type: ClusterIP<br/>Port: 8000]
        end
        
        subgraph "API Pods"
            API1[api-pod-1<br/>CPU: 1 core<br/>RAM: 1GB]
            API2[api-pod-2<br/>CPU: 1 core<br/>RAM: 1GB]
        end
        
        subgraph "MongoDB Service"
            DBSVC[mongodb-service<br/>Type: ClusterIP<br/>Port: 27017]
        end
        
        subgraph "MongoDB Pod"
            DB[mongodb-pod<br/>CPU: 2 cores<br/>RAM: 2GB]
        end
        
        subgraph "Storage"
            PV[PersistentVolume<br/>5Gi Storage<br/>hostPath: /mnt/data/mongodb]
            PVC[PersistentVolumeClaim<br/>5Gi Request]
        end
        
        subgraph "Configuration"
            SEC[Secrets<br/>- JWT Token<br/>- MongoDB Password]
        end
    end
    
    User -->|http://localhost:8501| LB
    LB -->|Load Balance| ST1
    LB -->|Load Balance| ST2
    ST1 -->|API Requests| APISVC
    ST2 -->|API Requests| APISVC
    APISVC -->|Load Balance| API1
    APISVC -->|Load Balance| API2
    API1 -->|Database Queries| DBSVC
    API2 -->|Database Queries| DBSVC
    DBSVC --> DB
    DB -->|Mount| PVC
    PVC -->|Bound to| PV
    ST1 -.->|Read Config| SEC
    ST2 -.->|Read Config| SEC
    API1 -.->|Read Secrets| SEC
    API2 -.->|Read Secrets| SEC
    DB -.->|Read Secrets| SEC
    
    style User fill:#e1f5fe
    style LB fill:#fff9c4
    style ST1 fill:#c8e6c9
    style ST2 fill:#c8e6c9
    style APISVC fill:#fff9c4
    style API1 fill:#ffccbc
    style API2 fill:#ffccbc
    style DBSVC fill:#fff9c4
    style DB fill:#d1c4e9
    style PV fill:#f8bbd0
    style PVC fill:#f8bbd0
    style SEC fill:#b0bec5
```

---

## Network Architecture

This diagram illustrates the network topology and service communication:

```mermaid
graph LR
    subgraph "External Network"
        Internet[🌐 Internet/Localhost]
    end
    
    subgraph "Kubernetes Network - research-dashboard"
        subgraph "External Layer"
            LB[LoadBalancer<br/>streamlit-service<br/>External: localhost:8501<br/>Internal: 10.106.x.x:8501]
        end
        
        subgraph "Application Layer"
            ST[Streamlit Pods x2<br/>ENV: API_BASE_URL=<br/>http://api-service:8000]
        end
        
        subgraph "API Layer"
            APISVC[ClusterIP<br/>api-service<br/>10.101.x.x:8000]
            API[API Pods x2<br/>FastAPI Server<br/>Port: 8000]
        end
        
        subgraph "Data Layer"
            DBSVC[ClusterIP<br/>mongodb-service<br/>10.108.x.x:27017]
            DB[MongoDB Pod<br/>Port: 27017]
        end
        
        subgraph "Storage Layer"
            PV[PersistentVolume<br/>5Gi]
        end
    end
    
    Internet -->|HTTP| LB
    LB -->|HTTP| ST
    ST -->|REST API| APISVC
    APISVC -->|Forward| API
    API -->|MongoDB Protocol| DBSVC
    DBSVC -->|Forward| DB
    DB -->|Read/Write| PV
    
    style Internet fill:#e3f2fd
    style LB fill:#fff9c4
    style ST fill:#c8e6c9
    style APISVC fill:#fff9c4
    style API fill:#ffccbc
    style DBSVC fill:#fff9c4
    style DB fill:#d1c4e9
    style PV fill:#f8bbd0
```

---

## Deployment Flow

This shows the sequence of deployment steps:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant K8s as Kubernetes API
    participant NS as Namespace
    participant SEC as Secrets
    participant PV as PersistentVolume
    participant DB as MongoDB
    participant API as FastAPI
    participant ST as Streamlit
    participant User as End User
    
    Dev->>K8s: 1. kubectl apply -f namespace.yaml
    K8s->>NS: Create research-dashboard namespace
    
    Dev->>K8s: 2. kubectl apply -f secrets.yaml
    K8s->>SEC: Store JWT & passwords (base64)
    
    Dev->>K8s: 3. kubectl apply -f mongodb-pv.yaml
    K8s->>PV: Create 5Gi storage volume
    
    Dev->>K8s: 4. kubectl apply -f mongodb-deployment.yaml
    K8s->>DB: Deploy MongoDB pod
    DB->>PV: Mount persistent volume
    DB->>SEC: Load MongoDB password
    DB-->>K8s: Pod Ready ✓
    
    Dev->>K8s: 5. kubectl apply -f api-deployment.yaml
    K8s->>API: Deploy 2 API pods
    API->>SEC: Load JWT secret
    API->>DB: Connect to MongoDB
    API-->>K8s: Pods Ready ✓
    
    Dev->>K8s: 6. kubectl apply -f streamlit-deployment.yaml
    K8s->>ST: Deploy 2 Streamlit pods
    ST->>SEC: Load API URL config
    ST->>API: Connect to API service
    ST-->>K8s: Pods Ready ✓
    
    K8s-->>Dev: Deployment Complete ✓
    
    User->>ST: Access http://localhost:8501
    ST->>API: Forward requests
    API->>DB: Query data
    DB-->>API: Return results
    API-->>ST: JSON response
    ST-->>User: Render dashboard
```

---

## Data Flow

This diagram shows how data flows through the system:

```mermaid
flowchart TD
    subgraph "User Interaction"
        A[User Opens Browser<br/>http://localhost:8501]
    end
    
    subgraph "Streamlit Layer - 2 Pods"
        B[Streamlit Pod<br/>Load Balancer selects pod]
        C[Login Form Rendered]
        D[User Enters Credentials]
    end
    
    subgraph "API Layer - 2 Pods"
        E[POST /login<br/>to api-service:8000]
        F[API Pod<br/>Load Balancer selects pod]
        G[Validate Credentials]
        H[Generate JWT Token]
    end
    
    subgraph "Database Layer - 1 Pod"
        I[Query MongoDB<br/>mongodb-service:27017]
        J[MongoDB Pod]
        K[Find User in 'users' collection]
        L[Return User Data]
    end
    
    subgraph "Storage"
        M[(PersistentVolume<br/>5Gi<br/>/mnt/data/mongodb)]
    end
    
    subgraph "Response Flow"
        N[JWT Token Returned]
        O[Streamlit Stores Token]
        P[Dashboard Rendered]
        Q[Subsequent API Calls<br/>Include JWT Header]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> I
    I --> J
    J --> K
    K --> M
    M --> L
    L --> H
    H --> N
    N --> O
    O --> P
    P --> Q
    Q --> F
    
    style A fill:#e1f5fe
    style B fill:#c8e6c9
    style F fill:#ffccbc
    style J fill:#d1c4e9
    style M fill:#f8bbd0
    style N fill:#fff9c4
```

---

## Resource Hierarchy

This shows the Kubernetes resource organization:

```mermaid
graph TD
    subgraph "Kubernetes Cluster"
        NS[Namespace: research-dashboard]
        
        subgraph "Configuration Resources"
            SEC[Secrets<br/>- app-secrets]
        end
        
        subgraph "Storage Resources"
            PV[PersistentVolume<br/>- mongodb-pv<br/>- 5Gi, hostPath]
            PVC[PersistentVolumeClaim<br/>- mongodb-pvc<br/>- 5Gi request]
        end
        
        subgraph "Workload Resources"
            DEP1[Deployment: mongodb<br/>Replicas: 1]
            DEP2[Deployment: api<br/>Replicas: 2]
            DEP3[Deployment: streamlit<br/>Replicas: 2]
            
            RS1[ReplicaSet: mongodb-xxx]
            RS2[ReplicaSet: api-xxx]
            RS3[ReplicaSet: streamlit-xxx]
            
            POD1[Pod: mongodb-xxx-yyy]
            POD2[Pod: api-xxx-yyy]
            POD3[Pod: api-xxx-zzz]
            POD4[Pod: streamlit-xxx-aaa]
            POD5[Pod: streamlit-xxx-bbb]
        end
        
        subgraph "Network Resources"
            SVC1[Service: mongodb-service<br/>Type: ClusterIP<br/>Port: 27017]
            SVC2[Service: api-service<br/>Type: ClusterIP<br/>Port: 8000]
            SVC3[Service: streamlit-service<br/>Type: LoadBalancer<br/>Port: 8501]
        end
        
        subgraph "Pods Details"
            C1[Container: mongodb<br/>Image: projetapprecherche-mongo:latest<br/>CPU: 2 cores, RAM: 2GB]
            C2[Container: api<br/>Image: projetapprecherche-api:latest<br/>CPU: 1 core, RAM: 1GB]
            C3[Container: streamlit<br/>Image: projetapprecherche-streamlit:latest<br/>CPU: 1.5 cores, RAM: 1.5GB]
        end
    end
    
    NS --> SEC
    NS --> PV
    NS --> PVC
    NS --> DEP1
    NS --> DEP2
    NS --> DEP3
    NS --> SVC1
    NS --> SVC2
    NS --> SVC3
    
    PV -.->|Bound| PVC
    
    DEP1 --> RS1
    DEP2 --> RS2
    DEP3 --> RS3
    
    RS1 --> POD1
    RS2 --> POD2
    RS2 --> POD3
    RS3 --> POD4
    RS3 --> POD5
    
    POD1 --> C1
    POD2 --> C2
    POD3 --> C2
    POD4 --> C3
    POD5 --> C3
    
    SVC1 -.->|Selects| POD1
    SVC2 -.->|Selects| POD2
    SVC2 -.->|Selects| POD3
    SVC3 -.->|Selects| POD4
    SVC3 -.->|Selects| POD5
    
    POD1 -.->|Mounts| PVC
    POD1 -.->|Reads| SEC
    POD2 -.->|Reads| SEC
    POD3 -.->|Reads| SEC
    POD4 -.->|Reads| SEC
    POD5 -.->|Reads| SEC
    
    style NS fill:#e1bee7
    style SEC fill:#b0bec5
    style PV fill:#f8bbd0
    style PVC fill:#f8bbd0
    style DEP1 fill:#d1c4e9
    style DEP2 fill:#ffccbc
    style DEP3 fill:#c8e6c9
    style SVC1 fill:#fff9c4
    style SVC2 fill:#fff9c4
    style SVC3 fill:#fff9c4
```

---

## Component Details

### 📦 Pods and Replicas

| Component | Replicas | CPU Limit | Memory Limit | Purpose |
|-----------|----------|-----------|--------------|---------|
| MongoDB | 1 | 2 cores | 2GB | Primary database, stateful |
| FastAPI | 2 | 1 core | 1GB | Backend API, load balanced |
| Streamlit | 2 | 1.5 cores | 1.5GB | Frontend dashboard, load balanced |

### 🌐 Services

| Service Name | Type | Internal IP | External Access | Purpose |
|--------------|------|-------------|-----------------|---------|
| mongodb-service | ClusterIP | 10.108.x.x:27017 | Internal only | Database access |
| api-service | ClusterIP | 10.101.x.x:8000 | Internal only | API endpoints |
| streamlit-service | LoadBalancer | 10.106.x.x:8501 | localhost:8501 | User interface |

### 💾 Storage

| Resource | Type | Size | Path | Purpose |
|----------|------|------|------|---------|
| mongodb-pv | PersistentVolume | 5Gi | /mnt/data/mongodb | Physical storage |
| mongodb-pvc | PersistentVolumeClaim | 5Gi | - | Storage request |

### 🔐 Secrets

| Secret Name | Keys | Used By |
|-------------|------|---------|
| app-secrets | jwt-secret-key | API pods |
| app-secrets | mongo-password | MongoDB, API pods |

---

## Health Checks & Probes

```mermaid
graph TD
    subgraph "Liveness Probes - Is the app alive?"
        L1[MongoDB: TCP Socket<br/>Port 27017<br/>Delay: 60s, Period: 10s]
        L2[API: HTTP GET /<br/>Port 8000<br/>Delay: 30s, Period: 10s]
        L3[Streamlit: HTTP GET /<br/>Port 8501<br/>Delay: 60s, Period: 10s]
    end
    
    subgraph "Readiness Probes - Is the app ready?"
        R1[MongoDB: TCP Socket<br/>Port 27017<br/>Delay: 30s, Period: 5s]
        R2[API: HTTP GET /<br/>Port 8000<br/>Delay: 20s, Period: 5s]
        R3[Streamlit: HTTP GET /<br/>Port 8501<br/>Delay: 30s, Period: 5s]
    end
    
    subgraph "Actions on Failure"
        A1[Restart Container]
        A2[Remove from Service<br/>Stop routing traffic]
    end
    
    L1 -.->|Fails| A1
    L2 -.->|Fails| A1
    L3 -.->|Fails| A1
    
    R1 -.->|Fails| A2
    R2 -.->|Fails| A2
    R3 -.->|Fails| A2
    
    style L1 fill:#d1c4e9
    style L2 fill:#ffccbc
    style L3 fill:#c8e6c9
    style R1 fill:#d1c4e9
    style R2 fill:#ffccbc
    style R3 fill:#c8e6c9
    style A1 fill:#ffcdd2
    style A2 fill:#fff9c4
```

---

## Scaling & Load Balancing

```mermaid
graph TB
    subgraph "Incoming Traffic"
        REQ[User Requests]
    end
    
    subgraph "Load Balancer Service"
        LB[streamlit-service<br/>Distributes traffic]
    end
    
    subgraph "Streamlit Pods - Current: 2"
        ST1[Pod 1]
        ST2[Pod 2]
        ST3[Pod 3 - After Scaling]
        ST4[Pod 4 - After Scaling]
        ST5[Pod 5 - After Scaling]
    end
    
    subgraph "Scaling Commands"
        CMD1[kubectl scale deployment<br/>streamlit --replicas=5]
        CMD2[kubectl scale deployment<br/>api --replicas=3]
    end
    
    REQ --> LB
    LB -->|Round Robin| ST1
    LB -->|Round Robin| ST2
    LB -->|Round Robin| ST3
    LB -->|Round Robin| ST4
    LB -->|Round Robin| ST5
    
    CMD1 -.->|Creates| ST3
    CMD1 -.->|Creates| ST4
    CMD1 -.->|Creates| ST5
    
    style REQ fill:#e1f5fe
    style LB fill:#fff9c4
    style ST1 fill:#c8e6c9
    style ST2 fill:#c8e6c9
    style ST3 fill:#c8e6c9,stroke-dasharray: 5 5
    style ST4 fill:#c8e6c9,stroke-dasharray: 5 5
    style ST5 fill:#c8e6c9,stroke-dasharray: 5 5
    style CMD1 fill:#b0bec5
    style CMD2 fill:#b0bec5
```

---

## Deployment Strategies

### Rolling Update Process

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant K8s as Kubernetes
    participant Old as Old Pods (v1)
    participant New as New Pods (v2)
    participant LB as LoadBalancer
    participant User as Users
    
    Note over Old: 2 pods running v1
    Dev->>K8s: kubectl set image deployment/streamlit<br/>streamlit=new-image:v2
    
    K8s->>New: Create 1 new pod (v2)
    New->>K8s: Pod Ready ✓
    K8s->>LB: Add new pod to service
    
    Note over Old,New: 3 pods total (2 old + 1 new)
    
    K8s->>Old: Terminate 1 old pod
    Note over Old: 1 old pod remaining
    
    K8s->>New: Create 1 more new pod (v2)
    New->>K8s: Pod Ready ✓
    K8s->>LB: Add new pod to service
    
    K8s->>Old: Terminate last old pod
    
    Note over New: 2 new pods running v2
    Note over User: Zero downtime! ✓
```

---

## Quick Reference Commands

### View Architecture
```bash
# See all resources in namespace
kubectl get all -n research-dashboard

# Visualize pod distribution
kubectl get pods -n research-dashboard -o wide

# Check services and endpoints
kubectl get svc,ep -n research-dashboard
```

### Monitor Traffic
```bash
# Watch pod logs in real-time
kubectl logs -f -n research-dashboard -l app=streamlit

# Check load balancer
kubectl describe svc streamlit-service -n research-dashboard
```

### Scale Components
```bash
# Scale up
kubectl scale deployment api --replicas=5 -n research-dashboard

# Scale down
kubectl scale deployment streamlit --replicas=1 -n research-dashboard
```

---

## Related Documentation

- **[Deployment Guide](../README.md)** - Setup instructions and operations
- **[Documentation Index](README.md)** - All documentation files
- **[Technical Deep-Dive](DEPLOYMENT_EXPLAINED.md)** - Architecture and networking details

---

**Navigation**: [↑ Main README](../README.md) | [Documentation Index](README.md) | [Deployment Explained](DEPLOYMENT_EXPLAINED.md)

---

*Generated for Research Dashboard - Kubernetes Deployment*
