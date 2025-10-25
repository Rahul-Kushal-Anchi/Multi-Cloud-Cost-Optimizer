# AWS Cost Optimizer - Multi-stage Dockerfile
# Production-ready container for web and API services

# Build stage
FROM node:18-alpine AS web-builder

WORKDIR /app/web

# Copy package files
COPY web-app/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY web-app/ .

# Build the application
RUN npm run build

# Python API stage
FROM python:3.11-slim AS api-builder

WORKDIR /app/api

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source code
COPY api/ .

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NODE_ENV=production
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set up directories
WORKDIR /app
RUN mkdir -p /app/web /app/api /var/log/supervisor

# Copy Python dependencies from builder
COPY --from=api-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=api-builder /usr/local/bin /usr/local/bin

# Copy built web application
COPY --from=web-builder /app/web/dist /app/web/dist
COPY --from=web-builder /app/web/node_modules /app/web/node_modules
COPY --from=web-builder /app/web/package*.json /app/web/

# Copy API source code
COPY api/ /app/api/

# Copy configuration files
COPY deployment/docker/nginx.conf /etc/nginx/nginx.conf
COPY deployment/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY deployment/docker/entrypoint.sh /entrypoint.sh

# Set permissions
RUN chmod +x /entrypoint.sh
RUN chown -R appuser:appuser /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 3000

# Switch to app user
USER appuser

# Set working directory
WORKDIR /app

# Start services
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
