#!/usr/bin/env python3
"""
MCP Documentation Server - Fixed Version
========================================

A Model Context Protocol (MCP) server implementation with full functionality
from server_new.py but using the working asyncio pattern from stdio_server_test.py.

Features:
- Document listing and statistics  
- Full-text document retrieval
- Search functionality via integrated search tools
- Support for stdio, HTTP, and HTTPS transports

- Advanced configuration with environment variables
"""

import argparse
import asyncio
import contextlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import logging
import logging.handlers
import os
from pathlib import Path
from pydantic import BaseModel, Field, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys
from typing import Any, Dict, List, Optional, Union, Annotated, Callable, Tuple, Type
import yaml

from search_engine_faiss import FaissSearchEngine, FaissSearchEngineFactory
from models import Document, DocumentChunk, SearchEngine, SearchEngineFactory

# Load environment variables
load_dotenv()

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from mcp.types import PromptMessage, TextContent

# FastAPI imports for HTTP mode
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, RedirectResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class DEFAULTS:
    """Default configuration values with type annotations."""
    MODEL_NAME: str = "thenlper/gte-large"
    EMBEDDING_PATH: str = "./embeddings"
    DEVICE: str = "auto"
    
# Configure logging following reference pattern
def setup_logger() -> logging.Logger:
    """Configure logging for the MCP server to stderr."""
    logger = logging.getLogger("mcp-docs-server")

    # Remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create stderr handler for console output
    stderr_handler = logging.StreamHandler(sys.stderr)

    # Add handler to logger
    logger.addHandler(stderr_handler)

    # Set level
    logger.setLevel(logging.INFO)

    return logger


logger: logging.Logger = setup_logger()


class ServerSettings(BaseSettings):
    """Settings for the MCP Documentation Server following reference pattern."""

    model_config = SettingsConfigDict(env_prefix="MCP_", extra="allow")

    # Transport settings
    transport: str = Field(
        default="stdio",
        description="Transport mode: stdio, http, or https"
    )
    
    # Server settings
    host: str = Field(
        default="localhost",
        description="Server host address"
    )
    port: int = Field(
        default=8000,
        description="Server port number"
    )
    server_url: AnyHttpUrl = Field(
        default="http://localhost:8000",
        description="Full server URL"
    )
    
    # SSL settings
    ssl_cert_path: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate file"
    )
    ssl_key_path: Optional[str] = Field(
        default=None, 
        description="Path to SSL private key file"
    )

    # Server description
    description: str = Field(
        default="company documentation",
        description="Server description"
    )
    server_name: str = Field(
        default="docs-server",
        description="Name of the MCP server"
    )
    transformer_device: str = Field(
        default="auto",
        description="Device for transformer model"
    )
    
    # Model settings
    model_name: str = Field(
        default=DEFAULTS.MODEL_NAME,
        description="Name of the embedding model to use"
    )
    embedding_path: str = Field(
        default=DEFAULTS.EMBEDDING_PATH,
        description="Path to embedding files"
    )
    embedding_name: str = Field(
        default="docs_embeddings",
        description="Name identifier for embedding files"
    )
    
    # Version/alias handling
    alias_file: Optional[str] = Field(
        default=None,
        description="Path to version to aliases YAML file (optional)"
    )
    default_version: str = Field(
        default="latest",
        description="Default version when none specified"
    )


class FastAppSettings:
    """Application settings for HTTP/HTTPS mode following reference pattern."""
    
    def __init__(self, settings: ServerSettings, mcp_app: FastMCP) -> None:
        self.expose_url: str = str(settings.server_url)
        self.dns: Optional[str] = None
        self.settings: ServerSettings = settings
        self.servers: List[FastMCP] = [mcp_app]  # Use the provided FastMCP app

