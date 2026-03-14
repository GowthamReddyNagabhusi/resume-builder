# Cloud Deployment Guide

This guide covers deploying Resume Builder to AWS, Azure, or other cloud providers.

## Architecture Overview

### Production Stack

```
                    Internet
                       ↓
            ┌───────────────────┐
            │  CloudFront/CDN   │
            └───────────────────┘
                       ↓
    ┌──────────────────────────────────┐
    │   Load Balancer / API Gateway   │
    └──────────────────────────────────┘
                       ↓
        ┌──────────────────────────────┐
        │  ECS/App Service Cluster     │
        │  (Running Backend & Frontend)│
        │  Auto-scaling enabled       │
        └──────────────────────────────┘
                       ↓
    ┌────────────────────────────────────┐
    │   RDS PostgreSQL / Cloud SQL       │
    └────────────────────────────────────┘
    
    ┌────────────────────────────────────┐
    │   ElastiCache Redis / Cloud Cache  │
    └────────────────────────────────────┘
    
    ┌────────────────────────────────────┐
    │   S3 / Blob Storage (Generated)    │
    │   Resumes, user uploads            │
    └────────────────────────────────────┘
```

## AWS Deployment

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Docker image pushed to ECR
- RDS instance created
- S3 bucket for storage

### Step 1: Create RDS Database

```bash
# Using AWS CLI
aws rds create-db-instance \
  --db-instance-identifier resume-builder-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username resumeadmin \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --publicly-accessible false \
  --vpc-security-group-ids sg-xxxxx

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier resume-builder-db \
  --query 'DBInstances[0].Endpoint.Address'
```

### Step 2: Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id resume-builder-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --engine-version 7.0
```

### Step 3: Push Docker Images to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name resume-builder-backend
aws ecr create-repository --repository-name resume-builder-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -f infra/docker/backend.dockerfile -t resume-builder-backend .
docker tag resume-builder-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-builder-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-builder-backend:latest

# Build and push frontend
docker build -f infra/docker/frontend.dockerfile -t resume-builder-frontend .
docker tag resume-builder-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-builder-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/resume-builder-frontend:latest
```

### Step 4: Create ECS Cluster and Services

```bash
# Create cluster
aws ecs create-cluster --cluster-name resume-builder

# Create task definitions (see templates in infra/ecs/)
# Define backend and frontend tasks

# Create services
aws ecs create-service \
  --cluster resume-builder \
  --service-name resume-builder-backend \
  --task-definition resume-builder-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=8000
```

### Step 5: Setup CloudFront CDN

```bash
# Create distribution
aws cloudfront create-distribution \
  --distribution-config file://infra/cloudfront-config.json
```

## Azure Deployment

### Prerequisites

- Azure Subscription
- Azure CLI installed and configured
- Container Registry setup
- App Service Plan

### Step 1: Create Resource Group

```bash
az group create --name resumebuilder --location eastus
```

### Step 2: Create Container Registry

```bash
az acr create --resource-group resumebuilder \
  --name resumebuilder --sku Basic

# Get ACR login server
az acr show --resource-group resumebuilder \
  --name resumebuilder --query loginServer -o tsv
```

### Step 3: Push Docker Images

```bash
# Login to ACR
az acr login --name resumebuilder

# Build and push
az acr build --registry resumebuilder \
  --image resume-builder-backend:latest \
  --file infra/docker/backend.dockerfile .

az acr build --registry resumebuilder \
  --image resume-builder-frontend:latest \
  --file infra/docker/frontend.dockerfile .
```

### Step 4: Create App Service

```bash
# Create App Service Plan
az appservice plan create --name resumebuilder-plan \
  --resource-group resumebuilder --sku S1 --is-linux

# Create backend App Service
az webapp create --resource-group resumebuilder \
  --plan resumebuilder-plan --name resumebuilder-api \
  --deployment-container-image-name resumebuilder.azurecr.io/resume-builder-backend:latest \
  --docker-custom-id-user <admin-username> \
  --docker-custom-id-pass <admin-password>

# Create frontend App Service
az webapp create --resource-group resumebuilder \
  --plan resumebuilder-plan --name resumebuilder-app \
  --deployment-container-image-name resumebuilder.azurecr.io/resume-builder-frontend:latest
```

