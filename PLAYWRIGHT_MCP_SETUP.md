# Playwright MCP Server Setup

## Overview
The Playwright MCP (Model Context Protocol) server has been successfully installed and configured on your system. This allows AI assistants to interact with web browsers for automation tasks.

## Installation Status
✅ Node.js v24.2.0 installed at `C:\Program Files\nodejs`
✅ NPM v11.3.0 available
✅ Playwright MCP Server v0.0.29 installed
✅ Playwright browsers downloaded (Chromium, Firefox, WebKit)

## Files Created
- `start-playwright-mcp.bat` - Batch script to start the MCP server
- `start-playwright-mcp.ps1` - PowerShell script to start the MCP server
- `playwright-mcp-config.json` - Sample MCP configuration
- `PLAYWRIGHT_MCP_SETUP.md` - This documentation file

## Usage

### Starting the MCP Server

#### Option 1: Using Batch File (Recommended)
```cmd
.\start-playwright-mcp.bat
```

#### Option 2: Using PowerShell Script
```powershell
powershell -ExecutionPolicy Bypass -File .\start-playwright-mcp.ps1
```

#### Option 3: Direct Command
```cmd
set PATH=%PATH%;C:\Program Files\nodejs
npx @playwright/mcp
```

### Common Options
- `--version` - Show version information
- `--help` - Show all available options
- `--headless` - Run browser in headless mode
- `--browser chrome` - Use specific browser (chrome, firefox, webkit)
- `--port 3000` - Specify port for the server

### Example Commands
```cmd
# Start with Chrome browser in headless mode
.\start-playwright-mcp.bat --browser chrome --headless

# Start on specific port
.\start-playwright-mcp.bat --port 3000

# Start with specific device emulation
.\start-playwright-mcp.bat --device "iPhone 15"
```

## Configuration for MCP Tools

To add this to your MCP tools configuration, use the following configuration:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp"],
      "env": {
        "PATH": "C:\\Program Files\\nodejs;%PATH%"
      }
    }
  }
}
```

## Troubleshooting

### PATH Issues
If you get "npx not recognized" errors:
1. Use the provided batch/PowerShell scripts
2. Or manually add `C:\Program Files\nodejs` to your system PATH
3. Restart your terminal/IDE after PATH changes

### Permission Issues
If you get PowerShell execution policy errors:
- Use the batch file instead: `.\start-playwright-mcp.bat`
- Or run: `powershell -ExecutionPolicy Bypass -File .\start-playwright-mcp.ps1`

### Browser Installation
If browsers are missing, run:
```cmd
set PATH=%PATH%;C:\Program Files\nodejs
npx playwright install
```

## Next Steps
1. Add the MCP server to your AI assistant's configuration
2. Test browser automation capabilities
3. Explore the available MCP capabilities using `--help`

## Support
- Playwright MCP Documentation: https://github.com/microsoft/playwright-mcp
- Playwright Documentation: https://playwright.dev/
