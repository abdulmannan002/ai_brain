# AI Brain Vault - AWS EKS Deployment Guide

This guide provides step-by-step instructions for deploying the AI Brain Vault application to AWS EKS (Elastic Kubernetes Service).

## Prerequisites

### AWS Account Setup
- AWS CLI configured with appropriate permissions
- EKS cluster with version 1.24+
- kubectl configured to access your EKS cluster
- Docker installed locally

### Required AWS Services
- EKS (Elastic Kubernetes Service)
- RDS (PostgreSQL)
- S3 (for file storage)
- MSK (Managed Streaming for Kafka)
- Route 53 (DNS)
- CloudFront (CDN)
- Certificate Manager (SSL)

## Step 1: Infrastructure Setup

### 1.1 Create EKS Cluster

```bash
# Create EKS cluster
eksctl create cluster \
  --name ai-brain-vault \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --name ai-brain-vault --region us-east-1
```

### 1.2 Set up RDS PostgreSQL

```bash
# Create RDS subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name ai-brain-vault-db \
  --db-subnet-group-description "AI Brain Vault Database" \
  --subnet-ids subnet-12345678 subnet-87654321

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier ai-brain-vault-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 20 \
  --db-subnet-group-name ai-brain-vault-db \
  --vpc-security-group-ids sg-12345678
```

### 1.3 Create S3 Bucket

```bash
# Create S3 bucket for audio files
aws s3 mb s3://ai-brain-vault-audio --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ai-brain-vault-audio \
  --versioning-configuration Status=Enabled

# Configure CORS
aws s3api put-bucket-cors \
  --bucket ai-brain-vault-audio \
  --cors-configuration file://cors.json
```

### 1.4 Set up MSK Kafka Cluster

```bash
# Create MSK cluster
aws kafka create-cluster \
  --cluster-name ai-brain-vault-kafka \
  --kafka-version 3.4.0 \
  --number-of-broker-nodes 3 \
  --broker-node-group-info file://broker-node-group-info.json \
  --encryption-info file://encryption-info.json
```

## Step 2: Kubernetes Setup

### 2.1 Install Required Tools

```bash
# Install Helm
curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/

# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.12.0 \
  --set installCRDs=true

# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### 2.2 Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace ai-brain-vault

# PostgreSQL secret
kubectl create secret generic postgres-secret \
  --namespace ai-brain-vault \
  --from-literal=username=postgres \
  --from-literal=password=YourSecurePassword123! \
  --from-literal=database=ai_brain_vault

# AWS credentials secret
kubectl create secret generic aws-secret \
  --namespace ai-brain-vault \
  --from-literal=access-key-id=YOUR_AWS_ACCESS_KEY \
  --from-literal=secret-access-key=YOUR_AWS_SECRET_KEY

# xAI API secret
kubectl create secret generic xai-secret \
  --namespace ai-brain-vault \
  --from-literal=api-key=YOUR_XAI_API_KEY

# Auth0 secret
kubectl create secret generic auth0-secret \
  --namespace ai-brain-vault \
  --from-literal=domain=your-domain.auth0.com \
  --from-literal=audience=your-audience \
  --from-literal=secret=YOUR_AUTH0_SECRET \
  --from-literal=issuer-base-url=https://your-domain.auth0.com \
  --from-literal=client-id=YOUR_CLIENT_ID \
  --from-literal=client-secret=YOUR_CLIENT_SECRET

# Grafana secret
kubectl create secret generic grafana-secret \
  --namespace ai-brain-vault \
  --from-literal=admin-password=YourGrafanaPassword123!
```

## Step 3: Build and Push Docker Images

### 3.1 Configure Docker for ECR

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Create ECR repositories
aws ecr create-repository --repository-name ai-brain-backend
aws ecr create-repository --repository-name ai-brain-frontend
```

### 3.2 Build and Push Images

```bash
# Set ECR registry
export ECR_REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t $ECR_REGISTRY/ai-brain-backend:latest .
docker push $ECR_REGISTRY/ai-brain-backend:latest

# Build and push frontend
cd ../frontend
docker build -t $ECR_REGISTRY/ai-brain-frontend:latest .
docker push $ECR_REGISTRY/ai-brain-frontend:latest
```

## Step 4: Deploy Application

### 4.1 Update Image References

Update the Kubernetes deployment files to use your ECR images:

```yaml
# In k8s/backend-deployment.yaml and k8s/frontend-deployment.yaml
image: $ECR_REGISTRY/ai-brain-backend:latest
image: $ECR_REGISTRY/ai-brain-frontend:latest
```

### 4.2 Apply Kubernetes Manifests

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/monitoring/

# Wait for deployments
kubectl rollout status deployment/ai-brain-backend -n ai-brain-vault
kubectl rollout status deployment/ai-brain-frontend -n ai-brain-vault
```

## Step 5: DNS and SSL Configuration

### 5.1 Configure Route 53

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name ai-brain-vault.com \
  --caller-reference $(date +%s)

# Add A record pointing to your ingress
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_HOSTED_ZONE_ID \
  --change-batch file://route53-changes.json
```

### 5.2 SSL Certificate

```bash
# Create SSL certificate
aws acm request-certificate \
  --domain-name ai-brain-vault.com \
  --subject-alternative-names www.ai-brain-vault.com \
  --validation-method DNS

