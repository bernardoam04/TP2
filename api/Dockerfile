# API Container - Flask REST API Server
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application
COPY app.py .

# Set environment variables with defaults
# These can be overridden when running the container
ENV MODEL_PATH=/models/recommendation_model.pkl
ENV CHECK_MODEL_INTERVAL=5
ENV SERVER_VERSION=1.0
ENV HOST=0.0.0.0
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Create directory for models (will be mounted as volume)
RUN mkdir -p /models

# Expose port 5000 for Flask
EXPOSE 5000

# Run the Flask application when container starts
# Note: Using 0.0.0.0 to accept connections from outside the container
CMD ["python", "app.py"]