class FastApp:
    """FastAPI application for HTTP/HTTPS mode following reference pattern."""
    
    def __init__(self, fast_app_settings: FastAppSettings) -> None:
        self.app_settings: FastAppSettings = fast_app_settings

    def create_app(self) -> FastAPI:
        """Create FastAPI application with MCP server mounting."""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")
            
        servers = self.app_settings.servers

        # Create a combined lifespan to manage session managers
        @contextlib.asynccontextmanager
        async def lifespan(app: FastAPI) -> Any:
            async with contextlib.AsyncExitStack() as stack:
                for server in servers:
                    await stack.enter_async_context(server.session_manager.run())
                yield

        app = FastAPI(lifespan=lifespan)
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure as needed
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount the FastMCP app at root so its internal routes
        # (e.g., /mcp, /.well-known/*, /register) are exposed exactly
        # at those paths. This supports reverse proxies routing only
        # /mcp to this upstream.
        for server in servers:
            app.mount("/", server.streamable_http_app())

        @app.get("/", include_in_schema=False)
        async def redirect_to_help() -> RedirectResponse:
            return RedirectResponse(url="/help")

        @app.get("/help", include_in_schema=False)
        async def help() -> HTMLResponse:
            """Generate help page with server information."""
            try:
                help_text = """
                <html>
                <head><title>MCP Documentation Server</title></head>
                <body>
                <h1>MCP Documentation Server</h1>
                <p>This server provides access to documentation through the Model Context Protocol (MCP).</p>
                <h2>Available Servers</h2>
                """
                
                for server in servers:
                    tools = []
                    try:
                        tools = [tool.name for tool in server._tool_manager.list_tools()]
                    except Exception:
                        try:
                            maybe_tools = getattr(server, 'tools', [])
                            tools = [getattr(t, 'name', str(t)) for t in maybe_tools]
                        except Exception:
                            tools = []
                    help_text += f"""
                    <h3>{server.name}</h3>
                    <p>{server.instructions}</p>
                    <p><strong>Endpoint:</strong> <code>{self.app_settings.expose_url}/mcp</code></p>
                    <p><strong>Tools:</strong> {', '.join(tools) if tools else 'None'}</p>
                    """

                help_text += "</body></html>"
                return HTMLResponse(content=help_text, status_code=200)

            except Exception as e:
                logger.error(f"Error generating help page: {str(e)}")
                raise HTTPException(status_code=500, detail="Error generating help page")

        return app


