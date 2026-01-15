# Zebo Application - Deployment Guide

## 📋 Overview

Zebo is a CrewAI-powered application with FastAPI endpoints, now ready for Kubernetes deployment with proper health checks.

## 🚀 Available Endpoints

### Core Endpoints
- `GET /` - Root endpoint, returns status message
- `POST /run` - Run CrewAI flow with optional sentence count

### Health Check Endpoints (for Kubernetes)
- `GET /health` - Liveness probe (checks if app is alive)
- `GET /ready` - Readiness probe (checks if app is ready to serve traffic)

## 🏃 Running Locally

### Option 1: Using UV (Recommended)
```bash
cd zebo
uv sync
uv run uvicorn zebo.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Docker
```bash
cd zebo
docker build -t zebo-app:local .
docker run -p 8000:8000 zebo-app:local
```

### Option 3: Using Docker Compose
```bash
cd zebo
docker-compose up
```

## 🧪 Testing Endpoints

```bash
# Make the test script executable
chmod +x test_endpoints.sh

# Test locally
./test_endpoints.sh http://localhost:8000

# Test deployed service (replace with your LoadBalancer IP)
./test_endpoints.sh http://EXTERNAL_IP
```

### Manual Testing
```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Ready check
curl http://localhost:8000/ready

# Run CrewAI flow
curl -X POST http://localhost:8000/run \
  -H 'Content-Type: application/json' \
  -d '{"sentence_count": 3}'
```

## 🐳 Building for GKE

### Step 1: Configure Docker for Artifact Registry
```bash
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

### Step 2: Build and Tag
```bash
cd zebo

# Build the image
docker build -t asia-south1-docker.pkg.dev/zebraan-gcp-zebo-dev/zebo-registry/zebo-app:latest .

# Or with a specific tag
docker build -t asia-south1-docker.pkg.dev/zebraan-gcp-zebo-dev/zebo-registry/zebo-app:v1.0.0 .
```

### Step 3: Push to Artifact Registry
```bash
docker push asia-south1-docker.pkg.dev/zebraan-gcp-zebo-dev/zebo-registry/zebo-app:latest
```

### Step 4: Get SHA for Kubernetes
```bash
# Get the image digest
docker inspect asia-south1-docker.pkg.dev/zebraan-gcp-zebo-dev/zebo-registry/zebo-app:latest \
  --format='{{index .RepoDigests 0}}'

# Or use git commit SHA
git rev-parse --short HEAD
# Update kubernetes/overlays/dev/kustomization.yaml with this SHA
```

## 📦 Deploying to GKE

### Prerequisites
```bash
# Get cluster credentials
gcloud container clusters get-credentials dev-gke-cluster \
  --region asia-south1 \
  --project zebraan-gcp-zebo-dev
```

### Deploy
```bash
cd ../zebo-infra/kubernetes/overlays/dev

# Apply the manifests
kubectl apply -k .

# Check deployment status
kubectl get pods -l app=zebo
kubectl get svc zebo-service-dev
```

### Monitor Deployment
```bash
# Watch pods
kubectl get pods -w

# Check logs
kubectl logs -f -l app=zebo

# Check health probes
kubectl describe pod -l app=zebo | grep -A 10 "Liveness\|Readiness"
```

## 🔍 Troubleshooting

### Pods Not Starting
```bash
# Check pod events
kubectl describe pod -l app=zebo

# Check logs
kubectl logs -l app=zebo --tail=100

# Common issues:
# - Image pull errors: Check Artifact Registry permissions
# - Health check failures: Verify /health and /ready endpoints work
# - Resource limits: Check if pod is OOMKilled
```

### Health Check Failures
The application includes these endpoints for Kubernetes probes:

- **Liveness Probe** (`/health`): Checked every 10s after 60s initial delay
  - If fails 5 times consecutively → Pod is restarted
  
- **Readiness Probe** (`/ready`): Checked every 10s after 30s initial delay
  - If fails → Pod removed from service endpoints (no traffic)

```bash
# Test health endpoints locally first
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Test in pod
kubectl exec -it <pod-name> -- curl http://localhost:8000/health
```

### Image Pull Issues
```bash
# Create image pull secret if needed
kubectl create secret docker-registry artifact-registry-secret \
  --docker-server=asia-south1-docker.pkg.dev \
  --docker-username=_json_key \
  --docker-password="$(cat ~/key.json)" \
  --docker-email=your-email@example.com

# Verify secret
kubectl get secret artifact-registry-secret

# Uncomment imagePullSecrets in deployment.yaml if needed
```

## 🔧 Configuration

### Environment Variables
Current environment variable (can be extended):
- `ENVIRONMENT`: Set to "development" in dev overlay

### Adding New Environment Variables
Edit `kubernetes/overlays/dev/patch-deployment.yaml`:
```yaml
env:
- name: ENVIRONMENT
  value: "development"
- name: YOUR_NEW_VAR
  value: "your-value"
```

### Using Secrets
For sensitive data, use Kubernetes secrets:
```bash
# Create secret
kubectl create secret generic zebo-secrets \
  --from-literal=api-key=your-secret-key

# Reference in deployment
env:
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: zebo-secrets
      key: api-key
```

## 📊 API Documentation

Once deployed, FastAPI provides automatic documentation:
- Swagger UI: `http://<external-ip>/docs`
- ReDoc: `http://<external-ip>/redoc`

## 🎯 Next Steps

1. ✅ Health endpoints added (`/health`, `/ready`)
2. ✅ Dockerfile configured for GKE
3. ✅ Test script created
4. 🔲 Build and push Docker image
5. 🔲 Deploy to GKE
6. 🔲 Test via LoadBalancer IP
7. 🔲 Set up CI/CD with GitHub Actions

## 📝 Notes

- The application runs on port 8000
- Dockerfile uses `uv` for fast dependency management
- Health checks are configured for Kubernetes probes
- CrewAI flow can be triggered via POST /run endpoint
