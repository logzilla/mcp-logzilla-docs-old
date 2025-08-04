# MCP Documentation Server

A sophisticated Model Context Protocol (MCP) server implementation providing intelligent documentation search and retrieval capabilities. Built with FastMCP and featuring hybrid search technology combining BM25 keyword search with FAISS vector embeddings for superior search accuracy.

## 🚀 Overview

The MCP Documentation Server is designed to integrate with MCP-compatible AI assistants and applications, providing them with powerful access to your documentation through natural language queries. It serves as a bridge between AI models and your documentation repositories, enabling context-aware assistance and knowledge retrieval.

## ✨ Features

### Search & Retrieval
- **Hybrid Search**: BM25 keyword + semantic vector search via FAISS with sentence transformers
- **Document Indexing**: Automatic indexing of markdown files with metadata extraction
- **Smart Chunking**: Intelligent document segmentation for optimal search results
- **Search Analytics**: Query performance metrics and result scoring
- **Content Filtering**: Configurable file type and size restrictions

### Server Capabilities  
- **Multiple Transports**: stdio (for direct MCP integration), HTTP, and HTTPS
- **Streaming Support**: Efficient large-payload transfer with HTTP streaming
- **SSL/TLS Encryption**: Full HTTPS support with configurable certificates
- **CORS Support**: Cross-origin resource sharing for web applications
- **Health Checks**: Built-in health monitoring endpoints

### Authentication & Security
- **OAuth Integration**: Support for OAuth 2.0 token introspection
- **API Key Authentication**: Simple bearer token authentication
- **Path Security**: Protection against directory traversal attacks
- **File Size Limits**: Configurable maximum file sizes
- **Read-Only Access**: Secure read-only file system access

### Development & Operations
- **Docker Support**: Complete containerization with multi-stage builds
- **Comprehensive Testing**: Full test suite including unit, integration, and HTTP tests
- **Structured Logging**: Detailed logging with configurable levels
- **Environment Configuration**: Flexible `.env` file and environment variable support
- **Development Tools**: Hot reload, debugging support, and development certificates

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **System Requirements**: 2GB RAM minimum (4GB recommended for large document sets)
- **Dependencies**: See `requirements.txt` for complete list
- **Optional**: Docker and Docker Compose for containerized deployment

## 🚀 Quick Start

### Option 1: Direct Python Installation

```bash
# Clone repository and navigate to docs-server
cd model-context-protocol/docs-server

# Install dependencies
pip install -r requirements.txt

# Start the server (HTTP mode on port 8000)  
python server.py --transport http --port 8000 --docs /path/to/your/docs

# Or start in MCP stdio mode (for direct integration)
python server.py --transport stdio --docs /path/to/your/docs
```

### Option 2: Docker (Recommended for Production)

```bash
# Navigate to the docker directory
cd model-context-protocol/docs-server/docker

# Edit compose.yml to point to YOUR documentation directory
# Change: - ../docs:/app/docs:ro
# To: - /path/to/your/documentation:/app/docs:ro

# Start the server
docker-compose up -d

# The server will be available at http://localhost:8000
```

### Documentation Directory Requirements

Your documentation directory should contain:
- Markdown files (`.md`) 
- Organized in any subdirectory structure you prefer
- All files will be automatically indexed and searchable

Example structure:
```
/your/docs/path/
├── getting-started.md
├── api/
│   ├── authentication.md
│   └── endpoints.md
├── guides/
│   └── deployment.md
└── troubleshooting.md
```

## MCP Client Configuration

### Windsurf

In Windsurf, go to "Advanced Settings", then "Cascade", then "Manage 
MCP Servers", then "View raw config". Add the following information
(merge with "mcpServers" if you already have some).

```
{
    "mcpServers": {
      "lzdocs": {
        "serverUrl": "http://127.0.0.1:8008/logzilla-docs-server/mcp",
        "headers": {
          "Content-Type": "application/json"
        }
      }
    }
  }
```

Close the raw JSON tab and go back to the Manage MCPs tab. Click
"refresh" and you should see the `lzdocs` MCP server listed.

### Claude desktop

You must have `npx` on your system, in your PATH. 

1. **Check Node/NPM are installed**
   `node -v`  `npm -v`
   *Why it matters*: **npx** ships with npm ≥ 5.2, which is bundled with every
   modern Node installer (so if those commands work, you already have npx).

