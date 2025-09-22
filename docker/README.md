# MCP Documentation Server - Docker Guide

This comprehensive Docker guide covers containerized deployment and development workflows for the MCP Documentation Server.

## 🐳 Overview

The MCP Documentation Server provides full Docker support with:
- **Simple development setup** with compose.yml
- **Production-ready configurations** with health checks and restart policies
- **Volume strategies** for documentation and data persistence
- **Development workflows** with hot reload capabilities

## 📁 Docker Directory Structure

```
docker/
├── Dockerfile                  # Multi-stage container build
├── compose.yml                 # Main Docker Compose configuration
├── .dockerignore              # Build optimization
├── download_models.py         # Pre-download embedding models
├── logs/                      # Container logs (runtime)
└── README.md                  # This comprehensive guide
```

## 🚀 Quick Start

### Basic Development Setup

```bash
# Clone and navigate to docker directory
cd model-context-protocol/docs-server/docker

# Start with default configuration
docker-compose -f compose.yml up --build

# Access the server
curl http://127.0.0.1:8008/help
```

### Background Mode

```bash
# Start in background
docker-compose -f compose.yml up -d --build

# View logs
docker-compose -f compose.yml logs -f logzilla-docs-server

# Stop the service
docker-compose -f compose.yml down
```

## 🔧 Configuration

### Current Default Configuration (compose.yml)

The default compose.yml file is configured as:

```yaml
services:
  logzilla-docs-server:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: logzilla-docs-server
    ports:
      - "127.0.0.1:8008:8008"
    volumes:
      # Mount logzilla production docs directory
      - ../logzilla-docs:/app/docs:ro
      # Optional: Mount logs directory
      - ./logs:/app/logs
      # Mount embeddings directory for persistence
      - ../embeddings:/app/embeddings:rw
      # Optional: Mount model cache to persist models between container rebuilds
      - ./model_cache:/root/.cache/huggingface:rw
    environment:
      # MCP server configuration
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8008
      - MCP_SERVER_NAME=logzilla-docs-server
      - MCP_DESCRIPTION=logzilla documentation
      # Model and embedding settings
      - MCP_MODEL=thenlper/gte-large
      - MCP_EMBEDDING_PATH=/app/embeddings
      - MCP_DEVICE=auto
      - MCP_EMBEDDING_NAME=logzilla_md_docs
      - MCP_DEFAULT_VERSION=latest
      # Optional: Enable debug logging
      - PYTHONUNBUFFERED=1
    command: >
      python server.py 
      --transport http 
      --host 0.0.0.0 
      --port 8008 
      --server-name logzilla-docs-server 
      --description "logzilla documentation"
      --model thenlper/gte-large
      --embedding-path /app/embeddings
      --embedding-name logzilla_md_docs
      --device auto
      --default-version latest 
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8008/help"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  default:
    name: logzilla-docs-network
```

### Key Configuration Details

- **Server Name**: `logzilla-docs-server`
- **Port**: `8008` (bound to `127.0.0.1` only)
- **Transport**: HTTP only
- **Documentation**: Mounted from `../logzilla-docs` (read-only)
- **Embeddings**: Mounted from `../embeddings` (read-write for persistence)
- **Model Cache**: Mounted from `./model_cache` (read-write for model persistence)
- **Embedding Model**: `thenlper/gte-large` (pre-downloaded during build)
- **Device**: `auto` (automatically detects best compute device)
- **Logs**: Stored in `./logs` directory
- **Network**: Custom network `logzilla-docs-network`
- **Health Check**: Uses `/help` endpoint on port `8008`

## 🤖 Model Pre-loading and Dependencies

### Embedding Models

The Docker build process automatically pre-downloads embedding models using `download_models.py`:

- **Default Model**: `thenlper/gte-large` (1024 dimensions, high performance)
- **Fallback Models**: `sentence-transformers/all-MiniLM-L6-v2`, `BAAI/bge-small-en-v1.5`, `sentence-transformers/all-mpnet-base-v2`
- **Cache Location**: `/root/.cache/huggingface` (persisted via volume mount)

