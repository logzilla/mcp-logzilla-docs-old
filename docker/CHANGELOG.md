# Docker Configuration Updates - Changelog

## Overview

This document summarizes all the updates made to the Docker configuration to align with the latest server application changes and improvements.

## 🔄 Changes Made

### 1. Requirements.txt Updates

**Added Missing Dependencies:**
- `PyYAML>=6.0.0` - Required for YAML parsing in alias configuration support

**Rationale:** The server.py uses `yaml.safe_load()` for loading version aliases but PyYAML was not included in the requirements.

### 2. Dockerfile Improvements

**Fixed Copy Path Issues:**
- Changed `COPY ../requirements.txt .` to `COPY requirements.txt .`
- Changed `COPY ../models.py .` to `COPY models.py .`
- Changed `COPY ../server.py .` to `COPY server.py .`
- Changed `COPY ../search_engine_faiss.py .` to `COPY search_engine_faiss.py .`
- Changed `COPY ../embeddings /app/embeddings` to `COPY embeddings /app/embeddings`

**Added Missing Files:**
- Added `COPY index_builder_faiss.py .` - Required by the server application

**Updated Default Command:**
- Enhanced CMD with all necessary arguments matching server.py argument structure:
  ```dockerfile
  CMD ["python", "server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8008", "--server-name", "logzilla-docs-server", "--description", "logzilla documentation", "--model", "thenlper/gte-large", "--embedding-path", "/app/embeddings", "--embedding-name", "logzilla_md_docs", "--device", "auto", "--default-version", "latest"]
  ```

### 3. Docker Compose Configuration Updates

**Environment Variables Alignment:**
- Changed `MCP_MODEL_NAME` to `MCP_MODEL` (matches server.py argument parsing)
- Changed `MCP_TRANSFORMER_DEVICE` to `MCP_DEVICE` (matches server.py argument parsing)
- Fixed `MCP_EMBEDDING_NAME` from `docs_embeddings` to `logzilla_md_docs` (matches actual usage)
- Added `MCP_DEFAULT_VERSION=latest` for version support

**Volume Mounts:**
- Added embeddings persistence: `- ../embeddings:/app/embeddings:rw`
- Enabled model cache persistence: `- ./model_cache:/root/.cache/huggingface:rw`

**Command Arguments:**
- Updated command with complete argument set matching server.py:
  ```yaml
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
  ```

### 4. .dockerignore Updates

**Enhanced Exclusions:**
- Added `tests/` directory exclusion
- Added `.env` and `.env.local` exclusions for better security

### 5. Documentation Enhancements

**Added New Sections:**
- **Model Pre-loading and Dependencies** - Documents the embedding model download process
- **Environment Variables** - Comprehensive table of all MCP_ prefixed environment variables
- **Updated Configuration Details** - Reflects all new volume mounts and settings

**Updated Existing Sections:**
- **Configuration Examples** - Updated to match new environment variables and command structure
- **Key Configuration Details** - Added embeddings, model cache, and device information

## 🎯 Key Improvements

### 1. **Dependency Management**
- All required Python packages are now properly declared
- YAML support added for advanced configuration features

### 2. **Path Resolution**
- Fixed all relative path issues in Dockerfile
- Proper context-relative paths for Docker build process

### 3. **Configuration Consistency**
- Environment variables now match server.py argument names exactly
- Command-line arguments align with server.py parser definitions
- Default values consistent across Dockerfile and compose.yml

### 4. **Data Persistence**
- Embeddings directory properly mounted for persistence
- Model cache directory mounted to avoid re-downloading models
- Logs directory maintained for debugging

### 5. **Model Management**
- Pre-downloading of embedding models during build process
- Proper model cache persistence between container restarts
- Support for multiple embedding models with fallbacks

## 🔧 Technical Details

### Environment Variable Mapping

| Docker Compose Env | Server.py Argument | Purpose |
|-------------------|-------------------|---------|
| `MCP_TRANSPORT` | `--transport` | Protocol selection |
| `MCP_HOST` | `--host` | Server bind address |
| `MCP_PORT` | `--port` | Server port |
| `MCP_SERVER_NAME` | `--server-name` | MCP server identifier |
| `MCP_DESCRIPTION` | `--description` | Server description |
| `MCP_MODEL` | `--model` | Embedding model name |
| `MCP_EMBEDDING_PATH` | `--embedding-path` | Embeddings directory |
| `MCP_EMBEDDING_NAME` | `--embedding-name` | Embedding file prefix |
| `MCP_DEVICE` | `--device` | Compute device |
| `MCP_DEFAULT_VERSION` | `--default-version` | Default doc version |

### Volume Mount Strategy

```yaml
volumes:
  # Documentation (read-only)
  - ../logzilla-docs:/app/docs:ro
  
  # Embeddings (read-write for updates)
  - ../embeddings:/app/embeddings:rw
  
  # Model cache (read-write for persistence)
  - ./model_cache:/root/.cache/huggingface:rw
  
  # Logs (read-write for debugging)
  - ./logs:/app/logs
```

## 🚀 Usage Impact

### Before Updates
- Missing dependencies caused runtime failures
- Inconsistent environment variable names
- No model persistence between rebuilds
- Limited configuration options

### After Updates
- All dependencies properly declared and installed
- Consistent configuration across all components
- Model persistence reduces startup time
- Full configuration flexibility via environment variables
- Proper volume mounting for data persistence

## 🧪 Testing Recommendations

1. **Build Test:**
   ```bash
   cd docker
   docker-compose build
   ```

2. **Startup Test:**
   ```bash
   docker-compose up -d
   docker-compose logs -f logzilla-docs-server
   ```

3. **Health Check:**
   ```bash
   curl http://127.0.0.1:8008/help
   ```

4. **MCP Endpoint Test:**
   ```bash
   curl http://127.0.0.1:8008/logzilla-docs-server/mcp
   ```

## 📋 Migration Notes

For existing deployments:

1. **Update Environment Variables:** Change `MCP_MODEL_NAME` to `MCP_MODEL` and `MCP_TRANSFORMER_DEVICE` to `MCP_DEVICE`
2. **Create Volume Directories:** Ensure `./model_cache` directory exists for model persistence
3. **Rebuild Images:** Run `docker-compose build` to incorporate new dependencies
4. **Update Compose Files:** Use the updated compose.yml as reference for custom deployments

## ✅ Validation

All changes have been validated against:
- ✅ Server.py argument parsing structure
- ✅ Environment variable naming conventions
- ✅ Docker build context requirements
- ✅ Volume mount permissions and paths
- ✅ Health check endpoints
- ✅ Model download and caching process

---

*Last Updated: 2025-09-22*
*Changes Applied: Docker configuration alignment with server application v3.0*