### Step 5: Create Database

```bash
az postgres flexible-server create \
  --resource-group resumebuilder \
  --name resumebuilder-db \
  --admin-user resumeadmin \
  --admin-password YourSecurePassword \
  --sku-name Standard_B1ms \
  --tier Burstable
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (EKS, AKS, GKE, or local)
- kubectl configured
- Helm (optional but recommended)

### Step 1: Create Namespace

```bash
kubectl create namespace resume-builder
kubectl config set-context --current --namespace=resume-builder
```

### Step 2: Create Secrets

```bash
kubectl create secret generic resume-builder-secrets \
  --from-literal=database-url=postgresql://user:pass@postgres:5432/resume_builder \
  --from-literal=secret-key=your-secret-key \
  --from-literal=openai-api-key=sk-...

kubectl create secret docker-registry acr-secret \
  --docker-server=resumebuilder.azurecr.io \
  --docker-username=username \
  --docker-password=password
```

### Step 3: Apply Kubernetes Manifests

```bash
# Deploy PostgreSQL
kubectl apply -f infra/kubernetes/postgres-statefulset.yaml

# Deploy Redis
kubectl apply -f infra/kubernetes/redis-deployment.yaml

# Deploy Backend
kubectl apply -f infra/kubernetes/backend-deployment.yaml

# Deploy Frontend
kubectl apply -f infra/kubernetes/frontend-deployment.yaml

# Create Services
kubectl apply -f infra/kubernetes/services.yaml

# Create Ingress
kubectl apply -f infra/kubernetes/ingress.yaml
```

### Step 4: Check Status

```bash
kubectl get pods
kubectl get svc
kubectl describe ingress resume-builder
```

## CI/CD Pipeline Setup

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -f infra/docker/backend.dockerfile -t backend .
        docker build -f infra/docker/frontend.dockerfile -t frontend .
    
    - name: Push to ECR
      env:
        AWS_REGION: us-east-1
      run: |
        aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
        docker tag backend $ECR_REGISTRY/resume-builder-backend:latest
        docker push $ECR_REGISTRY/resume-builder-backend:latest
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster resume-builder \
          --service resume-builder-backend \
          --force-new-deployment
```

## Monitoring & Logging

### CloudWatch / Azure Monitor

```bash
# View logs
aws logs tail /ecs/resume-builder-backend --follow

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-resume-builder \
  --metric-name CPUUtilization \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### Application Insights

```bash
# Enable Application Insights
az monitor app-insights create \
  --resource-group resumebuilder \
  --app-insights-resource-name resumebuilder-insights
```

## Database Backups

### AWS RDS

```bash
# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier resume-builder-db \
  --db-snapshot-identifier resume-builder-backup-$(date +%Y%m%d)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier resume-builder-db-restored \
  --db-snapshot-identifier resume-builder-backup-20240115
```

### Azure Database

```bash
# Create backup
az postgres flexible-server backup create \
  --resource-group resumebuilder \
  --server-name resumebuilder-db \
  --backup-name manual-backup-$(date +%Y%m%d)
```

## Scaling

### Auto-scaling Configuration

```yaml
# AWS ECS auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/resume-builder/resume-builder-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --service-namespace ecs \
  --resource-id service/resume-builder/resume-builder-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Security Best Practices

1. **Network Security**
   - Use VPC/VNets
   - Security groups/NSGs
   - Private subnets for databases
   - NAT Gateway for outbound traffic

2. **Secrets Management**
   - AWS Secrets Manager / Azure Key Vault
   - Never hardcode credentials
   - Rotate API keys regularly

3. **SSL/TLS**
   - Use ACM certificates (AWS) or App Service Certificates (Azure)
   - Enable HTTPS everywhere
   - Use security headers

4. **Regular Updates**
   - Keep dependencies updated
   - Regular security patches
   - Monitor CVEs

## Cost Optimization

- Use reserved instances for databases
- Auto-scaling for compute
- CDN caching for static assets
- Monitoring and alerts for cost spikes

---

For Terraform IaC templates, see `infra/terraform/`

For troubleshooting, see specific cloud provider documentation.