2. **Install (or upgrade) Node** if the commands above fail or show an ancient
   version.

   * Download and run the LTS installer from [https://nodejs.org](https://nodejs.org) **or**
   * `winget install OpenJS.NodeJS.LTS`  # Windows 10/11
     *Why it matters*: This gives you the latest stable Node, npm, and npx in one
     shot.

3. **Open a shell** where you want to work.

   * Windows Terminal, PowerShell, or plain **cmd.exe**
   * (Optional) VS Code’s integrated terminal or Git Bash also work fine
     *Why it matters*: npx is just a CLI utility, so any terminal that can see the
     `node` executables on your `PATH` will do.

4. **Run the program with npx**
   `npx <package-name> [args]`
   Example: `npx create-react-app my-app`
   *Why it matters*: npx downloads the package (if you don’t already have it) to
   a temp cache, then immediately runs its CLI entry-point.

5. **Skip the “install? (y/N)” prompt** (npm ≥ 7)
   `npx -y <package-name>`
   *Why it matters*: Great for scripts or CI where you don’t want interactivity.

6. **Troubleshoot common issues**

   * *“‘npx’ is not recognized”*: the Node installer’s **postinstall** step
     didn’t add `%ProgramFiles%\nodejs\` to `PATH`. Log out/in or add it
     manually.
   * *Corporate proxy*:
     `npm config set proxy http://user:pass@proxy:port`
     `npm config set https-proxy http://user:pass@proxy:port`
   * *Firewall blocks downloads*: pre-install the CLI globally:
     `npm i -g <package-name>` and run it normally.
     *Why it matters*: These fixes get you past the usual Windows-specific
     roadblocks.


Once you have Node/NPM installed, in a text editor, open the file 
`C:\Users\your-user-name\AppData\Roaming\Claude\claude_desktop_config.json`.

Either add the following, or merge the "mcpServers" section:
```
{
    "mcpServers": {
        "logzilla-docs": {
            "args": [
                "mcp-remote",
                "http://127.0.0.1:8008/logzilla-docs-server/mcp"
            ],
            "command": "npx"
        }
    }
}
```


## 🔧 Installation

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd model-context-protocol/docs-server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install pytest pytest-asyncio httpx

# Verify installation
python server.py --help
```

### Production Installation

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip build-essential

# Create application directory
sudo mkdir -p /opt/mcp-docs-server
sudo chown $USER:$USER /opt/mcp-docs-server
cd /opt/mcp-docs-server

# Install application
pip install -r requirements.txt --user

# Create systemd service (optional)
sudo cp scripts/mcp-docs-server.service /etc/systemd/system/
sudo systemctl enable mcp-docs-server
sudo systemctl start mcp-docs-server
```

### Docker Installation

```bash
# Build from source
cd model-context-protocol/docs-server
docker build -f docker/Dockerfile -t mcp-docs-server .

# Or use docker-compose
cd docker
docker-compose up -d

# View logs
docker-compose logs -f docs-server
```

## ⚙️ Configuration

The server supports multiple configuration methods with environment variables taking precedence over `.env` files.

### Environment Variables

#### Core Server Settings
```bash
# Transport and Network
export MCP_TRANSPORT="http"              # Transport mode: stdio, http, https
export MCP_HOST="localhost"              # Server bind address (default: localhost)
export MCP_PORT="8000"                   # Server port (default: 8000)
export MCP_SERVER_NAME="docs-server"     # Server identifier (default: docs-server)
export MCP_DESCRIPTION="company documentation"  # Server description

# SSL/TLS Configuration (HTTPS mode)
export MCP_SSL_CERT_PATH="/path/to/cert.pem"    # SSL certificate file path
export MCP_SSL_KEY_PATH="/path/to/key.pem"      # SSL private key file path

# Authentication & Security
export MCP_OAUTH_ENABLED="false"        # Enable OAuth authentication (default: false)
export MCP_RUN_OAUTH_SERVER="false"     # Run standalone OAuth server (default: false)

# Document Management - IMPORTANT: Point to your documentation directory
export MCP_DOCS_PATH="/path/to/your/docs"  # Documentation root directory (default: ./docs)
export MCP_MAX_FILE_SIZE="10485760"     # Maximum file size (10MB)
export MCP_DEVICE="auto"                # Compute device: cpu, cuda, mps, auto, none (default: auto)
```

### Configuration File (.env)

Create a `.env` file in the project root:

```bash
# .env file example
MCP_TRANSPORT=http
MCP_HOST=localhost
MCP_PORT=8000
MCP_DOCS_PATH=/path/to/your/documentation
MCP_DEVICE=auto
MCP_SERVER_NAME=docs-server
MCP_DESCRIPTION="company documentation"

# Real examples:
# MCP_DOCS_PATH=/home/user/my-project/docs
# MCP_DOCS_PATH=/var/www/knowledge-base
# MCP_DOCS_PATH=./company-documentation
```

### SSL/HTTPS Setup

```bash
# Generate SSL certificates (self-signed for development)
openssl genrsa -out server.key 2048
openssl req -new -x509 -key server.key -out server.crt -days 365

# Configure environment
export MCP_SSL_CERT_PATH="server.crt"
export MCP_SSL_KEY_PATH="server.key"
export MCP_PORT="8443"

# Start with HTTPS  
python server.py --transport https --port 8443
```

### Docker Configuration

For Docker deployments, modify `compose.yml`:

```yaml
version: '3.8'
services:
  docs-server:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: docs-server
    ports:
      - "8000:8000"
    volumes:
      # IMPORTANT: Mount YOUR documentation directory here
      - /path/to/your/documentation:/app/docs:ro
      # Example: - /home/user/project-docs:/app/docs:ro
    environment:
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - MCP_DOCS_PATH=/app/docs
      - MCP_DEVICE=auto
      - PYTHONUNBUFFERED=1
```

**Key Points:**
- Replace `/path/to/your/documentation` with your actual documentation directory path
- The `:ro` flag mounts the directory as read-only for security
- The documentation will be available inside the container at `/app/docs`

## 📖 Usage

### Starting the Server

#### Command Line Arguments

```bash
# Basic usage with your documentation directory
python server.py --transport http --port 8000 --docs /path/to/your/docs

# All available options
python server.py \
  --docs /path/to/your/documentation \
  --transport https \
  --host localhost \
  --port 8443 \
  --name "production-docs-server" \
  --description "Production Documentation Server" \
  --device auto \
  --ssl-cert /path/to/cert.pem \
  --ssl-key /path/to/key.pem
```

#### Development Mode
```bash
# Start in development mode with hot reload
python server.py --transport http --port 8000 --device auto

# Start in MCP stdio mode (for direct MCP client integration)  
python server.py --transport stdio

# Start with HTTPS (requires SSL certificates)
python server.py --transport https --port 8443
```

#### Production Mode
```bash
# Production HTTP server
python server.py --transport http --host localhost --port 8000

# Production HTTPS server  
MCP_SSL_CERT_PATH="/etc/ssl/certs/server.crt" \
MCP_SSL_KEY_PATH="/etc/ssl/private/server.key" \
python server.py --transport https --port 8443

# Docker production deployment
docker-compose -f docker/compose.yml up -d
```

### Integration with MCP Clients

#### Claude Desktop Integration
Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "docs-server": {
      "command": "python",
      "args": ["/path/to/docs-server/server.py", "--transport", "stdio"],
      "env": {
        "MCP_DOCS_PATH": "/path/to/your/docs"
      }
    }
  }
}
```

#### Direct HTTP Integration
```bash
# Test server availability
curl http://localhost:8000/help

