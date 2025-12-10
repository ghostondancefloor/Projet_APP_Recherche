# Kubernetes Documentation Index

This directory contains comprehensive documentation for the Research Dashboard Kubernetes deployment.

## Documentation Structure

| Document | Description | Audience |
|----------|-------------|----------|
| **[Main README](../README.md)** | Quick start, deployment guide, operations, troubleshooting | All users |
| **[Deployment Explained](DEPLOYMENT_EXPLAINED.md)** | Technical deep-dive: architecture, networking, multi-host setup | Developers, students |
| **[Architecture Diagrams](ARCHITECTURE.md)** | Visual system design with Mermaid diagrams | Architects, visual learners |

## Quick Links

### Getting Started
- [Prerequisites](../README.md#prerequisites)
- [Quick Start Deployment](../README.md#quick-start)
- [Network Access Setup](../README.md#network-access)

### Understanding the System
- [Architecture Overview](DEPLOYMENT_EXPLAINED.md#architecture-overview)
- [Multi-Host Networking](DEPLOYMENT_EXPLAINED.md#multi-host-networking)
- [Visual Diagrams](ARCHITECTURE.md)

### Operations
- [Viewing Resources](../README.md#viewing-resources)
- [Scaling Applications](../README.md#scaling)
- [Monitoring & Debugging](../README.md#monitoring--debugging)

### Advanced Topics
- [Testing Kubernetes Features](DEPLOYMENT_EXPLAINED.md#testing-kubernetes-features)
- [Production Scaling](DEPLOYMENT_EXPLAINED.md#scaling-to-production)
- [Troubleshooting Guide](../README.md#troubleshooting)

## File Descriptions

### Main README.md
The primary documentation file containing:
- Prerequisites and installation requirements
- Automated deployment with `deploy.sh`
- Manual deployment step-by-step guide
- Operations: scaling, monitoring, logging
- Network access configuration
- Troubleshooting common issues
- Command reference and best practices

### DEPLOYMENT_EXPLAINED.md
Technical deep-dive explaining:
- Complete architecture overview with diagram
- Deployment components (namespace, storage, pods, services)
- Multi-host networking mechanisms (NodePort, kube-proxy, iptables)
- Key Kubernetes concepts (pods, replicasets, services)
- Production scaling considerations
- Practical testing procedures

### ARCHITECTURE.md
Visual documentation featuring:
- Complete system architecture diagram
- Network architecture and traffic flow
- Deployment flow diagrams
- Data flow visualization
- Component relationships

## Version Information

- **Version**: v1.1-multi-host
- **Last Updated**: December 2025
- **Kubernetes Version**: 1.28+
- **Docker Desktop**: 4.25+

---

**[← Back to k8s Directory](../)**