# Add DNS validation records to Route 53
# (Follow AWS console instructions)
```

## Step 6: Monitoring Setup

### 6.1 Deploy Monitoring Stack

```bash
# Deploy Prometheus and Grafana
kubectl apply -f k8s/monitoring/

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n ai-brain-vault
# Open http://localhost:3000
# Default credentials: admin / YourGrafanaPassword123!
```

### 6.2 Configure Alerts

```bash
# Create alert rules
kubectl apply -f k8s/monitoring/alert-rules.yaml

# Configure notification channels in Grafana
# (Email, Slack, PagerDuty, etc.)
```

## Step 7: CI/CD Pipeline

### 7.1 GitHub Actions Setup

1. Add repository secrets in GitHub:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `KUBE_CONFIG_PRODUCTION` (base64 encoded kubeconfig)
   - `ECR_REGISTRY`

2. Update `.github/workflows/ci-cd.yml` with your ECR registry

3. Push to main branch to trigger deployment

### 7.2 Environment Variables

Set these environment variables in your deployment:

```bash
# Backend environment variables
kubectl set env deployment/ai-brain-backend \
  -n ai-brain-vault \
  DB_HOST=your-rds-endpoint \
  DB_PORT=5432 \
  DB_NAME=ai_brain_vault \
  AWS_REGION=us-east-1 \
  S3_BUCKET=ai-brain-vault-audio \
  KAFKA_BOOTSTRAP_SERVERS=your-msk-endpoint:9092

# Frontend environment variables
kubectl set env deployment/ai-brain-frontend \
  -n ai-brain-vault \
  BACKEND_URL=https://api.ai-brain-vault.com \
  AUTH0_BASE_URL=https://ai-brain-vault.com
```

## Step 8: Verification

### 8.1 Health Checks

```bash
# Check pod status
kubectl get pods -n ai-brain-vault

# Check services
kubectl get svc -n ai-brain-vault

# Check ingress
kubectl get ingress -n ai-brain-vault

# Test endpoints
curl -I https://ai-brain-vault.com
curl -I https://api.ai-brain-vault.com/health
```

### 8.2 Load Testing

```bash
# Install k6
curl -L https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz | tar xz
sudo mv k6-v0.45.0-linux-amd64/k6 /usr/local/bin/

# Run load test
k6 run load-test.js
```

## Troubleshooting

### Common Issues

1. **Pod CrashLoopBackOff**
   ```bash
   kubectl logs -f deployment/ai-brain-backend -n ai-brain-vault
   kubectl describe pod -l app=ai-brain-backend -n ai-brain-vault
   ```

2. **Database Connection Issues**
   ```bash
   # Check RDS security groups
   aws rds describe-db-instances --db-instance-identifier ai-brain-vault-db
   
   # Test connection from pod
   kubectl exec -it deployment/ai-brain-backend -n ai-brain-vault -- nc -zv your-rds-endpoint 5432
   ```

3. **Ingress Issues**
   ```bash
   # Check ingress controller logs
   kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
   
   # Check ingress status
   kubectl describe ingress ai-brain-vault-ingress -n ai-brain-vault
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX CONCURRENTLY idx_ideas_user_timestamp ON ideas(user_id, timestamp);
   CREATE INDEX CONCURRENTLY idx_ideas_content_fts ON ideas USING gin(to_tsvector('english', content));
   ```

2. **Kubernetes Resource Limits**
   ```yaml
   resources:
     requests:
       memory: "512Mi"
       cpu: "250m"
     limits:
       memory: "1Gi"
       cpu: "500m"
   ```

3. **Horizontal Pod Autoscaling**
   ```bash
   # Check HPA status
   kubectl get hpa -n ai-brain-vault
   
   # Scale manually if needed
   kubectl scale deployment ai-brain-backend --replicas=5 -n ai-brain-vault
   ```

## Cost Optimization

### AWS Cost Management

1. **Use Spot Instances**
   ```bash
   # Update node group to use spot instances
   eksctl create nodegroup \
     --cluster ai-brain-vault \
     --name spot-workers \
     --spot \
     --instance-types t3.medium,t3.large
   ```

2. **Enable Auto Scaling**
   ```bash
   # Configure cluster autoscaler
   helm install cluster-autoscaler autoscaler/cluster-autoscaler \
     --set autoDiscovery.clusterName=ai-brain-vault \
     --set awsRegion=us-east-1
   ```

3. **Monitor Costs**
   ```bash
   # Set up AWS Cost Explorer alerts
   aws ce create-anomaly-monitor \
     --anomaly-monitor file://cost-monitor.json
   ```

## Security Best Practices

1. **Network Security**
   - Use private subnets for RDS and MSK
   - Configure security groups with minimal access
   - Enable VPC Flow Logs

2. **Secrets Management**
   - Use AWS Secrets Manager for sensitive data
   - Rotate credentials regularly
   - Enable audit logging

3. **Compliance**
   - Enable AWS Config rules
   - Set up CloudTrail logging
   - Implement backup and disaster recovery

## Support

For deployment issues:
- Check the troubleshooting section above
- Review Kubernetes and AWS logs
- Contact the development team
- Open an issue on GitHub

---

**Next Steps**: After successful deployment, proceed to user onboarding and feature rollout planning. 