# List available tools
curl http://localhost:8000/tools/list

# Access documentation catalog
curl http://localhost:8000/resources
```

## 🔧 API Reference

### MCP Resources

#### `docs://document/{document_id}`
Retrieves the full content of a specific document by its relative path.

**Parameters:**
- `document_id`: Relative path to the document from the docs root (e.g., "getting_started.md", "api/reference.md")

**Example Usage:**
```
Resource: docs://document/getting_started.md
Resource: docs://document/api/reference.md
Resource: docs://document/config/guide.md
```

**Response Format:**
Returns the raw markdown content of the specified document with proper formatting preserved.

**OAuth Protected Resource (admin access):**
- `admin://document/{document_id}` - Same functionality with administrative privileges

### MCP Tools

#### `search_for_documents`
Search for documents using query text with metadata results only.

**Parameters:**
- `query` (string, required): Search query text (1-1000 characters)
- `top_k` (integer, default: 10): Maximum number of results to return (1-50)
- `min_quality` (integer, default: 0): Quality cutoff 0-100
- `include_scores` (boolean, default: true): Include detailed scoring information

**Response:**
```json
{
  "status": "success",
  "results": {
  "results": [
    {
        "document_id": "auth/oauth.md",
        "title": "OAuth Authentication", 
        "path": "auth/oauth.md",
        "score": 8.5,
        "modified": "2024-01-15T10:30:00",
        "size": 4096
      }
    ]
  },
  "query": "authentication",
  "total_results": 1
}
```

