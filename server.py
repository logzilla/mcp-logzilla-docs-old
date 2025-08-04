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
- Optional OAuth authentication for private endpoints
- Public and private server instances
- Advanced configuration with environment variables
"""

import os
import sys
import argparse
import asyncio
import json
import logging
import logging.handlers
import contextlib
from typing import Any, Dict, List, Optional, Union, Annotated
from pathlib import Path
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pydantic import BaseModel, Field, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    
# OAuth imports
try:
    from mcp_oauth import IntrospectionTokenVerifier, OAuthServer, SimpleAuthSettings, AuthServerSettings
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False


# Configure logging following reference pattern
def setup_logger() -> logging.Logger:
    """Configure logging for the MCP server to stderr."""
    logger = logging.getLogger("mcp-docs-server")

    # Remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # File logging - commented out for now, can be enabled later if needed
    # # Define a consistent log directory in the user's home folder
    # log_dir = Path.home() / ".local" / "share" / "mcp-docs-server"
    # log_dir.mkdir(parents=True, exist_ok=True)
    # 
    # # Define the log file path
    # log_file = log_dir / "mcp_server.log"
    # 
    # # Create a rotating file handler
    # file_handler = logging.handlers.RotatingFileHandler(
    #     log_file,
    #     maxBytes=5 * 1024 * 1024,  # 5MB
    #     backupCount=3,
    #     encoding="utf-8",
    # )

    # Create stderr handler for console output
    stderr_handler = logging.StreamHandler(sys.stderr)

    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(message)s", 
        datefmt="%y/%m/%d %H:%M:%S"
    )

    # Add formatter to stderr handler
    stderr_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(stderr_handler)

    # Set level
    logger.setLevel(logging.DEBUG)

    return logger


logger = setup_logger()


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
        default=AnyHttpUrl("http://localhost:8000"),
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

    # Documentation settings
    docs_path: str = Field(
        default="./docs",
        description="Path to documentation directory"
    )
    max_file_size: int = Field(
        default=10485760,
        description="Maximum file size in bytes (default 10MB)"
    )
    
    # OAuth settings
    oauth_enabled: bool = Field(
        default=False,
        description="Enable OAuth authentication"
    )
    auth_server_url: AnyHttpUrl = Field(
        default=AnyHttpUrl("http://localhost:9000"),
        description="OAuth authorization server URL"
    )
    auth_server_introspection_endpoint: str = Field(
        default="http://localhost:9000/introspect",
        description="OAuth introspection endpoint"
    )
    mcp_scope: str = Field(
        default="user",
        description="Required OAuth scope"
    )
    oauth_strict: bool = Field(
        default=False,
        description="Enable strict OAuth resource validation"
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


class OAuthSettings(BaseSettings):
    """OAuth server settings following reference pattern."""
    
    model_config = SettingsConfigDict(env_prefix="OAUTH_")
    
    host: str = Field(default="127.0.0.1", description="OAuth server host")
    port: int = Field(default=9000, description="OAuth server port") 
    superusername: Optional[str] = Field(default=None, description="OAuth superuser username")
    superuserpassword: Optional[str] = Field(default=None, description="OAuth superuser password")


class FastAppSettings:
    """Application settings for HTTP/HTTPS mode following reference pattern."""
    def __init__(self, settings: ServerSettings, mcp_app: FastMCP):
        self.expose_url = str(settings.server_url)
        self.dns = None
        self.settings = settings
        self.servers = [mcp_app]  # Use the provided FastMCP app


class FastApp:
    """FastAPI application for HTTP/HTTPS mode following reference pattern."""
    def __init__(self, fast_app_settings):
        self.app_settings = fast_app_settings

    def create_app(self) -> FastAPI:
        """Create FastAPI application with MCP server mounting."""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")
            
        servers = self.app_settings.servers

        # Create a combined lifespan to manage session managers
        @contextlib.asynccontextmanager
        async def lifespan(app: FastAPI):
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
        
        # Mount each MCP server
        for server in servers:
            app.mount(f"/{server.name}", server.streamable_http_app())

        @app.get("/", include_in_schema=False)
        async def redirect_to_help():
            return RedirectResponse(url="/help")

        @app.get("/help", include_in_schema=False)
        async def help():
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
                    tools = [tool.name for tool in server._tool_manager.list_tools()]
                    help_text += f"""
                    <h3>{server.name}</h3>
                    <p>{server.instructions}</p>
                    <p><strong>Endpoint:</strong> <code>{self.app_settings.expose_url}/{server.name}/mcp</code></p>
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
    MCP Server class that encapsulates document cache, search tools, and server creation
    following MCP specification requirements.
    """
    
    def __init__(self, settings: ServerSettings, device: str = "auto"):
        self.settings = settings
        self.device = device
        self.document_cache = None
        self.search_tools = None
        self.is_ready = False
        self.server_ready = {"status": False, "message": "Server starting..."}
        self.logger = logger
        
        # Set up threading exception hook for uncaught exceptions in threads
        self._setup_threading_exception_handler()
        
        # Import dependencies
        try:
            from document_cache import DocumentCache
            self.DocumentCache = DocumentCache
        except ImportError:
            self.DocumentCache = None
            
        try:
            from search_tools import SearchTools
            from models import SearchRequest
            self.SearchTools = SearchTools
            self.SearchRequest = SearchRequest
        except ImportError as e:
            logger.warning(f"Failed to import SearchTools: {e}")
            self.SearchTools = None
            self.SearchRequest = None
        
        # Initialize document cache
        try:
            if self.DocumentCache is None:
                raise ImportError("DocumentCache not available")
            self.document_cache = self.DocumentCache()
        except Exception as e:
            logger.warning(f"Could not initialize DocumentCache: {e}")
    
    def _setup_threading_exception_handler(self):
        """Set up exception handler for uncaught exceptions in threads."""
        import threading
        import sys
        
        def thread_exception_handler(args):
            """Handle uncaught exceptions in threads."""
            exc_type, exc_value, exc_traceback, thread = args
            if exc_type is SystemExit:
                return  # Don't log SystemExit
            
            # Log the exception with full traceback
            self.logger.error(
                f"Uncaught exception in thread '{thread.name}': {exc_type.__name__}: {exc_value}",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
            
            # Also print to stderr for immediate visibility
            print(f"THREAD ERROR in '{thread.name}': {exc_type.__name__}: {exc_value}", file=sys.stderr)
            
            # Update server status if this is search initialization thread
            if thread.name.startswith("search-init") or "search" in thread.name.lower():
                self.server_ready["status"] = False
                self.server_ready["message"] = f"Search thread failed: {exc_value}"
        
        # Set the exception handler for all threads
        threading.excepthook = thread_exception_handler
    
    def on_document_cache_ready(self, loaded_count: int, error_count: int):
        """Callback when document cache is ready - initializes search tools"""
        print(f"Step 10: Document loading callback - loaded {loaded_count} docs, {error_count} errors", file=sys.stderr)
        
        if self.SearchTools and self.document_cache:
            print("Step 10: Creating SearchTools (async initialization will follow)...", file=sys.stderr)
            try:
                self.search_tools = self.SearchTools(self.document_cache, device=self.device, wait_for_vector_engine=False)
                print("Step 11: SearchTools instance created", file=sys.stderr)
                
                # Start async initialization in background thread like original
                import threading
                def async_search_initialization():
                    try:
                        self.server_ready["message"] = "Loading search engines..."
                        print("Background: Starting search engine initialization...", file=sys.stderr)
                        self.logger.info("Starting search engine initialization in background thread")
                        
                        def on_search_ready(ready: bool):
                            if ready:
                                self.is_ready = True
                                self.server_ready["status"] = True
                                self.server_ready["message"] = "Ready"
                                print("Background: ✓ Search engines ready! Server fully operational.", file=sys.stderr)
                                self.logger.info("Search engines initialized successfully")
                            else:
                                self.server_ready["status"] = False
                                self.server_ready["message"] = "Search engines failed to initialize"
                                print("Background: ✗ Search engines failed to initialize", file=sys.stderr)
                                self.logger.warning("Search engines failed to initialize")
                        
                        # Ensure search_tools is still valid before calling initialize
                        if self.search_tools is None:
                            raise RuntimeError("SearchTools instance became None during initialization")
                        
                        # Run async initialize in background thread
                        import asyncio
                        asyncio.run(self.search_tools.initialize(on_search_ready))
                        
                    except Exception as e:
                        self.server_ready["status"] = False
                        self.server_ready["message"] = f"Search initialization failed: {str(e)}"
                        error_msg = f"Failed to initialize search tools: {e}"
                        print(f"Background: {error_msg}", file=sys.stderr)
                        self.logger.error(error_msg, exc_info=True)
                
                # Create thread with descriptive name for better error tracking
                init_thread = threading.Thread(
                    target=async_search_initialization, 
                    name="search-init-worker",
                    daemon=True
                )
                
                try:
                    init_thread.start()
                    print("Step 11.5: Search initialization started in background", file=sys.stderr)
                    self.logger.info("Search initialization thread started successfully")
                except Exception as e:
                    error_msg = f"Failed to start search initialization thread: {e}"
                    print(f"Step 11.5: {error_msg}", file=sys.stderr)
                    self.logger.error(error_msg)
                    self.server_ready["status"] = False
                    self.server_ready["message"] = f"Thread start failed: {str(e)}"
                
            except Exception as e:
                print(f"Step 11: Failed to create SearchTools: {e}", file=sys.stderr)
                logger.warning(f"Could not create SearchTools: {e}")
                self.server_ready["message"] = f"SearchTools creation failed: {str(e)}"
        else:
            print("Step 10: SearchTools or DocumentCache not available", file=sys.stderr)
            logger.warning("SearchTools or DocumentCache not available")
            self.server_ready["message"] = "SearchTools not available"

    def on_search_tools_ready(self, ready: bool):
        """Callback when search tools are ready"""
        if ready:
            logger.info("Search tools are ready")
            self.is_ready = True
            self.server_ready["status"] = True
            self.server_ready["message"] = "Ready"
        else:
            logger.warning("Search tools are not ready")
            self.server_ready["status"] = False
            self.server_ready["message"] = "Search engines failed to initialize"
    
    def create_public_server(self) -> Optional[FastMCP]:
        """Create public documentation server following reference pattern."""
        try:
            mcp = FastMCP(
                name=self.settings.server_name,
                instructions=f"Documentation server for {self.settings.description}. Provides search and retrieval of documentation.",
                debug=True,
                stateless_http=True
            )
        except Exception as e:
            logger.error(f"Failed to create FastMCP server: {e}")
            return None

        # Add MCP tools
        @mcp.tool(
            name="search_for_documents",
            description="Search for documents using query text with advanced options"
        )
        def search_for_documents(
                query: Annotated[str, Field(description="Search query string", min_length=1, max_length=1000)],
                top_k: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=50)] = 10,
                min_quality: Annotated[int, Field(description="Quality cutoff 0-100", ge=0, le=100)] = 0,
                include_scores: Annotated[bool, Field(description="Include detailed scoring information")] = True
            ) -> Dict[str, Any]:
                """Search for documents using the integrated search tools"""
                # Check if server is ready
                if not self.server_ready["status"]:
                    return {
                        "status": "not_ready",
                        "message": f"Server not ready: {self.server_ready['message']}"
                    }
                
                if not self.search_tools or not self.SearchRequest:
                    return {
                        "status": "error", 
                        "message": "Search functionality not available"
                    }
                
                try:
                    search_request = self.SearchRequest(
                        query=query,
                        top_k=top_k,
                        min_quality=min_quality,
                        include_scores=include_scores
                    )
                    results = self.search_tools.search_for_documents(search_request)
                    return {
                        "status": "success",
                        "results": results,
                        "query": query,
                        "total_results": len(results.get("results", []))
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Search failed: {str(e)}"
                    }

        @mcp.tool(
            name="search_and_retrieve_documents",
            description="Search for documents and retrieve their content"
        )
        def search_and_retrieve_documents(
            query: Annotated[str, Field(description="Search query string", min_length=1, max_length=1000)],
            top_k: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=50)] = 10,
            min_quality: Annotated[int, Field(description="Quality cutoff 0-100", ge=0, le=100)] = 0,
            include_scores: Annotated[bool, Field(description="Include detailed scoring information")] = True
        ) -> Dict[str, Any]:
            """Search for documents and retrieve their full content"""
            # Check if server is ready
            if not self.server_ready["status"]:
                return {
                    "status": "not_ready",
                    "message": f"Server not ready: {self.server_ready['message']}"
                }
            
            if not self.search_tools or not self.SearchRequest:
                return {
                    "status": "error", 
                    "message": "Search functionality not available"
                }
            
            try:
                search_request = self.SearchRequest(
                    query=query,
                    top_k=top_k,
                    min_quality=min_quality,
                    include_scores=include_scores
                )
                results = self.search_tools.search_and_get_documents(search_request)
                return {
                    "status": "success",
                    "results": results,
                    "query": query,
                    "total_results": len(results.get("results", []))
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Search and retrieve failed: {str(e)}"
                }

        @mcp.resource(
            uri="docs://document/{document_id}",
            name="document_content", 
            description="Get the complete text of a specified document",
            mime_type="text/markdown"
        )
        def get_document_content(document_id: str) -> str:
            """Get the complete text of a specified document"""
            try:
                if self.document_cache and hasattr(self.document_cache, 'get_document_content'):
                    content = self.document_cache.get_document_content(document_id)
                    return content if content is not None else f"Document '{document_id}' not found"
                else:
                    return f"Document retrieval not available"
            except Exception as e:
                return f"Error retrieving document {document_id}: {str(e)}"

        # Add utility tools
        @mcp.tool()
        def health_check() -> Dict[str, Any]:
            """Check the health status of the documentation server."""
            try:
                # Try to get document count safely
                doc_count = 0
                if self.document_cache and hasattr(self.document_cache, 'documents') and self.document_cache.documents:
                    doc_count = len(self.document_cache.documents)
                else:
                    doc_count = 0
                
                return {
                    "status": "ready" if self.server_ready["status"] else "initializing",
                    "message": self.server_ready["message"],
                    "documents_loaded": doc_count,
                    "search_tools_available": self.search_tools is not None,
                    "search_engines_ready": self.search_tools.get_status() if self.search_tools is not None else "not available",
                    "docs_directory": self.settings.docs_path,
                    "transport": self.settings.transport,
                    "oauth_enabled": self.settings.oauth_enabled
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}"
                }
        
        return mcp

    def create_private_server(self) -> Optional[FastMCP]:
        """Create private documentation server with OAuth authentication following reference pattern."""
        if not self.settings.oauth_enabled:
            return None
            
        if not OAUTH_AVAILABLE:
            logger.error("OAuth enabled but mcp_oauth package not available. Install with: pip install mcp-oauth")
            raise ImportError("mcp_oauth package required for OAuth functionality. Install with: pip install mcp-oauth")
            
        try:
            from mcp_oauth import IntrospectionTokenVerifier
            
            token_verifier = IntrospectionTokenVerifier(
                introspection_endpoint=self.settings.auth_server_introspection_endpoint,
                server_url=str(self.settings.server_url),
                validate_resource=self.settings.oauth_strict,
            )

            name = self.settings.server_name
            resource_server_url = AnyHttpUrl(str(self.settings.server_url) + name)
            
            mcp = FastMCP(
                name=name,
                instructions=f"Private documentation server for {self.settings.description}. Provides authenticated access to restricted documentation and admin tools.",
                debug=True,
                stateless_http=True,
                # Auth configuration for RS mode
                token_verifier=token_verifier,
                auth=AuthSettings(
                    issuer_url=self.settings.auth_server_url,
                    required_scopes=[self.settings.mcp_scope],
                    resource_server_url=resource_server_url,
                ),
            )
            
            # Add all the same tools as public server for authenticated access
            @mcp.tool(
                name="admin_search_for_documents",
                description="Administrative search for documents with enhanced permissions"
            )
            def admin_search_for_documents(
                query: Annotated[str, Field(description="Search query string", min_length=1, max_length=1000)],
                top_k: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=50)] = 10,
                min_quality: Annotated[int, Field(description="Quality cutoff 0-100", ge=0, le=100)] = 0,
                include_scores: Annotated[bool, Field(description="Include detailed scoring information")] = True
            ) -> Dict[str, Any]:
                """Search for documents using the integrated search tools with admin privileges"""
                # Check if server is ready
                if not self.server_ready["status"]:
                    return {
                        "status": "not_ready",
                        "message": f"Server not ready: {self.server_ready['message']}"
                    }
                
                if not self.search_tools or not self.SearchRequest:
                    return {
                        "status": "error", 
                        "message": "Search functionality not available"
                    }
                
                try:
                    search_request = self.SearchRequest(
                        query=query,
                        top_k=top_k,
                        min_quality=min_quality,
                        include_scores=include_scores
                    )
                    results = self.search_tools.search_for_documents(search_request)
                    return {
                        "status": "success",
                        "results": results,
                        "query": query,
                        "total_results": len(results.get("results", [])),
                        "server_type": "private",
                        "auth_required": True
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Search failed: {str(e)}"
                    }

            @mcp.tool()
            def admin_health_check() -> Dict[str, Any]:
                """Administrative health check with detailed server information."""
                try:
                    doc_count = 0
                    if self.document_cache and hasattr(self.document_cache, 'documents') and self.document_cache.documents:
                        doc_count = len(self.document_cache.documents)
                        
                    return {
                        "status": "ready" if self.server_ready["status"] else "initializing",
                        "message": self.server_ready["message"],
                        "documents_loaded": doc_count,
                        "search_tools_available": self.search_tools is not None,
                        "search_engines_ready": self.server_ready["status"],
                        "docs_directory": self.settings.docs_path,
                        "transport": self.settings.transport,
                        "oauth_enabled": self.settings.oauth_enabled,
                        "server_type": "private",
                        "auth_required": True
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"Admin health check failed: {str(e)}"
                    }

            @mcp.resource(
                uri="admin://document/{document_id}",
                name="admin_document_content", 
                description="Get the complete text of a specified document with admin privileges",
                mime_type="text/markdown"
            )
            def admin_get_document_content(document_id: str) -> str:
                """Get the complete text of a specified document with admin access"""
                try:
                    if self.document_cache and hasattr(self.document_cache, 'get_document_content'):
                        content = self.document_cache.get_document_content(document_id)
                        return content if content is not None else f"Document '{document_id}' not found"
                    else:
                        return f"Document retrieval not available"
                except Exception as e:
                    return f"Error retrieving document {document_id}: {str(e)}"
            
            return mcp
            
        except ImportError as e:
            logger.error(f"Failed to import mcp_oauth: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create private server: {e}")
            raise

    def run_oauth_server(self, oauth_settings: OAuthSettings):
        """Run OAuth server following reference pattern."""
        if not OAUTH_AVAILABLE:
            logger.error("OAuth dependencies not available. Install with: pip install mcp-oauth")
            raise ImportError("mcp_oauth package required for OAuth server. Install with: pip install mcp-oauth")

        try:
            from mcp_oauth import OAuthServer, SimpleAuthSettings, AuthServerSettings
            
            server_settings = AuthServerSettings(
                host=oauth_settings.host,
                port=oauth_settings.port,
                server_url=AnyHttpUrl(f"http://{oauth_settings.host}:{oauth_settings.port}"),
                auth_callback_path=f"http://{oauth_settings.host}:{oauth_settings.port}/login",
            )
            
            auth_settings = SimpleAuthSettings(
                superusername=oauth_settings.superusername or "admin",
                superuserpassword=oauth_settings.superuserpassword or "admin",
                mcp_scope="user",
            )
            
            oauth_server = OAuthServer(
                server_settings=server_settings, 
                auth_settings=auth_settings
            )
            
            logger.info(f"Starting OAuth server on {oauth_settings.host}:{oauth_settings.port}")
            logger.info(f"OAuth login at: http://{oauth_settings.host}:{oauth_settings.port}/login")
            oauth_server.run_starlette_server()
            
        except ImportError as e:
            logger.error(f"Failed to import mcp_oauth: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to start OAuth server: {e}")
            raise

    def start_initialization(self):
        """Start the initialization process following the proper sequence."""
        print("Step 6: Initializing DocumentCache...", file=sys.stderr)
        
        if self.document_cache:
            print("Step 7: Successfully instantiated DocumentCache!", file=sys.stderr)
            
            # Load documents - this triggers the callback chain  
            print(f"Step 8: Loading documents from {self.settings.docs_path}...", file=sys.stderr)
            default_file_patterns = ['*.md', '*.txt', '*.html', '*.htm', '*.rst']
            
            # Start async document loading in background thread
            import threading
            def async_document_loading():
                try:
                    import asyncio
                    
                    async def load_documents_async():
                        # Type check to satisfy linter
                        if self.document_cache is None:
                            raise RuntimeError("DocumentCache is None")
                        loaded_count, total_size, error_count = await self.document_cache.load_all_documents(
                            docs_path=self.settings.docs_path,
                            file_patterns=default_file_patterns,
                            max_file_size=self.settings.max_file_size,
                            on_load_fn=self.on_document_cache_ready
                        )
                        print(f"Step 9: Successfully loaded {loaded_count} documents ({total_size} bytes)!", file=sys.stderr)
                    
                    # Run async function in new event loop
                    asyncio.run(load_documents_async())
                    
                except Exception as e:
                    print(f"Step 9: Failed to load documents: {e}", file=sys.stderr)
                    self.server_ready["message"] = f"Document loading failed: {str(e)}"
            
            # Start document loading in background thread
            doc_thread = threading.Thread(
                target=async_document_loading,
                name="document-loader",
                daemon=True
            )
            try:
                doc_thread.start()
                print("Step 9: Document loading started in background thread", file=sys.stderr)
            except Exception as e:
                print(f"Step 9: Failed to start document loading thread: {e}", file=sys.stderr)
                self.server_ready["message"] = f"Failed to start document loading: {str(e)}"
        else:
            print("Step 6-7: DocumentCache not available", file=sys.stderr)
            self.server_ready["message"] = "DocumentCache not available"

    def run_stdio_server(self):
        """Run MCP server in stdio mode. Now synchronous since FastMCP handles async internally."""
        # Start initialization first
        self.start_initialization()
        
        print("Step 12: Creating FastMCP server...", file=sys.stderr)
        public_server = self.create_public_server()
        if public_server is None:
            self.logger.error("Failed to create public server")
            return
        print("Step 13: Advanced MCP tools added successfully", file=sys.stderr)
        
        print("Step 14: Starting server in stdio mode...", file=sys.stderr)
        self.logger.info("Starting MCP server in stdio mode")

        # Let FastMCP itself spin up the stdio transport and session manager:
        try:
            print("Step 15: Server running in stdio mode...", file=sys.stderr)
            # Type assertion to help linter understand public_server is not None
            assert public_server is not None
            
            # Use FastMCP's default run() method (stdio mode)
            print("Step 16: Starting FastMCP default mode (stdio)...", file=sys.stderr)
            # Use the synchronous run() method without transport parameter (defaults to stdio)
            public_server.run()
            print("Step 17: Server finished.", file=sys.stderr)
        except Exception as e:
            self.logger.error(f"Failed to run public server: {e}")


def create_private_server(settings: ServerSettings, doc_cache, search_tools, server_ready) -> Optional[FastMCP]:
    """Create private documentation server with OAuth authentication following reference pattern."""
    if not settings.oauth_enabled:
        return None
        
    if not OAUTH_AVAILABLE:
        logger.error("OAuth enabled but mcp_oauth package not available. Install with: pip install mcp-oauth")
        raise ImportError("mcp_oauth package required for OAuth functionality. Install with: pip install mcp-oauth")
        
    try:
        from mcp_oauth import IntrospectionTokenVerifier
        
        token_verifier = IntrospectionTokenVerifier(
            introspection_endpoint=settings.auth_server_introspection_endpoint,
            server_url=str(settings.server_url),
            validate_resource=settings.oauth_strict,
        )

        name = f"private-{settings.server_name}"
        resource_server_url = AnyHttpUrl(str(settings.server_url) + name)
        
        mcp = FastMCP(
            name=name,
            instructions=f"Private documentation server for {settings.description}. Provides authenticated access to restricted documentation and admin tools.",
            debug=True,
            stateless_http=True,
            # Auth configuration for RS mode
            token_verifier=token_verifier,
            auth=AuthSettings(
                issuer_url=settings.auth_server_url,
                required_scopes=[settings.mcp_scope],
                resource_server_url=resource_server_url,
            ),
        )
        
        # Add all the same tools as public server for authenticated access
        @mcp.tool(
            name="admin_search_for_documents",
            description="Administrative search for documents with enhanced permissions"
        )
        def admin_search_for_documents(
            query: Annotated[str, Field(description="Search query string", min_length=1, max_length=1000)],
            top_k: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=50)] = 10,
            min_quality: Annotated[int, Field(description="Quality cutoff 0-100", ge=0, le=100)] = 0,
            include_scores: Annotated[bool, Field(description="Include detailed scoring information")] = True
        ) -> Dict[str, Any]:
            """Search for documents using the integrated search tools with admin privileges"""
            # Check if server is ready
            if not server_ready["status"]:
                return {
                    "status": "not_ready",
                    "message": f"Server not ready: {server_ready['message']}"
                }
            
            # Import SearchRequest in function scope
            try:
                from models import SearchRequest
            except ImportError:
                return {
                    "status": "error", 
                    "message": "SearchRequest class not available"
                }
            
            if not search_tools:
                return {
                    "status": "error", 
                    "message": "Search functionality not available"
                }
            
            try:
                search_request = SearchRequest(
                    query=query,
                    top_k=top_k,
                    min_quality=min_quality,
                    include_scores=include_scores
                )
                results = search_tools.search_for_documents(search_request)
                return {
                    "status": "success",
                    "results": results,
                    "query": query,
                    "total_results": len(results.get("results", [])),
                    "server_type": "private",
                    "auth_required": True
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Search failed: {str(e)}"
                }

        @mcp.tool()
        def admin_health_check() -> Dict[str, Any]:
            """Administrative health check with detailed server information."""
            try:
                doc_count = 0
                if hasattr(doc_cache, 'documents') and doc_cache.documents:
                    doc_count = len(doc_cache.documents)
                    
                return {
                    "status": "ready" if server_ready["status"] else "initializing",
                    "message": server_ready["message"],
                    "documents_loaded": doc_count,
                    "search_tools_available": search_tools is not None,
                    "search_engines_ready": server_ready["status"],
                    "docs_directory": settings.docs_path,
                    "transport": settings.transport,
                    "oauth_enabled": settings.oauth_enabled,
                    "server_type": "private",
                    "auth_required": True
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Admin health check failed: {str(e)}"
                }

        @mcp.resource(
            uri="admin://document/{document_id}",
            name="admin_document_content", 
            description="Get the complete text of a specified document with admin privileges",
            mime_type="text/markdown"
        )
        def admin_get_document_content(document_id: str) -> str:
            """Get the complete text of a specified document with admin access"""
            try:
                if hasattr(doc_cache, 'get_document_content'):
                    content = doc_cache.get_document_content(document_id)
                    return content if content is not None else f"Document '{document_id}' not found"
                else:
                    return f"Document retrieval not available"
            except Exception as e:
                return f"Error retrieving document {document_id}: {str(e)}"
        
        return mcp
        
    except ImportError as e:
        logger.error(f"Failed to import mcp_oauth: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create private server: {e}")
        raise


def run_oauth_server(oauth_settings: OAuthSettings):
    """Run OAuth server following reference pattern."""
    # Create a dummy settings instance for the MCPServer
    settings = ServerSettings()
    mcp_server = MCPServer(settings, device="auto")  # OAuth server uses auto-detection
    mcp_server.run_oauth_server(oauth_settings)


def run_stdio_server(settings: ServerSettings, device: str = "auto"):
    """Run MCP server in stdio mode. Now synchronous since FastMCP handles async internally."""
    mcp_server = MCPServer(settings, device=device)
    mcp_server.run_stdio_server()


def run_http_server_with_mcp(settings: ServerSettings, device: str = "auto"):
    """Run MCP server in HTTP mode following reference pattern."""
    # Create MCP server instance
    mcp_server = MCPServer(settings, device=device)
    
    # Start initialization process
    mcp_server.start_initialization()
    
    print("Step 12: Creating FastMCP server...", file=sys.stderr)
    
    # Create public server
    public_app = mcp_server.create_public_server()
    if public_app is None:
        logger.error("Failed to create public server")
        return 1
    
    print("Step 13: Adding advanced MCP tools...", file=sys.stderr)
    print("Step 14: Advanced MCP tools added successfully", file=sys.stderr)
    print(f"Step 15: Starting server in {settings.transport.upper()} mode...", file=sys.stderr)
    
    # Create private server if OAuth is enabled
    private_app = None
    if settings.oauth_enabled:
        print("Step 15.1: Creating private OAuth-protected server...", file=sys.stderr)
        try:
            private_app = mcp_server.create_private_server()
            print("Step 15.2: Private server created successfully", file=sys.stderr)
        except ImportError as e:
            print(f"Step 15.2: OAuth functionality requires missing dependencies: {e}", file=sys.stderr)
            print("Install with: pip install mcp-oauth", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Step 15.2: Failed to create private server: {e}", file=sys.stderr)
            return 1
    
    # Start HTTP server with both apps
    run_http_server(public_app, settings, private_app)
    print("Step 16: HTTP/HTTPS server finished.", file=sys.stderr)
    return 0


def run_http_server(mcp_app: FastMCP, settings: ServerSettings, private_app: Optional[FastMCP] = None):
    """Run MCP server in HTTP/HTTPS mode following reference pattern."""
    if not FASTAPI_AVAILABLE:
        logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
        return

    try:
        # Create list of servers to mount
        servers = [mcp_app]
        if private_app:
            servers.append(private_app)
            
        # Update FastAppSettings to handle multiple servers
        class MultiServerFastAppSettings:
            def __init__(self, settings: ServerSettings, servers: List):
                self.expose_url = str(settings.server_url)
                self.dns = None
                self.settings = settings
                self.servers = servers
        
        app_settings = MultiServerFastAppSettings(settings, servers)
        fast_app = FastApp(app_settings)
        app = fast_app.create_app()
        
        # Configure SSL if HTTPS
        ssl_keyfile = settings.ssl_key_path if settings.transport == "https" else None
        ssl_certfile = settings.ssl_cert_path if settings.transport == "https" else None
        
        if settings.transport == "https" and (not ssl_keyfile or not ssl_certfile):
            logger.warning("HTTPS requested but SSL cert/key not provided. Falling back to HTTP.")
            ssl_keyfile = ssl_certfile = None
        
        logger.info(f"Starting MCP server on {settings.host}:{settings.port} ({'HTTPS' if ssl_keyfile else 'HTTP'})")
        if settings.oauth_enabled:
            logger.info("OAuth authentication enabled")
            if private_app:
                logger.info(f"Private server available at: {settings.server_url}private-docs-server/mcp")
            else:
                logger.warning("OAuth enabled but private server creation failed (mcp_oauth dependency required)")
        
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
        raise


def main():
    """Working FastMCP implementation with full server_new.py functionality."""
    import sys
    print("=== BUILD v2.5 - Non-blocking MCP Server with MCPServer class ===", file=sys.stderr)
    
    # Import all necessary components with error handling
    print("Step 1: Importing components...", file=sys.stderr)
    
    # Import existing functionality - using try/except like server_new.py
    try:
        from search_tools import SearchTools
        from models import SearchRequest
        print("Step 1.1: Successfully imported SearchTools and SearchRequest!", file=sys.stderr)
    except ImportError:
        SearchTools = None
        SearchRequest = None
        print("Step 1.1: SearchTools/SearchRequest not available", file=sys.stderr)

    try:
        from document_cache import DocumentCache
        print("Step 1.2: Successfully imported DocumentCache!", file=sys.stderr)
    except ImportError:
        DocumentCache = None
        print("Step 1.2: DocumentCache not available", file=sys.stderr)
        return 1

    print("Step 2: Parsing arguments...", file=sys.stderr)
    
    # Enhanced argument parsing from server_new.py
    parser = argparse.ArgumentParser(
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
    
  For boolean flags (--oauth, --run-oauth-server), set to: true, 1, yes, or on
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-d", "--docs", type=str, 
                       default=os.getenv("MCP_DOCS_PATH"), 
                       help="Path to documentation directory. Set via env var MCP_DOCS_PATH or command line.") 
    parser.add_argument("--transport", choices=["stdio", "http", "https"], 
                       default=os.getenv("MCP_TRANSPORT", "stdio"),
                       help="Transport protocol: 'stdio' for MCP clients, 'http'/'https' for web servers. Default: stdio. Set via env var MCP_TRANSPORT.")
    parser.add_argument("--host", type=str, 
                       default=os.getenv("MCP_HOST", "localhost"), 
                       help="Host address to bind server to (only for http/https transport). Default: localhost. Set via env var MCP_HOST.")
    parser.add_argument("--port", type=int, 
                       default=int(os.getenv("MCP_PORT", "8000")), 
                       help="Port number to bind server to (only for http/https transport). Default: 8000. Set via env var MCP_PORT.")
    parser.add_argument("--oauth", action="store_true", 
                       default=os.getenv("MCP_OAUTH_ENABLED", "").lower() in ("true", "1", "yes", "on"),
                       help="Enable OAuth authentication for protected endpoints. Set via env var MCP_OAUTH_ENABLED=true/false.")
    parser.add_argument("--run-oauth-server", action="store_true", 
                       default=os.getenv("MCP_RUN_OAUTH_SERVER", "").lower() in ("true", "1", "yes", "on"),
                       help="Run standalone OAuth authorization server instead of MCP server. Set via env var MCP_RUN_OAUTH_SERVER=true/false.")
    parser.add_argument("--ssl-cert", type=str, 
                       default=os.getenv("MCP_SSL_CERT_PATH"),
                       help="Path to SSL certificate file for HTTPS transport. Set via env var MCP_SSL_CERT_PATH.")
    parser.add_argument("--ssl-key", type=str, 
                       default=os.getenv("MCP_SSL_KEY_PATH"),
                       help="Path to SSL private key file for HTTPS transport. Set via env var MCP_SSL_KEY_PATH.")
    parser.add_argument("--device", type=str, choices=["cpu", "cuda", "mps", "auto", "none"], 
                       default=os.getenv("MCP_DEVICE", "auto"), 
                       help="Compute device for vector search: 'cpu' (CPU only), 'cuda' (NVIDIA GPU), 'mps' (Apple Silicon), 'auto' (auto-detect best), 'none' (disable vector search). Default: auto. Set via env var MCP_DEVICE.")
    parser.add_argument("-n", "--name", type=str, 
                       default=os.getenv("MCP_SERVER_NAME", "docs-server"),
                       help="Name identifier for the MCP server instance. Default: docs-server. Set via env var MCP_SERVER_NAME.")
    parser.add_argument("--description", type=str, 
                       default=os.getenv("MCP_DESCRIPTION", "company documentation"),
                       help="Human-readable description of the MCP server. Default: 'company documentation'. Set via env var MCP_DESCRIPTION.")
    args = parser.parse_args()
    
    print(f"Step 3: Args parsed - docs: {args.docs}, transport: {args.transport}", file=sys.stderr)
    
    print("Step 3.5: Setting up logging...", file=sys.stderr)
    
    # Set up logging like server_new.py
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    print("Step 3.6: Logging configured", file=sys.stderr)
    
    print("Step 4: Creating settings...", file=sys.stderr)
    
    # Check if running OAuth server first
    if args.run_oauth_server:
        print("Step 4: Running OAuth server...", file=sys.stderr)
        oauth_settings = OAuthSettings()
        try:
            run_oauth_server(oauth_settings)
            return 0
        except Exception as e:
            print(f"Step 4: Failed to start OAuth server: {e}", file=sys.stderr)
            return 1

    # Create settings object with all the advanced options
    settings = ServerSettings(
        docs_path=args.docs or "./docs",
        transport=args.transport,
        host=args.host,
        port=args.port,
        server_url=AnyHttpUrl(f"http{'s' if args.transport == 'https' else ''}://{args.host}:{args.port}"),
        oauth_enabled=args.oauth,
        ssl_cert_path=args.ssl_cert,
        ssl_key_path=args.ssl_key,
        server_name=args.name,
        description=args.description
    )
    
    print(f"Step 5: Settings created - {settings}", file=sys.stderr)
    
    # Handle different transport modes using MCPServer class
    try:
        if settings.transport == "stdio":
            # Changed: Call synchronous run_stdio_server without asyncio.run
            run_stdio_server(settings, device=args.device)
                
        elif settings.transport in ["http", "https"]:
            result = run_http_server_with_mcp(settings, device=args.device)
            return result
        else:
            print(f"Step 6: Unknown transport mode '{settings.transport}'", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
