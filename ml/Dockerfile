# ML Container - Playlist Recommendation Model Generator
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the model generator script
COPY model_generator.py .

# Set environment variables with defaults
# These can be overridden when running the container
ENV DATASET_PATH=/data/2023_spotify_ds1.csv
ENV MODEL_OUTPUT_PATH=/models/recommendation_model.pkl
ENV MIN_SUPPORT=0.05
ENV MIN_CONFIDENCE=0.5
ENV SAMPLE_SIZE=10000
ENV PYTHONUNBUFFERED=1

# Create directories for data and models (will be mounted as volumes)
RUN mkdir -p /data /models

# Run the model generator when container starts
CMD ["python", "model_generator.py"]
