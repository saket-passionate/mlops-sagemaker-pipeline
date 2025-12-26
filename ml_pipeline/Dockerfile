# Use an ARM64-compatible Python base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements if any
COPY requirements.txt .
RUN pip install -r requirements.txt || echo "No requirements.txt found, continuing..."

WORKDIR /opt/ml/processing/input/

CMD ["python3", "/opt/ml/processing/input/code/preprocess.py"]