class MCPServer:
    """
    MCP Server class that encapsulates search engine and server creation
    following MCP specification requirements.
    """
    
    def __init__(self, settings: ServerSettings, device: str = "auto") -> None:
        self._settings: ServerSettings = settings
        self._device: str = device
        self._logger: logging.Logger = logger
        
        # Create factory for shared SentenceTransformer
        self._engine_factory: SearchEngineFactory = FaissSearchEngineFactory(
            model_name=settings.model_name,
            device=settings.transformer_device,
            embedding_dir=settings.embedding_path,
            embedding_prefix=""
        )
        
        # Cache for search engines by canonical version
        self._engine_cache: Dict[str, SearchEngine] = {}
        
        # Load alias mapping from YAML if provided
        self._alias_to_version: Dict[str, str] = {}
        self._valid_versions: set[str] = set()
        self._load_alias_mapping()
        
        self._is_ready: bool = False
        self._initialization_error: Optional[str] = None
    
    def _load_alias_mapping(self) -> None:
        """Load version to aliases mapping from YAML file if provided."""
        if not self._settings.alias_file:
            return
            
        try:
            alias_path = Path(self._settings.alias_file)
            if not alias_path.exists():
                self._logger.warning(f"Alias file not found, using no aliases: {alias_path}")
                return
                
            with open(alias_path, 'r', encoding='utf-8') as f:
                version_aliases = yaml.safe_load(f) or {}
                
            # Convert version to aliases list to alias to version mapping
            for version, aliases in version_aliases.items():
                self._valid_versions.add(version)
                if aliases:
                    for alias in aliases:
                        self._alias_to_version[alias] = version
                        
            self._logger.info(f"Loaded {len(self._alias_to_version)} aliases for {len(self._valid_versions)} versions")
            
        except Exception as e:
            self._logger.warning(f"Failed to load alias mapping: {e}")
    
    def _resolve_version(self, requested_version: Optional[str] = None) -> str:
        """Resolve requested version to canonical version."""
        if not requested_version:
            requested_version = self._settings.default_version
            
        # Check if it's an alias
        canonical = self._alias_to_version.get(requested_version, requested_version)
        
        # Validate it's a known version (if we have alias info)
        if self._valid_versions and canonical not in self._valid_versions:
            raise ValueError(f"Unknown version '{requested_version}'. Available: {sorted(self._valid_versions)}")
            
        return canonical
    
    def _get_search_engine(self, version: Optional[str] = None) -> SearchEngine:
        """Get or create search engine for the specified version."""
        canonical = self._resolve_version(version)
        
        if canonical not in self._engine_cache:
            try:
                engine = self._engine_factory.get_engine(canonical)
                self._engine_cache[canonical] = engine
            except Exception as e:
                raise ValueError(f"Failed to load search engine for version '{canonical}': {e}")
                
        return self._engine_cache[canonical]
       
    def create_public_server(self) -> Optional[FastMCP]:
        """Create public documentation server following reference pattern."""
        try:
            # Test default version engine initialization
            default_engine = self._get_search_engine()
            
            mcp = FastMCP(
                name=self._settings.server_name,
                instructions=f"Documentation server for {self._settings.description}. Provides search and retrieval of documentation with version support.",
                debug=True,
                stateless_http=True
            )
            self._is_ready = True
        except Exception as e:
            self._initialization_error = str(e)
            logger.error(f"Failed to initialize search engine: {e}")
            logger.error(f"Failed to create FastMCP server: {e}")
            return None

        # Add MCP tools
        @mcp.tool(
            name="search_for_chunks",
            description="Search for document chunks matching query"
        )
        def search_for_chunks(
                query: Annotated[str, Field(description="Search query string", min_length=1, max_length=1000)],
                top_k: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=50)] = 10,
                version: Annotated[Optional[str], Field(description="Documentation version (default: latest)")] = None
            ) -> Dict[str, Any]:
                """Search for document chunks using the integrated search tools"""
                # Check if server is ready
                if not self._is_ready:
                    return {
                        "status": "not_ready",
                        "message": "Server not ready"
                    }
                
                try:
                    search_engine = self._get_search_engine(version)
                    chunks: List[DocumentChunk] = search_engine.search_for_chunks(
                        query=query,
                        top_k=top_k
                    )
                    canonical_version = self._resolve_version(version)
                    return {
                        "status": "success",
                        "chunks": [c.to_dict() for c in chunks],
                        "query": query,
                        "version": canonical_version,
                        "total_chunks": len(chunks)
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Search for chunks failed: {str(e)}"
                    }

        @mcp.tool(
            name="search_for_documents",
            description="Search for full documents matching query"
        )
        def search_for_documents(
            query: Annotated[str, Field(description="Search query string", min_length=1, max_length=1000)],
            top_k: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=50)] = 10,
            version: Annotated[Optional[str], Field(description="Documentation version (default: latest)")] = None
        ) -> Dict[str, Any]:
            """Search for documents and retrieve their full content"""
            # Check if server is ready
            if not self._is_ready:
                return {
                    "status": "not_ready",
                    "message": "Server not ready"
                }
            
            try:
                search_engine = self._get_search_engine(version)
                documents: List[Document] = search_engine.search_for_documents(query, top_k)
                canonical_version = self._resolve_version(version)
                return {
                    "status": "success",
                    "documents": [d.to_dict() for d in documents],
                    "query": query,
                    "version": canonical_version,
                    "total_documents": len(documents)
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Search for documents failed: {str(e)}"
                }
                
        # note: there was an mcp resource of "docs://document/{document_id}"
        #       but it we're not using it now because we don't keep documents
        #       by id anywhere at this point. review git history for more info

        # Add utility tools
        @mcp.tool()
        def health_check() -> Dict[str, Any]:
            """Check the health status of the documentation server."""
            try:
                total_documents = 0
                
                # Count documents from cached engines
                for engine in self._engine_cache.values():
                    total_documents += getattr(engine, 'doc_count', 0)
                
                # If no engines cached, try to get default engine to verify service works
                if not self._engine_cache:
                    try:
                        default_engine = self._get_search_engine()
                        total_documents = getattr(default_engine, 'doc_count', 0)
                    except Exception as e:
                        return {
                            "status": "error",
                            "message": f"Service unavailable: {str(e)}"
                        }
                
                return {
                    "status": "ready" if self._is_ready else "initializing",
                    "documents_loaded": total_documents,
                    "available_versions": sorted(self._valid_versions) if self._valid_versions else ["default"],
                    "aliases": dict(self._alias_to_version),
                    "default_version": self._settings.default_version
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}"
                }
        
        @mcp.tool()
        def list_versions() -> Dict[str, Any]:
            """List available documentation versions and their aliases."""
            try:
                return {
                    "status": "success",
                    "versions": sorted(self._valid_versions) if self._valid_versions else ["default"],
                    "aliases": dict(self._alias_to_version),
                    "default_version": self._settings.default_version
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to list versions: {str(e)}"
                }
        
        return mcp

    def run_stdio_server(self) -> None:
        """Run MCP server in stdio mode. Now synchronous since FastMCP handles async internally."""
        
        self._logger.debug("Step 7: Creating FastMCP server...")
        public_server = self.create_public_server()
        if public_server is None:
            self._logger.error("Failed to create public server")
            if self._initialization_error:
                raise Exception(self._initialization_error)
            return
        
        self._logger.debug("Step 8: Starting server in stdio mode...")
        self._logger.info("Starting MCP server in stdio mode")

        # Let FastMCP itself spin up the stdio transport and session manager:
        try:
            self._logger.debug("Step 9: Server running in stdio mode...")
            # Type assertion to help linter understand public_server is not None
            assert public_server is not None
            
            # Use FastMCP's default run() method (stdio mode)
            self._logger.debug("Step 10: Starting FastMCP default mode (stdio)...")
            # Use the synchronous run() method without transport parameter (defaults to stdio)
            public_server.run()
            self._logger.debug("Step 11: Server finished.")
        except Exception as e:
            self._logger.error(f"Failed to run public server: {e}")

    def run_http_server_with_mcp(self) -> int:
        """Run MCP server in HTTP mode following reference pattern."""
        
        self._logger.debug("Step 7: Creating FastMCP server...")
        
        # Create public server
        public_app = self.create_public_server()
        if public_app is None:
            self._logger.error("Failed to create public server")
            if self._initialization_error:
                raise Exception(self._initialization_error)
            return 1
        
        self._logger.debug(f"Step 8: Starting server in {self._settings.transport.upper()} mode...")
        
        # Start HTTP server with public app
        self.run_http_server(public_app)
        self._logger.debug("Step 9: HTTP/HTTPS server finished.")
        return 0

    def run_http_server(self, mcp_app: FastMCP) -> None:
        """Run MCP server in HTTP/HTTPS mode following reference pattern."""
        if not FASTAPI_AVAILABLE:
            self._logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
            return

        try:
            # Create list of servers to mount
            servers = [mcp_app]
                
            app_settings = FastAppSettings(self._settings, mcp_app)
            fast_app = FastApp(app_settings)
            app = fast_app.create_app()
            
            # Configure SSL if HTTPS
            ssl_keyfile = self._settings.ssl_key_path if self._settings.transport == "https" else None
            ssl_certfile = self._settings.ssl_cert_path if self._settings.transport == "https" else None
            
            if self._settings.transport == "https" and (not ssl_keyfile or not ssl_certfile):
                self._logger.warning("SECURITY WARNING: HTTPS requested but SSL cert/key not provided. Falling back to HTTP. This connection will NOT be encrypted!")
                ssl_keyfile = ssl_certfile = None
            
            self._logger.info(f"Starting MCP server on {self._settings.host}:{self._settings.port} ({'HTTPS' if ssl_keyfile else 'HTTP'})")

            uvicorn.run(
                app,
                host=self._settings.host,
                port=self._settings.port,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
                log_level="info"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to start HTTP server: {e}")
            raise


def main() -> int:
    """Working FastMCP implementation with full server_new.py functionality."""
    import sys
    logger.info("🚀 MCP Documentation Server initializing...")
    logger.debug("=== BUILD v3.0 - Non-blocking MCP Server with MCPServer class ===")
    
    logger.debug("Step 1: Parsing arguments...")
    
    # Enhanced argument parsing from server_new.py
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="MCP Documentation Server - A Model Context Protocol server for documentation search and retrieval",
        epilog="""
Environment Variables:
  All command line arguments can be set via environment variables with MCP_ prefix.
  Command line arguments override environment variables.
  
  Examples:
    export MCP_TRANSPORT=http
    export MCP_HOST=127.0.0.1
    export MCP_PORT=8008
    export MCP_SERVER_NAME=my-docs-server
    export MCP_DESCRIPTION="My documentation server"
    

        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-d", "--debug", action="store_true", 
                       help="Enable debug logging output.") 
    parser.add_argument("--transport", choices=["stdio", "http", "https"], 
                       default=os.getenv("MCP_TRANSPORT", "stdio"),
                       help="Transport protocol: 'stdio' for MCP clients, 'http'/'https' for web servers. Default: stdio. Set via env var MCP_TRANSPORT.")
    parser.add_argument("--host", type=str, 
                       default=os.getenv("MCP_HOST", "localhost"), 
                       help="Host address to bind server to (only for http/https transport). Default: localhost. Set via env var MCP_HOST.")
    parser.add_argument("--port", type=int, 
                       default=int(os.getenv("MCP_PORT", "8000")), 
                       help="Port number to bind server to (only for http/https transport). Default: 8000. Set via env var MCP_PORT.")
    parser.add_argument("--ssl-cert", type=str, 
                       default=os.getenv("MCP_SSL_CERT_PATH"),
                       help="Path to SSL certificate file for HTTPS transport. Set via env var MCP_SSL_CERT_PATH.")
    parser.add_argument("--ssl-key", type=str, 
                       default=os.getenv("MCP_SSL_KEY_PATH"),
                       help="Path to SSL private key file for HTTPS transport. Set via env var MCP_SSL_KEY_PATH.")
    parser.add_argument("--device", type=str, choices=["cpu", "cuda", "mps", "auto", "none"], 
                       default=os.getenv("MCP_DEVICE", "auto"), 
                       help="Compute device for vector search: 'cpu' (CPU only), 'cuda' (NVIDIA GPU), 'mps' (Apple Silicon), 'auto' (auto-detect best), 'none' (disable vector search). Default: auto. Set via env var MCP_DEVICE.")
    parser.add_argument("-n", "--server-name", type=str, 
                       default=os.getenv("MCP_SERVER_NAME", "docs-server"),
                       help="Name identifier for the MCP server instance. Default: docs-server. Set via env var MCP_SERVER_NAME.")
    parser.add_argument("--description", type=str, 
                       default=os.getenv("MCP_DESCRIPTION", "company documentation"),
                       help="Human-readable description of the MCP server. Default: 'company documentation'. Set via env var MCP_DESCRIPTION.")
    parser.add_argument("-m", "--model", type=str,
                       default=os.getenv("MCP_MODEL", DEFAULTS.MODEL_NAME),
                       help=f"Name of the embedding model to use. Default: {DEFAULTS.MODEL_NAME}. Set via env var MCP_MODEL.")
    parser.add_argument("-p", "--embedding-path", type=str,
                       default=os.getenv("MCP_EMBEDDING_PATH", DEFAULTS.EMBEDDING_PATH),
                       help=f"Path to embedding files. Default: {DEFAULTS.EMBEDDING_PATH}. Set via env var MCP_EMBEDDING_PATH.")
    parser.add_argument("-e", "--embedding-name", type=str,
                       default=os.getenv("MCP_EMBEDDING_NAME", "docs_embeddings"),
                       help="Name identifier for embedding files. Default: docs_embeddings. Set via env var MCP_EMBEDDING_NAME.")
    parser.add_argument("--alias-file", type=str,
                       default=os.getenv("MCP_ALIAS_FILE"),
                       help="Path to version to aliases YAML file. Set via env var MCP_ALIAS_FILE.")
    parser.add_argument("--default-version", type=str,
                       default=os.getenv("MCP_DEFAULT_VERSION", "latest"),
                       help="Default documentation version. Default: latest. Set via env var MCP_DEFAULT_VERSION.")
    args: argparse.Namespace = parser.parse_args()
    
    logger.debug(f"Step 2: Args parsed - debug: {args.debug}, transport: {args.transport}")
    
    logger.debug("Step 3: Setting up logging...")
    
    # Set up logging with debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    logger.debug("Step 4: Logging configured")
    
    logger.debug("Step 5: Creating settings...")
    

    # Create settings object with all the advanced options
    settings: ServerSettings = ServerSettings(
        transport=args.transport,
        host=args.host,
        port=args.port,
        server_url=f"http{'s' if args.transport == 'https' else ''}://{args.host}:{args.port}",
        transformer_device=args.device,
        ssl_cert_path=args.ssl_cert,
        ssl_key_path=args.ssl_key,
        server_name=args.server_name,
        description=args.description,
        model_name=args.model,
        embedding_path=args.embedding_path,
        embedding_name=args.embedding_name,
        alias_file=args.alias_file,
        default_version=args.default_version
    )
    
    logger.debug(f"Step 6: Settings created - {settings}")
    
    # Handle different transport modes using MCPServer class
    try:
        # Create MCP server instance
        mcp_server: MCPServer = MCPServer(settings, device=args.device)
        
        if settings.transport == "stdio":
            # Call the stdio server directly
            mcp_server.run_stdio_server()
                
        elif settings.transport in ["http", "https"]:
            result: int = mcp_server.run_http_server_with_mcp()
            return result
        else:
            logger.error(f"Unknown transport mode '{settings.transport}'")
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        # Show help when there's a server initialization error
        if "FAISS index file not found" in str(e) or "Failed to initialize" in str(e):
            print("\n" + "="*80)
            print("HELP: Server initialization failed. Please check the following:")
            print("="*80)
            parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
