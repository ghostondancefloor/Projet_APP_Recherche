# 📊 Monitoring Stack - Prometheus + Grafana

This directory contains the Kubernetes manifests for deploying a complete monitoring solution for the Research Dashboard application.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Components](#components)
- [Accessing Dashboards](#accessing-dashboards)
- [Available Metrics](#available-metrics)
- [Alerting](#alerting)
- [Troubleshooting](#troubleshooting)

---

## Overview

The monitoring stack provides:
- **Real-time metrics** collection from all services
- **Pre-built dashboards** for FastAPI and MongoDB
- **Alerting rules** for critical conditions
- **15-day data retention** for historical analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Streamlit   │    │   FastAPI    │    │   MongoDB    │       │
│  │   (2 pods)   │───▶│   (2 pods)   │───▶│   (1 pod)    │       │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘       │
│                             │ /metrics          │               │
│                             ▼                   ▼               │
│                    ┌────────────────┐   ┌────────────────┐      │
│                    │  Prometheus    │◀──│ MongoDB        │      │
│                    │  (scrapes)     │   │ Exporter:9216  │      │
│                    └────────┬───────┘   └────────────────┘      │
│                             │                                   │
│                             ▼                                   │
│                    ┌────────────────┐                           │
│                    │    Grafana     │                           │
│                    │  (visualize)   │                           │
│                    └────────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Kubernetes Deployment

```bash
# Navigate to monitoring directory
cd k8s/monitoring

# Make deploy script executable
chmod +x deploy-monitoring.sh

# Deploy the monitoring stack
./deploy-monitoring.sh
```

### Docker Compose (Local Development)

```bash
# Start all services including monitoring
docker-compose up -d

# Access services:
# - Grafana:    http://localhost:3000
# - Prometheus: http://localhost:9090
```

## Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Prometheus** | Metrics collection & storage | 9090 |
| **Grafana** | Visualization & dashboards | 3000 |
| **MongoDB Exporter** | Export MongoDB metrics | 9216 |

### Files in this Directory

```
monitoring/
├── namespace.yaml              # Monitoring namespace (if separate)
├── rbac.yaml                   # ServiceAccount & permissions
├── secrets.yaml                # Grafana credentials
├── prometheus-configmap.yaml   # Prometheus scrape configuration
├── prometheus-deployment.yaml  # Prometheus StatefulSet & Service
├── grafana-configmap.yaml      # Grafana datasources config
├── grafana-deployment.yaml     # Grafana Deployment & Service
├── mongodb-exporter.yaml       # MongoDB metrics exporter
├── alerting-rules.yaml         # Prometheus alerting rules
├── deploy-monitoring.sh        # Deployment script
└── README.md                   # This file
```

## Accessing Dashboards

### Grafana

| Setting | Value |
|---------|-------|
| **URL** | http://localhost:3000 |
| **Username** | `admin` |
| **Password** | `admin123` (change in production!) |

#### Pre-configured Dashboards

1. **FastAPI Dashboard** - API metrics
   - Request rate by endpoint
   - Response time percentiles (P50, P90, P95, P99)
   - Error rates (4xx, 5xx)
   - Request duration histogram

2. **MongoDB Dashboard** - Database metrics
   - Current connections
   - Operations per second (queries, inserts, updates, deletes)
   - Memory usage (resident, virtual)
   - Connection pool status

### Prometheus

| Setting | Value |
|---------|-------|
| **URL** | http://localhost:9090 |
| **Auth** | None (internal only) |

Use the Prometheus UI to:
- Check target health at `/targets`
- Run ad-hoc PromQL queries
- View alerting rules at `/alerts`

### Port Forwarding (Kubernetes)

If using NodePort or ClusterIP services:

```bash
# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n research-dashboard

# Grafana
kubectl port-forward svc/grafana-service 3000:3000 -n research-dashboard
```

## Available Metrics

### FastAPI Metrics

| Metric | Description |
|--------|-------------|
| `http_requests_total` | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Request duration histogram |
| `http_requests_in_progress` | Current in-flight requests |

#### Example PromQL Queries

```promql
# Request rate per second
rate(http_requests_total[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# Requests by endpoint
sum(rate(http_requests_total[5m])) by (handler)
```

### MongoDB Metrics

| Metric | Description |
|--------|-------------|
| `mongodb_up` | MongoDB instance availability |
| `mongodb_ss_connections` | Connection statistics |
| `mongodb_ss_opcounters` | Operation counters (query, insert, update, delete) |
| `mongodb_ss_mem_resident` | Resident memory usage |
| `mongodb_ss_mem_virtual` | Virtual memory usage |

#### Example PromQL Queries

```promql
# Current connections
mongodb_ss_connections{conn_type="current"}

# Query operations per second
rate(mongodb_ss_opcounters{type="query"}[5m])

# Memory usage in bytes
mongodb_ss_mem_resident * 1024 * 1024
```

## Alerting

### Configured Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `HighErrorRate` | Error rate > 5% for 5m | Critical |
| `HighResponseTime` | P95 latency > 2s for 5m | Warning |
| `APIDown` | API unreachable for 1m | Critical |
| `MongoDBDown` | MongoDB unreachable for 1m | Critical |
| `MongoDBHighConnections` | Connections > 80% for 5m | Warning |
| `PodRestartLoop` | Pod restarts > 3/hour | Warning |

### Setting Up Alert Notifications

To receive alerts via Slack, email, etc., you need to configure Alertmanager. Add to your deployment:

```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'
    route:
      receiver: 'slack-notifications'
    receivers:
      - name: 'slack-notifications'
        slack_configs:
          - channel: '#alerts'
            send_resolved: true
```

## Troubleshooting

### Prometheus Targets Not Showing

1. Check if services are running:
   ```bash
   kubectl get pods -n research-dashboard
   ```

2. Verify service discovery:
   ```bash
   kubectl get endpoints -n research-dashboard
   ```

3. Check Prometheus logs:
   ```bash
   kubectl logs -l app=prometheus -n research-dashboard
   ```

### No Metrics in Grafana

1. Verify Prometheus datasource:
   - Go to Grafana → Settings → Data sources
   - Click "Test" on Prometheus datasource

2. Check if metrics exist in Prometheus:
   - Open Prometheus UI → Graph
   - Try query: `up`

### MongoDB Exporter Not Working

1. Check MongoDB connectivity:
   ```bash
   kubectl logs -l app=mongodb-exporter -n research-dashboard
   ```

2. Verify MongoDB URI in exporter config

### Common Issues

| Issue | Solution |
|-------|----------|
| "No data" in Grafana | Wait 1-2 minutes for metrics to populate |
| Prometheus target "DOWN" | Check pod logs and network policies |
| Grafana login fails | Reset password or check secrets |
| High memory usage | Adjust retention period or add resource limits |

---

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [MongoDB Exporter](https://github.com/percona/mongodb_exporter)
