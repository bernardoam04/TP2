# Kubernetes Deployment Configuration

Kubernetes manifests for deploying the Playlist Recommendation System.

## Files Overview

- **pvc.yaml** - PersistentVolumeClaim for shared model storage
- **deployment.yaml** - API server deployment (2 replicas)
- **service.yaml** - Service to expose the API
- **ml-job.yaml** - Job for ML model generation

## Pre-Deployment Checklist

### 1. Update Configuration Values

Before deploying, update these placeholders:

**service.yaml:**
- Update `nodePort` with your allocated port number from the course website

**ml-job.yaml:**
- Change job name for each new run (e.g., `ml-job-v1`, `ml-job-v2`, `ml-job-ds2`)
- Update `DATASET_PATH` when switching datasets

**deployment.yaml:**
- Update `SERVER_VERSION` when deploying new code

### 2. Upload Dataset to Cluster

SSH to the cluster and copy datasets to the PersistentVolume:

```bash
# SSH to cluster
ssh bernardomiranda@pugna.snes.2advanced.dev -p 51927 -i ~/.ssh/cloudvm_2023028021_ed25519

# Navigate to your PV directory
cd /home/bernardomiranda/project2-pv

# Create data subdirectory
mkdir -p data

# Copy datasets from cluster location
cp /home/datasets/spotify/2023_spotify_ds1.csv data/
cp /home/datasets/spotify/2023_spotify_ds2.csv data/
cp /home/datasets/spotify/2023_spotify_songs.csv data/
```

## Manual Deployment (Testing)

Before setting up ArgoCD, test manually:

```bash
# Apply PersistentVolumeClaim
kubectl -n bernardomiranda apply -f pvc.yaml

# Verify PVC is bound
kubectl -n bernardomiranda get pvc

# Apply API deployment and service
kubectl -n bernardomiranda apply -f deployment.yaml
kubectl -n bernardomiranda apply -f service.yaml

# Check deployment status
kubectl -n bernardomiranda get deployments
kubectl -n bernardomiranda get pods
kubectl -n bernardomiranda get services

# Run ML job to generate model
kubectl -n bernardomiranda apply -f ml-job.yaml

# Check job status
kubectl -n bernardomiranda get jobs
kubectl -n bernardomiranda logs -l component=ml

# Test the API
# Get the cluster-ip from the service
CLUSTER_IP=$(kubectl -n bernardomiranda get service playlist-recommender-service -o jsonpath='{.spec.clusterIP}')
wget --server-response \
    --output-document response.out \
    --header='Content-Type: application/json' \
    --post-data '{"songs": ["HUMBLE.", "DNA."]}' \
    http://$CLUSTER_IP:5000/api/recommend

cat response.out
```

## ArgoCD Deployment

### 1. Push to Git Repository

Create a Git repository and push the k8s directory:

```bash
# Create GitHub repository (e.g., playlist-recommender-k8s)
# Then:
git init
git add .
git commit -m "Add Kubernetes configurations"
git remote add origin https://github.com/GITHUB_USERNAME/playlist-recommender-k8s.git
git push -u origin main
```

### 2. Update argocd/application.yaml

Replace `GITHUB_USERNAME` with your actual GitHub username in `argocd/application.yaml`.

### 3. Deploy via ArgoCD

```bash
# SSH to cluster
ssh bernardomiranda@pugna.snes.2advanced.dev -p 51927

# Login to ArgoCD (first time only)
argocd login localhost:31443 --username bernardomiranda --password YOUR_PASSWORD --insecure

# Change password (first time only)
argocd account update-password

# Create application
kubectl apply -f argocd/application.yaml

# OR use CLI:
argocd app create playlist-recommender-bernardomiranda \
      --repo https://github.com/GITHUB_USERNAME/playlist-recommender-k8s.git \
      --path k8s \
      --project bernardomiranda-project \
      --dest-namespace bernardomiranda \
      --dest-server https://kubernetes.default.svc \
      --sync-policy auto

# Check application status
argocd app get playlist-recommender-bernardomiranda

# Sync if needed
argocd app sync playlist-recommender-bernardomiranda
```

## Updating the Deployment

### Update Code Version

1. Build and push new Docker image with new tag:
   ```bash
   docker build -t bernardoam04/playlist-recommender-api:0.2 api/
   docker push bernardoam04/playlist-recommender-api:0.2
   ```

2. Update `deployment.yaml`:
   - Change `image: bernardoam04/playlist-recommender-api:0.2`
   - Change `SERVER_VERSION: "0.2"`

3. Commit and push to Git
   ```bash
   git add k8s/deployment.yaml
   git commit -m "Update API to version 0.2"
   git push
   ```

4. ArgoCD will automatically detect and deploy the change!

### Update Dataset

1. Copy new dataset to PV:
   ```bash
   ssh bernardomiranda@pugna.snes.2advanced.dev -p 51927
   cp /home/datasets/spotify/2023_spotify_ds2.csv /home/bernardomiranda/project2-pv/data/
   ```

2. Update `ml-job.yaml`:
   - Change job name: `name: ml-job-ds2-v1`
   - Change dataset: `DATASET_PATH: "/data/2023_spotify_ds2.csv"`

3. Commit and push to Git
   ```bash
   git add k8s/ml-job.yaml
   git commit -m "Update ML job to use dataset 2"
   git push
   ```

4. ArgoCD will automatically run the new job!

### Update Deployment Configuration (e.g., replicas)

1. Edit `deployment.yaml`:
   ```yaml
   replicas: 3  # Changed from 2 to 3
   ```

2. Commit and push to Git
   ```bash
   git add k8s/deployment.yaml
   git commit -m "Scale API to 3 replicas"
   git push
   ```

3. ArgoCD will automatically scale!

## Useful Commands

```bash
# View all resources
kubectl -n bernardomiranda get all

# View logs
kubectl -n bernardomiranda logs -l app=bernardomiranda-playlist-recommender
kubectl -n bernardomiranda logs -l component=api
kubectl -n bernardomiranda logs -l component=ml

# Describe pod (for troubleshooting)
kubectl -n bernardomiranda describe pod <pod-name>

# Get shell in pod
kubectl -n bernardomiranda exec -it <pod-name> -- bash

# Delete resources
kubectl -n bernardomiranda delete -f deployment.yaml
kubectl -n bernardomiranda delete -f service.yaml
kubectl -n bernardomiranda delete job ml-job-v1

# Force sync in ArgoCD
argocd app sync playlist-recommender-bernardomiranda --force

# View ArgoCD app logs
argocd app logs playlist-recommender-bernardomiranda
```

## Troubleshooting

### Pod stuck in ImagePullBackOff
- Check Docker image name and tag in deployment.yaml
- Verify images are public on DockerHub
- Check: `kubectl -n bernardomiranda describe pod <pod-name>`

### Pod stuck in CrashLoopBackOff
- Check logs: `kubectl -n bernardomiranda logs <pod-name>`
- Check if model file exists in PV
- Verify environment variables

### PVC not binding
- Check PVC selector matches PV labels
- Verify storage class name
- Check: `kubectl -n bernardomiranda describe pvc project2-pv-bernardomiranda`

### ML Job not completing
- Check logs: `kubectl -n bernardomiranda logs -l component=ml`
- Verify dataset exists in /home/bernardomiranda/project2-pv/data/
- Check resource limits if OOMKilled

### ArgoCD not syncing
- Check repo URL is correct and public
- Verify path to k8s directory
- Check ArgoCD app status: `argocd app get playlist-recommender-bernardomiranda`
- Force sync: `argocd app sync playlist-recommender-bernardomiranda`