#### `search_and_retrieve_documents`
Search for documents and retrieve their full content.

**Parameters:**
- `query` (string, required): Search query text (1-1000 characters)
- `top_k` (integer, default: 10): Maximum number of results to return (1-50)
- `min_quality` (integer, default: 0): Quality cutoff 0-100

**Response:**
```json
{
  "status": "success", 
  "results": {
    "results": [
      {
        "document_id": "auth/oauth.md",
        "title": "OAuth Authentication",
        "path": "auth/oauth.md", 
        "score": 8.5,
  "modified": "2024-01-15T10:30:00",
        "size": 4096,
        "content": "# OAuth Authentication\n\nThis document explains..."
      }
    ]
  },
  "query": "authentication",
  "total_results": 1
}
```

#### `health_check`
Check the health status of the documentation server.

**Response:**
```json
{
  "status": "ready",
  "message": "Server ready",
  "documents_loaded": 15,
  "search_tools_available": true,
  "search_engines_ready": true,
  "docs_directory": "./docs",
  "transport": "http",
  "oauth_enabled": false
}
```

#### OAuth Protected Tools (admin access)

When OAuth is enabled, additional administrative tools are available:

- `admin_search_for_documents` - Same as `search_for_documents` with admin privileges
- `admin_health_check` - Enhanced health check with additional server details

## 📁 Project Structure

```
docs-server/
├── server.py                    # Main MCP server implementation (1,238 lines)
├── requirements.txt             # Python dependencies and versions
├── README.md                   # This comprehensive documentation
│
├── Core Components/
│   ├── models.py               # Pydantic data models and schemas
│   ├── search_tools.py         # MCP tools integration layer
│   ├── document_cache.py       # Document caching and metadata
│   ├── bm25_search.py          # BM25 keyword search engine
│   └── vector_search.py        # FAISS vector search with embeddings
│
├── Testing Suite/
│   └── tests/                  # Test suite directory
│       ├── test_mcp_responses.py   # MCP protocol response tests
│       ├── test_http.py            # HTTP endpoint testing
│       ├── test_http_client.py     # HTTP client integration tests
│       ├── test_stdio.py           # stdio transport testing
│       ├── test_search_routines.py # Search functionality tests
│       └── test_mcp_responses.out  # Test output reference
│
├── Docker Environment/
│   ├── docker/
│   │   ├── Dockerfile          # Multi-stage container build
│   │   ├── compose.yml         # Production deployment config
│   │   ├── download_models.py  # Pre-download embedding models
│   │   ├── .dockerignore       # Docker build exclusions
│   │   └── logs/              # Container log directory
│
└── Runtime/
    ├── __pycache__/            # Python bytecode cache
    └── .pytest_cache/          # Pytest cache directory
```

### Component Overview

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **server.py** | Main FastMCP server | Multi-transport support, OAuth, SSL/TLS |
| **search_tools.py** | Search orchestration | Hybrid search, result ranking, analytics |
| **bm25_search.py** | Keyword search | TF-IDF, BM25 scoring, term matching |
| **vector_search.py** | Semantic search | FAISS indexing, sentence transformers |
| **models.py** | Data structures | Pydantic schemas, validation, serialization |
| **document_cache.py** | Performance layer | Metadata caching, file monitoring |

## 🧪 Testing

The project includes a comprehensive test suite covering all major functionality:

### Running Tests

**Important**: All tests must be run from the main project directory so Python can find the library modules.

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests (from main directory)
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories (from main directory)
python tests/test_search_routines.py   # Search functionality
python tests/test_mcp_responses.py     # MCP protocol compliance
python tests/test_http.py              # HTTP endpoints
python tests/test_stdio.py             # stdio transport

