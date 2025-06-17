# PowerShell script to start Playwright MCP Server
# This script ensures Node.js is in the PATH and starts the MCP server

# Add Node.js to PATH for this session
$env:PATH = $env:PATH + ";C:\Program Files\nodejs"

# Start the Playwright MCP server
Write-Host "Starting Playwright MCP Server..."
Write-Host "Node.js version: $(node --version)"
Write-Host "NPX version: $(npx --version)"
Write-Host ""

# You can add additional arguments here as needed
# For example: --headless, --browser chrome, etc.
& npx @playwright/mcp $args