### Updated Dependencies

The `requirements.txt` includes all necessary dependencies:

```txt
# Core MCP Framework
mcp>=1.0.0

# Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Configuration
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
PyYAML>=6.0.0                 # YAML parsing for alias configuration

# Search Engine
faiss-cpu>=1.7.4              # Vector similarity search
sentence-transformers>=2.2.2  # Embedding models
numpy>=1.24.0                 # Numerical operations
rank-bm25>=0.2.2              # BM25 keyword search
nltk>=3.8.1                   # Natural language processing
beautifulsoup4>=4.12.0        # HTML parsing

# System Monitoring
psutil>=5.9.0                 # System statistics
```

## 🔧 Environment Variables

All server configuration can be controlled via environment variables with the `MCP_` prefix:

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| `MCP_TRANSPORT` | `stdio` | Transport protocol: `stdio`, `http`, or `https` |
| `MCP_HOST` | `localhost` | Server host address (HTTP/HTTPS only) |
| `MCP_PORT` | `8000` | Server port number (HTTP/HTTPS only) |
| `MCP_SERVER_NAME` | `docs-server` | Name identifier for the MCP server |
| `MCP_DESCRIPTION` | `company documentation` | Human-readable server description |
| `MCP_MODEL` | `thenlper/gte-large` | Embedding model name |
| `MCP_EMBEDDING_PATH` | `./embeddings` | Path to embedding files |
| `MCP_EMBEDDING_NAME` | `docs_embeddings` | Name identifier for embedding files |
| `MCP_DEVICE` | `auto` | Compute device: `cpu`, `cuda`, `mps`, `auto` |
| `MCP_DEFAULT_VERSION` | `latest` | Default documentation version |
| `MCP_ALIAS_FILE` | - | Path to version aliases YAML file |
| `MCP_SSL_CERT_PATH` | - | SSL certificate path (HTTPS only) |
| `MCP_SSL_KEY_PATH` | - | SSL private key path (HTTPS only) |

### Example Environment Configuration

```bash
# Production HTTP server
export MCP_TRANSPORT=http
export MCP_HOST=0.0.0.0
export MCP_PORT=8008
export MCP_SERVER_NAME=company-docs-server
export MCP_DESCRIPTION="Company Documentation Server"
export MCP_MODEL=thenlper/gte-large
export MCP_EMBEDDING_PATH=/app/embeddings
export MCP_DEVICE=auto

# Start server
python server.py
```

## 📖 Usage

### Server Access

```bash
# Server endpoint
curl http://127.0.0.1:8008/help

# MCP endpoint (for MCP clients)
http://127.0.0.1:8008/logzilla-docs-server/mcp

# Check server status
docker-compose -f compose.yml ps

# View server logs
docker-compose -f compose.yml logs logzilla-docs-server
```

### Customizing Documentation Path

The compose.yml is currently configured to use the `logzilla-docs` directory:

```yaml
volumes:
  # Current production docs directory
  - ../logzilla-docs:/app/docs:ro
  
  # To use a different directory, change to:
  # - /path/to/your/documentation:/app/docs:ro
  # Example: - /home/user/my-docs:/app/docs:ro
  # Example: - /var/www/company-docs:/app/docs:ro
```


### Development with Hot Reload

Create a development override file `compose.dev.yml`:

```yaml
# compose.dev.yml
services:
  logzilla-docs-server:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: development
    volumes:
      # Bind mount source code for development
      - ..:/app:delegated
      - ../logzilla-docs:/app/docs:ro
      - ./logs:/app/logs
    environment:
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8008
      - MCP_SERVER_NAME=logzilla-docs-server-dev
      - MCP_DESCRIPTION=logzilla documentation (development)
      - MCP_DOCS_PATH=/app/docs
      - MCP_DEVICE=cpu
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
    command: >
      python server.py
    restart: "no"  # Don't restart automatically during development
```


```

Execution examples:

```bash
# Start production deployment
docker-compose -f compose.yml -f compose.prod.yml up -d --build

