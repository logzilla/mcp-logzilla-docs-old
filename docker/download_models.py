#!/usr/bin/env python3
"""
Pre-download embedding models for the vector search engine.
This script downloads the models during Docker build to avoid runtime downloads.
"""

import logging
import sys
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_model(model_name: str, device: str = "cpu") -> bool:
    """Download a specific sentence-transformer model
    
    Args:
        model_name: HuggingFace model identifier
        device: Device to use for loading (use "cpu" during build to avoid GPU issues)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from sentence_transformers import SentenceTransformer
        
        logger.info(f"Downloading model: {model_name}")
        
        # Load the model which will trigger download if not cached
        model = SentenceTransformer(model_name, device=device)
        
        # Verify the model works by encoding a test string
        test_embedding = model.encode("test sentence", convert_to_numpy=True)
        
        logger.info(f"Successfully downloaded and verified model: {model_name} (dimension: {len(test_embedding)})")
        
        # Clean up the model to free memory
        del model
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model {model_name}: {e}")
        return False

def main():
    """Download all supported models"""
    
    # Models from vector_search.py SUPPORTED_MODELS
    models_to_download = [
        "sentence-transformers/all-MiniLM-L6-v2",  # Fallback model - download first
        "BAAI/bge-small-en-v1.5",                  # Good balance model
        "thenlper/gte-large",                      # Default/large model
        "sentence-transformers/all-mpnet-base-v2"  # High-quality model
    ]
    
    logger.info("Starting model download process...")
    logger.info(f"Will download {len(models_to_download)} models")
    
    success_count = 0
    for model_name in models_to_download:
        if download_model(model_name, device="cpu"):
            success_count += 1
        else:
            logger.warning(f"Skipping failed model: {model_name}")
    
    logger.info(f"Download complete: {success_count}/{len(models_to_download)} models downloaded successfully")
    
    if success_count == 0:
        logger.error("No models were downloaded successfully!")
        sys.exit(1)
    elif success_count < len(models_to_download):
        logger.warning(f"Some models failed to download ({success_count}/{len(models_to_download)})")
        # Don't exit with error if at least one model downloaded
    else:
        logger.info("All models downloaded successfully!")

if __name__ == "__main__":
    main()