# Or use pytest with full paths
pytest tests/test_search_routines.py -v
pytest tests/test_mcp_responses.py -v
pytest tests/test_http.py -v
pytest tests/test_stdio.py -v
```

### Test Categories

#### Unit Tests
- **Search Engine Tests** (`test_search_routines.py`): BM25, vector search, hybrid ranking
- **Document Cache Tests**: Caching behavior, invalidation, performance
- **Model Validation Tests**: Pydantic schema validation, serialization

#### Integration Tests  
- **MCP Protocol Tests** (`test_mcp_responses.py`): Full MCP compliance testing
- **HTTP Client Tests** (`test_http_client.py`): End-to-end HTTP workflows
- **Transport Tests** (`test_stdio.py`, `test_http.py`): Transport layer validation

#### Performance Tests
- **Search Performance**: Query response times, large document sets
- **Concurrent Access**: Multi-client stress testing
- **Memory Usage**: Document caching efficiency

### Manual Testing

#### HTTP Endpoints
```bash
# Health check
curl http://localhost:8000/help

# List tools
curl http://localhost:8000/tools/list

# Test search functionality
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_for_documents",
    "arguments": {
      "query": "authentication",
      "top_k": 5
    }
  }'

# Test with authentication
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:8000/resources
```

#### MCP Integration Testing
```bash
# Test stdio transport directly (from main directory)
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python server.py --transport stdio