# Monitor production logs
docker-compose -f compose.yml -f compose.prod.yml logs -f
```

## 🔄 Development Workflows

### Local Development

```bash
# Start development environment
docker-compose -f compose.yml up --build

# Code changes require container restart
docker-compose -f compose.yml restart logzilla-docs-server

# Access container shell for debugging
docker-compose -f compose.yml exec logzilla-docs-server bash

# Run tests inside container (from main directory)
docker-compose -f compose.yml exec logzilla-docs-server python tests/test_search_routines.py
docker-compose -f compose.yml exec logzilla-docs-server python tests/test_mcp_responses.py
```

### Development with Custom Documentation

```bash
# Mount your local documentation directory
docker run -it --rm \
  -p 127.0.0.1:8008:8008 \
  -v /path/to/your/docs:/app/docs:ro \
  -v $(pwd)/logs:/app/logs \
  -e MCP_TRANSPORT=http \
  -e MCP_PORT=8008 \
  -e MCP_SERVER_NAME=my-docs-server \
  --name my-docs-server \
  mcp-docs-server:latest
```

### Building and Testing Images

```bash
# Build image
docker build --target development -t mcp-docs-server:dev -f docker/Dockerfile .

# Test image with current settings
docker run --rm -p 127.0.0.1:8008:8008 \
  -e MCP_TRANSPORT=http \
  -e MCP_PORT=8008 \
  -e MCP_SERVER_NAME=test-server \
  -v ./logzilla-docs:/app/docs:ro \
  mcp-docs-server:prod

# Test connectivity
curl http://127.0.0.1:8008/help
```

## 🏗️ Deployment Strategies

### Single Container Deployment

```bash
# Basic production deployment
docker run -d \
  --name logzilla-docs-server \
  --restart unless-stopped \
  -p 0.0.0.0:8008:8008 \
  -v /var/lib/company-docs:/app/docs:ro \
  -v /var/log/mcp-server:/app/logs \
  -e MCP_TRANSPORT=http \
  -e MCP_PORT=8008 \
  -e MCP_SERVER_NAME=company-docs-server \
  -e MCP_DESCRIPTION="Company Documentation" \
  -e MCP_DOCS_PATH=/app/docs \
  --memory=2g \
  --cpus=1.0 \
  mcp-docs-server:prod
```

## 🔒 Security Considerations

### Container Security

```bash
# Run with security options
docker run -d \
  --name logzilla-docs-server \
  --restart unless-stopped \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --cap-add CHOWN \
  --cap-add SETGID \
  --cap-add SETUID \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /var/run \
  -p 127.0.0.1:8008:8008 \
  mcp-docs-server:prod
```

### Network Security

```yaml
# Restrict network access
services:
  logzilla-docs-server:
    # ... other configuration
    ports:
      - "127.0.0.1:8008:8008"  # Only bind to localhost
    networks:
      - internal
    
networks:
  internal:
    driver: bridge
    internal: true  # No external access
```

## 📊 Monitoring and Logging

### Container Monitoring

```bash
# Monitor resource usage
docker stats logzilla-docs-server

# Check container health
docker inspect logzilla-docs-server | grep -A 10 "Health"

# View detailed logs
docker-compose -f compose.yml logs -f --tail=100 logzilla-docs-server
```

### Log Management

```yaml
# Enhanced logging configuration
services:
  logzilla-docs-server:
    # ... other configuration
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
        labels: "service=docs-server,environment=production"
```

### Health Monitoring

```bash
# Health check endpoint
curl http://127.0.0.1:8008/help

# Container health status
docker inspect logzilla-docs-server --format='{{.State.Health.Status}}'

# Automated health monitoring script
#!/bin/bash
while true; do
  if curl -f http://127.0.0.1:8008/help > /dev/null 2>&1; then
    echo "$(date): Server is healthy"
  else
    echo "$(date): Server is unhealthy"
  fi
  sleep 30
done
```

## 🔧 Advanced Configuration

### Custom Nginx Reverse Proxy

```nginx
# nginx/nginx-lb.conf
events {
    worker_connections 1024;
}

