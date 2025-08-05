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

# Create a startup script
RUN echo '#!/bin/bash\n\
if [ ! -d "/app/chroma_db/chroma.sqlite3" ]; then\n\
    echo "ChromaDB not found. Initializing with sample data..."\n\
    if [ -f "/app/doctors_data.json" ]; then\n\
        python create_embeddings.py\n\
    else\n\
        echo "Warning: doctors_data.json not found. Generate it first with generate_doctor_data.py"\n\
    fi\n\
fi\n\
\n\
echo "Starting SmartDoctors API..."\n\
python api_server.py' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]