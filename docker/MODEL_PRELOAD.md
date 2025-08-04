# Pre-loading Embedding Models in Docker

## Overview

The vector search engine automatically downloads embedding models from HuggingFace when first initialized. To avoid this download delay at runtime, we pre-download the models during Docker build.

## What Gets Downloaded

The following models are downloaded during build (from `vector_search.py`):

1. **sentence-transformers/all-MiniLM-L6-v2** (384D) - Fallback model
2. **BAAI/bge-small-en-v1.5** (384D) - Good balance of speed/accuracy
3. **thenlper/gte-large** (1024D) - Default model, excellent for technical content
4. **sentence-transformers/all-mpnet-base-v2** (768D) - High-quality semantic search

## How It Works

### Build Process
1. `download_models.py` is copied into the container
2. During `docker build`, the script downloads all models to `/root/.cache/huggingface/`
3. Models are cached in the final image layer
4. Runtime model loading becomes instant

### Model Cache Location
- **Container**: `/root/.cache/huggingface/`
- **Host (optional)**: `./model_cache/` (if volume mounted)

## Usage

### Standard Build (models cached in image)
```bash
cd model-context-protocol/docs-server/docker
docker-compose build
docker-compose up
```

### With Persistent Cache (faster rebuilds)
1. Uncomment the cache volume in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./model_cache:/root/.cache/huggingface:rw
   ```

2. Build and run:
   ```bash
   docker-compose build
   docker-compose up
   ```

The `./model_cache/` directory will be created and models will persist between container rebuilds.

## Benefits

- **No runtime downloads**: Container starts immediately
- **Offline capable**: Works without internet at runtime
- **Consistent performance**: No download delays on first use
- **Cache persistence**: Optional volume mounting for faster rebuilds

## Troubleshooting

If model download fails during build:
1. Check internet connectivity during build
2. Verify `sentence-transformers>=2.2.2` in requirements.txt
3. Check build logs for specific model errors
4. Some models are larger (gte-large ~1GB) - ensure sufficient disk space

The script will continue if some models fail, as long as at least one downloads successfully.