http {
    upstream docs_backend {
        server docs-server-1:8008;
        server docs-server-2:8008;
        server docs-server-3:8008;
    }

    server {
        listen 80;
        server_name docs.company.com;

        location / {
            proxy_pass http://docs_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Health check
            proxy_connect_timeout 5s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        location /help {
            access_log off;
            proxy_pass http://docs_backend/help;
        }
    }
}
```

## 🐛 Troubleshooting

### Common Docker Issues

#### Container Won't Start
```bash
# Check container logs
docker logs logzilla-docs-server

# Test server health
curl http://127.0.0.1:8008/help

# Check container status
docker ps -a

# Inspect container configuration
docker inspect logzilla-docs-server

# Check resource usage
docker stats logzilla-docs-server
```

#### Port Binding Issues
```bash
# Check what's using port 8008
sudo netstat -tulpn | grep :8008

# Use different port
docker run -p 127.0.0.1:8009:8008 mcp-docs-server

# Check Docker port mapping
docker port logzilla-docs-server
```

#### Volume Mount Problems
```bash
# Check volume mounts
docker inspect logzilla-docs-server | grep -A 10 "Mounts"

# Test volume accessibility
docker run --rm \
  -v /path/to/docs:/test:ro \
  alpine ls -la /test

# Fix permissions
sudo chown -R 1000:1000 /path/to/docs
```

#### Service Communication Issues
```bash
# Test container networking
docker network ls
docker network inspect logzilla-docs-network

# Check DNS resolution inside container
docker exec logzilla-docs-server nslookup google.com

# Test internal connectivity
docker exec logzilla-docs-server curl http://localhost:8008/help
```

### Performance Optimization

#### Memory Optimization
```bash
# Monitor memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Limit memory
docker run --memory=1g --memory-swap=2g mcp-docs-server

# Optimize for memory-constrained environments
docker run \
  -e MCP_DEVICE=cpu \
  -e MCP_MAX_FILE_SIZE=5242880 \
  mcp-docs-server
```

#### CPU Optimization
```bash
# Limit CPU usage
docker run --cpus=0.5 mcp-docs-server

# Check CPU usage
docker exec logzilla-docs-server top

# Enable GPU support (if available)
docker run --gpus all \
  -e MCP_DEVICE=cuda \
  mcp-docs-server
```

## 📚 Quick Reference

### Essential Commands

```bash
# Start server
docker-compose -f compose.yml up -d

# View logs
docker-compose -f compose.yml logs -f logzilla-docs-server

# Stop server
docker-compose -f compose.yml down

# Check status
curl http://127.0.0.1:8008/help

# Access container
docker-compose -f compose.yml exec logzilla-docs-server bash

# Restart service
docker-compose -f compose.yml restart logzilla-docs-server

# View resource usage
docker stats logzilla-docs-server
```

### Key URLs

- **Server Help**: http://127.0.0.1:8008/help
- **MCP Endpoint**: http://127.0.0.1:8008/logzilla-docs-server/mcp
- **Container Logs**: `docker-compose -f compose.yml logs logzilla-docs-server`

### Configuration Files

- **Main**: `compose.yml` - Default configuration
- **Development**: `compose.dev.yml` - Development overrides
- **Production**: `compose.prod.yml` - Production configuration
- **HA Setup**: `compose.ha.yml` - High availability

## 📝 Testing with Production Docs

**Important**: To run tests against the server with your production documentation:

```bash
# Start the Docker container
cd docker
docker-compose -f compose.yml up -d
cd ..  # Return to main directory - REQUIRED for Python imports

# Run tests (must be from main directory for Python imports to work)
python tests/test_mcp_responses.py
python tests/test_search_routines.py  
python tests/test_http.py
python tests/test_stdio.py
```

You must start the server in order for this one:
```
python tests/test_http_client.py
```

The server will serve your `logzilla-docs` content at:
- **Help page**: http://127.0.0.1:8008/help  
- **MCP endpoint**: http://127.0.0.1:8008/logzilla-docs-server/mcp

---

This Docker guide provides comprehensive coverage of containerized deployment strategies for the MCP Documentation Server. For general server configuration and usage, refer to the main README.md.
