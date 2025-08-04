# Logzilla Documentation Server - Docker Setup

This Docker setup runs the MCP Documentation Server with the following configuration:

## Features

- **Server Name**: logzilla-docs-server  
- **Description**: logzilla documentation
- **Transport**: HTTP
- **Host**: 127.0.0.1 (mapped from container)
- **Port**: 8008
- **Python Files Included**:
  - `bm25_search.py` - BM25 keyword search functionality
  - `document_cache.py` - Document caching and loading
  - `models.py` - Data models and request/response schemas
  - `search_tools.py` - Integrated search tools
  - `server.py` - Main MCP server implementation
  - `vector_search.py` - Vector similarity search

## Quick Start

1. **Build and run the service**:
   ```bash
   cd model-context-protocol/docs-server/docker
   docker-compose up --build
   ```

2. **Access the server**:
   - Server endpoint: http://127.0.0.1:8008
   - Help page: http://127.0.0.1:8008/help
   - MCP endpoint: http://127.0.0.1:8008/logzilla-docs-server/mcp

3. **Background mode**:
   ```bash
   docker-compose up -d --build
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f logzilla-docs-server
   ```

5. **Stop the service**:
   ```bash
   docker-compose down
   ```

## Directory Structure

```
docker/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Build optimization
├── README.md               # This file
└── logs/                   # Container logs (created at runtime)
```

## Volume Mounts

- `../docs:/app/docs:ro` - Documentation files (read-only)
- `./logs:/app/logs` - Application logs

## Configuration

The server runs with these exact parameters as specified:
```bash
python server.py --transport http --host 0.0.0.0 --port 8008 -n logzilla-docs-server --description "logzilla documentation"
```

## Health Check

The container includes a health check that verifies the server is responding:
- **Endpoint**: http://localhost:8008/help
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 60 seconds

## Customization

To modify the server configuration, edit the `command` section in `docker-compose.yml` or adjust the environment variables as needed.
