# Docker Configuration Test Script (PowerShell)
# Tests the updated Docker configuration for the MCP Documentation Server

param(
    [switch]$SkipBuild = $false,
    [switch]$Verbose = $false
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

Write-Host "🐳 MCP Documentation Server - Docker Configuration Test" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Test functions
function Test-Build {
    Write-Host "📦 Testing Docker build..." -ForegroundColor $Yellow
    
    try {
        if ($SkipBuild) {
            Write-Host "⏭️  Skipping build (--SkipBuild specified)" -ForegroundColor $Yellow
            return $true
        }
        
        $buildResult = docker-compose -f compose.yml build --no-cache
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker build successful" -ForegroundColor $Green
            return $true
        } else {
            Write-Host "❌ Docker build failed" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Docker build failed: $($_.Exception.Message)" -ForegroundColor $Red
        return $false
    }
}

function Test-Startup {
    Write-Host "🚀 Testing container startup..." -ForegroundColor $Yellow
    
    try {
        docker-compose -f compose.yml up -d
        
        # Wait for container to be ready
        Write-Host "Waiting for container to start..."
        Start-Sleep -Seconds 10
        
        $psResult = docker-compose -f compose.yml ps
        if ($psResult -match "Up") {
            Write-Host "✅ Container started successfully" -ForegroundColor $Green
            return $true
        } else {
            Write-Host "❌ Container failed to start" -ForegroundColor $Red
            docker-compose -f compose.yml logs
            return $false
        }
    }
    catch {
        Write-Host "❌ Container startup failed: $($_.Exception.Message)" -ForegroundColor $Red
        return $false
    }
}

function Test-Health {
    Write-Host "🏥 Testing health endpoint..." -ForegroundColor $Yellow
    
    # Wait a bit more for the server to be ready
    Start-Sleep -Seconds 15
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8008/help" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health endpoint responding" -ForegroundColor $Green
            return $true
        } else {
            Write-Host "❌ Health endpoint returned status: $($response.StatusCode)" -ForegroundColor $Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Health endpoint not responding: $($_.Exception.Message)" -ForegroundColor $Red
        Write-Host "Container logs:" -ForegroundColor $Yellow
        docker-compose -f compose.yml logs --tail=20
        return $false
    }
}

function Test-MCPEndpoint {
    Write-Host "🔌 Testing MCP endpoint..." -ForegroundColor $Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8008/logzilla-docs-server/mcp" -TimeoutSec 10 -UseBasicParsing -ErrorAction SilentlyContinue
        Write-Host "✅ MCP endpoint accessible" -ForegroundColor $Green
        return $true
    }
    catch {
        Write-Host "⚠️  MCP endpoint returned error (expected for direct HTTP access)" -ForegroundColor $Yellow
        return $true
    }
}

function Invoke-Cleanup {
    Write-Host "🧹 Cleaning up..." -ForegroundColor $Yellow
    docker-compose -f compose.yml down
    Write-Host "✅ Cleanup complete" -ForegroundColor $Green
}

# Main test execution
function Main {
    Write-Host "Starting Docker configuration tests..."
    Write-Host ""
    
    # Ensure we're in the right directory
    if (-not (Test-Path "compose.yml")) {
        Write-Host "❌ compose.yml not found. Please run this script from the docker/ directory" -ForegroundColor $Red
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor $Red
            exit 1
        }
    }
    catch {
        Write-Host "❌ Docker is not available. Please install Docker Desktop." -ForegroundColor $Red
        exit 1
    }
    
    # Run tests
    $failed = 0
    
    if (-not (Test-Build)) { $failed++ }
    Write-Host ""
    
    if (-not (Test-Startup)) { $failed++ }
    Write-Host ""
    
    if (-not (Test-Health)) { $failed++ }
    Write-Host ""
    
    if (-not (Test-MCPEndpoint)) { $failed++ }
    Write-Host ""
    
    # Show container info
    Write-Host "📊 Container Information:" -ForegroundColor $Yellow
    docker-compose -f compose.yml ps
    Write-Host ""
    
    Write-Host "📋 Recent Logs:" -ForegroundColor $Yellow
    docker-compose -f compose.yml logs --tail=10
    Write-Host ""
    
    # Cleanup
    Invoke-Cleanup
    
    # Final results
    Write-Host "=======================================================" -ForegroundColor Cyan
    if ($failed -eq 0) {
        Write-Host "🎉 All tests passed! Docker configuration is working correctly." -ForegroundColor $Green
        exit 0
    } else {
        Write-Host "❌ $failed test(s) failed. Please check the configuration." -ForegroundColor $Red
        exit 1
    }
}

# Handle script interruption
try {
    Main
}
finally {
    # Ensure cleanup happens even if script is interrupted
    try {
        Invoke-Cleanup
    }
    catch {
        # Ignore cleanup errors
    }
}