# Test with MCP client library
python -c "
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_mcp():
    server = StdioServerParameters(
        command='python',
        args=['server.py', '--transport', 'stdio']
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            tools = await session.list_tools()
            print(f'Available tools: {[tool.name for tool in tools]}')

asyncio.run(test_mcp())
"
```

## 🛠️ Development

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd model-context-protocol/docs-server

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Setup pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Development Workflow

#### Code Style and Linting
```bash
# Format code with Black
black . --line-length 88

# Lint with flake8
flake8 . --max-line-length 88 --ignore E203,W503

# Type checking with mypy
mypy . --ignore-missing-imports
```

#### Hot Reload Development
```bash
# Start server with auto-reload for development
python server.py --transport http --port 8000 --device auto

# Or use uvicorn directly for HTTP mode (if FastAPI mode is available)
uvicorn server:app --reload --port 8000
```

### Adding New Features

#### Adding New MCP Tools
1. Define the tool function in `search_tools.py`
2. Add Pydantic models to `models.py`
3. Register the tool in `server.py`
4. Add comprehensive tests
5. Update this documentation

#### Adding New Search Providers
1. Implement the `SearchEngine` interface in `models.py`
2. Add the engine to `search_tools.py`
3. Update configuration options
4. Add performance benchmarks

### Debugging

#### Logging Configuration
```bash
# Enable debug logging (note: controlled by Python logging, not MCP environment variables)
export PYTHONPATH=/path/to/docs-server

# Start with verbose output
python server.py --transport http --port 8000 --device auto
```

#### Common Debugging Scenarios
```bash
# Debug search issues (from main directory)
python -c "
from search_tools import SearchTools
from models import SearchRequest
tools = SearchTools('./logzilla-docs')
result = tools.search_documents(SearchRequest(query='test', max_results=5))
print(result)
"

# Debug document indexing (from main directory)
python -c "
from document_cache import DocumentCache
cache = DocumentCache('./logzilla-docs')
docs = cache.list_documents()
print(f'Found {len(docs)} documents')
"
```

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    subgraph "MCP Clients"
        A[Claude Desktop] 
        B[Custom MCP Client]
        C[HTTP Client]
    end
    
    subgraph "Transport Layer"
        D[stdio Transport]
        E[HTTP Transport] 
        F[HTTPS Transport]
    end
    
    subgraph "MCP Documentation Server"
        G[FastMCP Core]
        H[Authentication Layer]
        I[Request Router]
    end
    
    subgraph "Search Engine"
        J[Hybrid Search Orchestrator]
        K[BM25 Keyword Search]
        L[FAISS Vector Search]
        M[Sentence Transformers]
    end
    
    subgraph "Data Layer"
        N[Document Cache]
        O[File System Monitor]
        P[Metadata Index]
    end
    
    subgraph "Storage"
        Q[Documentation Files]
        R[Search Indices]
        S[Cache Storage]
    end
    
    A --> D
    B --> E
    C --> F
    D --> G
    E --> G
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    J --> L
    L --> M
    J --> N
    N --> O
    N --> P
    O --> Q
    P --> R
    N --> S
```

### Component Architecture

#### Transport Layer
- **stdio**: Direct MCP client integration via stdin/stdout
- **HTTP**: RESTful API for web integration  
- **HTTPS**: Secure HTTP with SSL/TLS encryption

#### Search Architecture
```python
# Hybrid Search Flow
query = "authentication setup"

# 1. BM25 Keyword Search
bm25_results = bm25_engine.search(query, max_results=20)
bm25_scores = [result.score for result in bm25_results]

# 2. Vector Semantic Search  
query_embedding = sentence_transformer.encode(query)
vector_results = faiss_index.search(query_embedding, max_results=20)
vector_scores = [result.score for result in vector_results]

# 3. Hybrid Score Combination
final_results = combine_scores(
    bm25_results, vector_results,
    bm25_weight=0.7, vector_weight=0.3
)
```

#### Document Processing Pipeline
```python
# Document Indexing Flow
markdown_file → document_parser → chunks → {
    bm25_index.add_document(chunks),
    vector_embeddings = sentence_transformer.encode(chunks),
    faiss_index.add_vectors(vector_embeddings),
    document_cache.store_metadata(document)
}
```


## 🔒 Security Considerations

### Authentication & Authorization
- **OAuth 2.0 Integration**: Full OAuth token introspection support
- **Transport Security**: HTTPS with configurable SSL/TLS certificates

### File System Security
- **Sandboxed Access**: Only serves files from configured documentation directory
- **Path Traversal Protection**: Robust protection against directory traversal attacks
- **File Type Restrictions**: Configurable allowed file extensions
- **Size Limits**: Configurable maximum file sizes prevent abuse

### Network Security
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Rate Limiting**: Built-in request rate limiting (planned)
- **Request Validation**: Comprehensive Pydantic-based input validation
- **Error Sanitization**: Secure error messages that don't leak system information

## ⚡ Performance & Optimization

### Search Performance
```bash
# Performance tuning environment variables
export MCP_DEVICE="cuda"                  # Use GPU for embeddings (if available)
export MCP_MAX_FILE_SIZE="20971520"       # Increase max file size to 20MB
# Note: Other performance settings are configured in the application code
```

### System Optimization
- **Async/Await**: Full asynchronous I/O for high concurrency
- **HTTP Streaming**: Efficient transfer of large responses
- **Document Caching**: Intelligent metadata and content caching
- **Index Optimization**: Optimized FAISS indices for fast vector search
- **Connection Pooling**: Uvicorn server with optimized connection handling

### Memory Management
```bash
# Monitor memory usage
docker stats docs-server

# Optimize for large document sets
export MCP_MAX_FILE_SIZE="5242880"       # Limit individual file sizes (5MB)
export MCP_DEVICE="cpu"                  # Use CPU only to reduce memory usage
```

## 🚀 Production Deployment

### Docker Production Setup

Create a production `compose.prod.yml` file:

```yaml
# compose.prod.yml
version: '3.8'
services:
  docs-server:
    image: mcp-docs-server:latest
    restart: always
    ports:
      - "443:8443"
    volumes:
      # CRITICAL: Mount your production documentation directory
      - /path/to/your/production/docs:/app/docs:ro
      # Examples:
      # - /var/www/company-docs:/app/docs:ro
      # - /opt/documentation:/app/docs:ro
      # - /home/docs/knowledge-base:/app/docs:ro
      
      # SSL certificates (for HTTPS)
      - /etc/ssl/certs:/app/certs:ro
      # Logs directory
      - ./logs:/app/logs
    environment:
      - MCP_TRANSPORT=https
      - MCP_PORT=8443
      - MCP_SSL_CERT_PATH=/app/certs/server.crt
      - MCP_SSL_KEY_PATH=/app/certs/server.key
      - MCP_DOCS_PATH=/app/docs
    healthcheck:
      test: ["CMD", "curl", "-f", "-k", "https://localhost:8443/help"]
      interval: 30s
      timeout: 10s
      retries: 3

# Deploy with:
# docker-compose -f compose.prod.yml up -d
```

**Production Documentation Setup:**
1. **Update the volume path**: Change `/path/to/your/production/docs` to your actual documentation directory
2. **Ensure read permissions**: The documentation directory must be readable by the container
3. **Structure doesn't matter**: Any directory structure with `.md` files will work
4. **Real-time updates**: Changes to documentation files are automatically detected

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-docs-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-docs-server
  template:
    metadata:
      labels:
        app: mcp-docs-server
    spec:
      containers:
      - name: docs-server
        image: mcp-docs-server:latest
        ports:
        - containerPort: 8008
        env:
        - name: MCP_TRANSPORT
          value: "http"
        - name: MCP_HOST
          value: "0.0.0.0"
        - name: MCP_PORT
          value: "8008"
        volumeMounts:
        - name: docs-volume
          mountPath: /app/docs
          readOnly: true
      volumes:
      - name: docs-volume
        configMap:
          name: documentation-files
```

### System Service (systemd)
```ini
# /etc/systemd/system/mcp-docs-server.service
[Unit]
Description=MCP Documentation Server
After=network.target

[Service]
Type=simple
User=mcp-server
Group=mcp-server
WorkingDirectory=/opt/mcp-docs-server
Environment=MCP_TRANSPORT=https
Environment=MCP_PORT=8443
Environment=MCP_DOCS_PATH=/opt/docs
ExecStart=/opt/mcp-docs-server/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring & Logging

### Health Monitoring
```bash
# Server status via help page
curl https://localhost:8443/help

# Health check via MCP tool (requires MCP client)
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "health_check", "arguments": {}}'
```

### Logging Configuration
```bash
# Logging is controlled by Python's logging module
# Server outputs structured logs to stderr by default
# Redirect to file using shell redirection:
python server.py --transport http --port 8000 2>/var/log/mcp-docs-server.log
```

### Log Analysis Examples
```bash
# Monitor search queries
tail -f /var/log/mcp-docs-server/server.log | grep "search_documents"

# Performance monitoring
grep "execution_time_ms" /var/log/mcp-docs-server/server.log | \
  awk '{print $NF}' | sort -n | tail -10

# Error tracking
grep "ERROR" /var/log/mcp-docs-server/server.log | tail -20
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. SSL Certificate Errors
```bash
# Symptoms: SSL handshake failures, certificate validation errors
# Solutions:
- Verify certificate files exist and are readable
- Check certificate validity: openssl x509 -in server.crt -text -noout
- Ensure certificate matches hostname
   - Use absolute paths for certificate files
- Check certificate chain completeness
```

#### 2. Search Performance Issues
```bash
# Symptoms: Slow search responses, high memory usage
# Solutions:
# Use supported environment variables  
export MCP_DEVICE="cpu"                    # Force CPU if GPU issues
export MCP_MAX_FILE_SIZE="5242880"        # Reduce max file size

# Restart server to rebuild indices (indices rebuild automatically on startup)
python server.py --transport http --port 8000 --device cpu
```

#### 3. Document Indexing Problems
```bash
# Symptoms: Documents not found, indexing errors
# Debug steps (run from main directory):
python -c "
from document_cache import DocumentCache
cache = DocumentCache('./logzilla-docs')
print(f'Found documents: {len(cache.list_documents())}')
for doc in cache.list_documents()[:5]:
    print(f'  {doc.path} - {doc.size} bytes')
"
```

#### 4. Memory and Resource Issues
```bash
# Monitor resource usage
docker stats --no-stream docs-server

# Optimize for limited resources
export MCP_MAX_FILE_SIZE="2097152"        # 2MB limit
export MCP_DEVICE="cpu"                   # Force CPU-only mode
```

#### 5. Network and Connectivity
```bash
# Test local connectivity
curl -v http://localhost:8000/help

# Test with authentication (if OAuth is enabled)
curl -H "Authorization: Bearer your-oauth-token" http://localhost:8000/resources

# Debug HTTPS issues
openssl s_client -connect localhost:8443 -servername localhost
```

### Debug Mode
```bash
# Enable comprehensive debugging
python server.py --transport http --port 8000 --device auto
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run the test suite: `pytest`
5. Submit a pull request

### Development Standards
- **Code Style**: Follow Black formatting (88 character lines)
- **Type Hints**: Use comprehensive type annotations  
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update README and docstrings
- **Performance**: Benchmark any performance-critical changes

### Areas for Contribution
- **New Search Algorithms**: Additional search engine implementations
- **Performance Optimizations**: Caching, indexing, and query optimization
- **Transport Protocols**: Additional MCP transport implementations
- **Authentication**: Additional authentication providers
- **Documentation**: Improved documentation and examples

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastMCP**: For the excellent MCP server framework
- **FAISS**: For high-performance vector similarity search
- **Sentence Transformers**: For state-of-the-art text embeddings
- **FastAPI**: For the robust async web framework
- **Pydantic**: For data validation and serialization