# Playlist Recommendation System - DevOps Project

A microservice-based playlist recommendation system built for cloud deployment with CI/CD automation.

## Project Structure

```
├── ml/                      # ML Model Generator Component
│   ├── model_generator.py   # FP-Growth based model training
│   └── requirements.txt     # ML dependencies
├── api/                     # REST API Server Component
│   ├── app.py              # Flask server with /api/recommend endpoint
│   └── requirements.txt    # API dependencies
├── client/                  # CLI Client Component
│   ├── client.py           # Command-line test client
│   └── requirements.txt    # Client dependencies
├── k8s/                     # Kubernetes Configuration (TODO)
├── argocd/                  # ArgoCD Configuration (TODO)
├── models/                  # Generated ML models
└── venv/                    # Python virtual environment

## Components

### 1. ML Model Generator (ml/)

Generates playlist recommendations using the FP-Growth algorithm for frequent itemset mining.

**Features:**
- Processes Spotify playlist datasets
- Generates association rules (IF song A THEN recommend song B)
- Configurable via environment variables
- Optimized for memory efficiency with sampling

**Configuration:**
- `DATASET_PATH`: Path to CSV dataset (default: ../2023_spotify_ds1.csv)
- `MODEL_OUTPUT_PATH`: Where to save model (default: ../models/recommendation_model.pkl)
- `MIN_SUPPORT`: Minimum support threshold (default: 0.05 = 5%)
- `MIN_CONFIDENCE`: Minimum confidence threshold (default: 0.5 = 50%)
- `SAMPLE_SIZE`: Number of playlists to sample (default: 10000, set to 0 for all)

**Usage:**
```bash
source venv/bin/activate
cd ml
python model_generator.py
```

### 2. REST API Server (api/)

Flask-based REST API that serves playlist recommendations.

**Features:**
- POST `/api/recommend` - Get song recommendations
- GET `/health` - Health check endpoint
- GET `/` - API information
- Automatic model reloading when file changes
- Background monitoring thread

**Request Format:**
```json
POST /api/recommend
{
  "songs": ["Song Name 1", "Song Name 2"]
}
```

**Response Format:**
```json
{
  "songs": ["Recommended Song 1", "Recommended Song 2", ...],
  "version": "1.0",
  "model_date": "2025-11-10T19:47:48.001485",
  "input_songs": ["Song Name 1", "Song Name 2"],
  "num_recommendations": 10
}
```

**Configuration:**
- `MODEL_PATH`: Path to model file (default: ../models/recommendation_model.pkl)
- `CHECK_MODEL_INTERVAL`: Seconds between model checks (default: 5)
- `SERVER_VERSION`: API version string (default: "1.0")
- `HOST`: Bind address (default: 127.0.0.1)
- `PORT`: Port number (default: 5000)

**Usage:**
```bash
source venv/bin/activate
cd api
python app.py
```

### 3. CLI Client (client/)

Command-line client for testing the API.

**Features:**
- Send recommendations requests with song names
- Display formatted results
- Health check support
- JSON output mode

**Usage:**
```bash
source venv/bin/activate
python client/client.py "Song 1" "Song 2" [options]

Options:
  --url URL          API endpoint URL
  --timeout SECONDS  Request timeout
  --health          Check API health first
  --json            Output raw JSON
```

**Examples:**
```bash
# Basic usage
python client/client.py "HUMBLE." "DNA."

# With custom URL
python client/client.py "Song 1" --url http://localhost:5000/api/recommend

# With health check
python client/client.py "Song 1" "Song 2" --health

# JSON output
python client/client.py "Song 1" --json
```

## Local Testing

### Setup

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r ml/requirements.txt -r api/requirements.txt -r client/requirements.txt
```

3. **Generate ML model:**
```bash
cd ml
python model_generator.py
cd ..
```

4. **Start API server:**
```bash
cd api
python app.py &
cd ..
```

5. **Test with client:**
```bash
python client/client.py "HUMBLE." "DNA."
```

### Test Results

The system successfully:
- ✅ Generates 15,775 association rules from 2,262 playlists
- ✅ Loads model in Flask API (619.52 KB)
- ✅ Serves recommendations via REST API
- ✅ Automatically reloads model when file changes
- ✅ Handles requests with CLI client

**Example recommendations for ["HUMBLE.", "DNA."]:**
1. Mask Off
2. Bad and Boujee (feat. Lil Uzi Vert)
3. XO TOUR Llif3
4. Bounce Back
5. goosebumps
6. Congratulations
7. T-Shirt
8. Slippery (feat. Gucci Mane)
9. iSpy (feat. Lil Yachty)
10. Broccoli (feat. Lil Yachty)

## Next Steps (Remote Deployment)

### Phase 2: Containerization
- [ ] Create Dockerfile for ML container
- [ ] Create Dockerfile for API container
- [ ] Test locally with Docker
- [ ] Push images to DockerHub/Quay.io

### Phase 3: Kubernetes & ArgoCD
- [ ] Create PersistentVolumeClaim YAML
- [ ] Create Deployment YAML
- [ ] Create Service YAML
- [ ] Create Job YAML for ML container
- [ ] Configure ArgoCD application
- [ ] Set up automatic sync and pruning

### Phase 4: Testing & Documentation
- [ ] Test code version updates
- [ ] Test deployment configuration updates
- [ ] Test dataset updates (ds1 → ds2)
- [ ] Measure deployment times
- [ ] Document CI/CD findings in PDF

## Dataset

The project uses Spotify playlist datasets:
- **2023_spotify_ds1.csv** - 241,457 tracks in 2,262 playlists (initial training)
- **2023_spotify_ds2.csv** - Similar dataset for model updates
- **2023_spotify_songs.csv** - 7,000 songs for testing

## Technology Stack

- **ML**: Python, FP-Growth (fpgrowth-py), Pandas, NumPy
- **API**: Flask, Pickle for model serialization
- **Client**: Python Requests library
- **Containers**: Docker (TODO)
- **Orchestration**: Kubernetes (TODO)
- **CD**: ArgoCD (TODO)

## Model Details

**Algorithm:** FP-Growth (Frequent Pattern Growth)
- Efficiently mines frequent itemsets from transaction data
- Generates association rules (IF-THEN relationships)
- Uses compact FP-tree data structure

**Parameters:**
- Minimum Support: 5% (songs must appear together in 5% of playlists)
- Minimum Confidence: 50% (rules must be correct 50% of the time)

**Performance:**
- Model generation: ~5-10 seconds for 10,000 playlists
- Model size: 619.52 KB
- Rules generated: 15,775 association rules
- API response time: <100ms

## Notes for Cluster Deployment

When deploying to the cluster, configure:
- Username/namespace for Kubernetes
- Port number (from allocation table)
- PersistentVolume paths
- Docker registry credentials
- Git repository URL for ArgoCD

Model will use shared PersistentVolume at: `/home/<username>/project2-pv2`
