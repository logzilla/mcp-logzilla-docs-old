# MCP Documentation Server - Docker Guide

This comprehensive Docker guide covers containerized deployment and development workflows for the MCP Documentation Server.

## 🐳 Overview

The MCP Documentation Server provides full Docker support with:
- **Simple development setup** with compose.yml
- **Production-ready configurations** with health checks and restart policies
- **Volume strategies** for documentation and data persistence
- **Development workflows** with hot reload capabilities
- **Production deployment** patterns for scalable setups

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
      # Optional: Mount model cache to persist models between container rebuilds
      # - ./model_cache:/root/.cache/huggingface:rw
    environment:
      # MCP server configuration
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8008
      - MCP_SERVER_NAME=logzilla-docs-server
      - MCP_DESCRIPTION=logzilla documentation
      # Optional: Additional MCP settings
      - MCP_DOCS_PATH=/app/docs
      - MCP_DEVICE=auto
      # Optional: Enable debug logging
      - PYTHONUNBUFFERED=1
    command: >
      python server.py 
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
- **Logs**: Stored in `./logs` directory
- **Network**: Custom network `logzilla-docs-network`
- **Health Check**: Uses `/help` endpoint on port `8008`

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

Run development mode:
```bash
# Start development environment
docker-compose -f compose.yml -f compose.dev.yml up --build

# Code changes will be reflected when you restart the container
```

### Production Configuration

Create a production override file `compose.prod.yml`:

```yaml
# compose.prod.yml
services:
  logzilla-docs-server:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: production
    container_name: logzilla-docs-server-prod
    ports:
      - "0.0.0.0:8008:8008"  # Expose to all interfaces for production
    volumes:
      # Production documentation mount
      - /var/lib/company-docs:/app/docs:ro
      - ./logs:/app/logs
      - docs-cache:/app/cache
    environment:
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8008
      - MCP_SERVER_NAME=logzilla-docs-server
      - MCP_DESCRIPTION=company documentation
      - MCP_DOCS_PATH=/app/docs
      - MCP_DEVICE=auto
      - PYTHONUNBUFFERED=1
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8008/help"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"

volumes:
  docs-cache:
    driver: local
```

Deploy production:
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
# Build development image
docker build --target development -t mcp-docs-server:dev -f docker/Dockerfile .

# Build production image
docker build --target production -t mcp-docs-server:prod -f docker/Dockerfile .

# Test production image with current settings
docker run --rm -p 127.0.0.1:8008:8008 \
  -e MCP_TRANSPORT=http \
  -e MCP_PORT=8008 \
  -e MCP_SERVER_NAME=test-server \
  -v ./logzilla-docs:/app/docs:ro \
  mcp-docs-server:prod

# Test connectivity
curl http://127.0.0.1:8008/help
```

## 🏗️ Production Deployment Strategies

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
