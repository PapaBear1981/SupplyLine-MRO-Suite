@echo off
REM Batch script to start Playwright MCP Server
REM This script ensures Node.js is in the PATH and starts the MCP server

echo Adding Node.js to PATH...
set PATH=%PATH%;C:\Program Files\nodejs

echo Starting Playwright MCP Server...
echo Node.js version:
node --version
echo NPX version:
npx --version
echo.

REM Start the Playwright MCP server with any passed arguments
npx @playwright/mcp %*
