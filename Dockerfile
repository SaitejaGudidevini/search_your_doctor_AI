# Multi-stage build for SmartDoctors
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create directory for ChromaDB
RUN mkdir -p /app/chroma_db

# Expose the port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false

# Create a startup script with proper initialization order
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== SmartDoctors Docker Initialization ==="\n\
\n\
# Step 1: Pre-download the model by importing rag_system\n\
echo "Step 1: Downloading and caching SentenceTransformer model..."\n\
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer(\"sentence-transformers/all-MiniLM-L6-v2\"); print(\"Model downloaded successfully\")"\n\
\n\
# Step 2: Check if doctors_data.json exists\n\
if [ ! -f "/app/doctors_data.json" ]; then\n\
    echo "Step 2: Generating doctors data..."\n\
    python generate_doctor_data.py\n\
else\n\
    echo "Step 2: doctors_data.json found"\n\
fi\n\
\n\
# Step 3: Initialize ChromaDB with embeddings\n\
echo "Step 3: Initializing ChromaDB..."\n\
python create_embeddings.py\n\
\n\
# Step 4: Start the API server\n\
echo "Step 4: Starting SmartDoctors API..."\n\
python api_server.py' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]