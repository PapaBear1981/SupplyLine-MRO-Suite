#!/usr/bin/env node

/**
 * Portable HTTP Server for SupplyLine MRO Suite PWA
 * 
 * This server provides a simple way to run the PWA locally without installation.
 * Perfect for USB deployment or local testing.
 */

const express = require('express');
const serveStatic = require('serve-static');
const path = require('path');
const fs = require('fs');
const open = require('open');

class PortableServer {
  constructor() {
    this.app = express();
    this.port = process.env.PORT || 3000;
    this.host = process.env.HOST || 'localhost';
    this.frontendPath = path.join(__dirname, '../frontend/dist');
    this.autoOpen = process.env.AUTO_OPEN !== 'false';
  }

  setupMiddleware() {
    // Security headers
    this.app.use((req, res, next) => {
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
      
      // PWA specific headers
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
      
      next();
    });

    // Serve static files from frontend/dist with proper MIME types
    this.app.use(serveStatic(this.frontendPath, {
      maxAge: 0, // No caching for development
      etag: false,
      lastModified: false,
      setHeaders: (res, path) => {
        // Set proper MIME types for JavaScript modules
        if (path.endsWith('.js')) {
          res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
        } else if (path.endsWith('.mjs')) {
          res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
        } else if (path.endsWith('.css')) {
          res.setHeader('Content-Type', 'text/css; charset=utf-8');
        } else if (path.endsWith('.json')) {
          res.setHeader('Content-Type', 'application/json; charset=utf-8');
        } else if (path.endsWith('.html')) {
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
        }
      }
    }));

    // Handle client-side routing - serve index.html for navigation requests only
    this.app.get('*', (req, res) => {
      // Don't serve index.html for asset requests
      if (req.path.startsWith('/assets/') ||
          req.path.includes('.') && !req.path.endsWith('.html')) {
        return res.status(404).send('Asset not found');
      }

      const indexPath = path.join(this.frontendPath, 'index.html');

      if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
      } else {
        res.status(404).send(`
          <html>
            <head><title>SupplyLine MRO Suite - Not Found</title></head>
            <body>
              <h1>Frontend Not Built</h1>
              <p>The frontend application hasn't been built yet.</p>
              <p>Please run: <code>npm run frontend:build</code></p>
              <p>Expected location: <code>${this.frontendPath}</code></p>
            </body>
          </html>
        `);
      }
    });
  }

  async findAvailablePort(startPort) {
    const net = require('net');
    
    return new Promise((resolve) => {
      const server = net.createServer();
      
      server.listen(startPort, (err) => {
        if (err) {
          server.close();
          resolve(this.findAvailablePort(startPort + 1));
        } else {
          const port = server.address().port;
          server.close();
          resolve(port);
        }
      });
    });
  }

  async start() {
    this.setupMiddleware();

    // Find available port
    this.port = await this.findAvailablePort(this.port);

    return new Promise((resolve, reject) => {
      const server = this.app.listen(this.port, this.host, (err) => {
        if (err) {
          reject(err);
          return;
        }

        const url = `http://${this.host}:${this.port}`;
        
        console.log('🚀 SupplyLine MRO Suite PWA Server Started!');
        console.log('==========================================');
        console.log(`📍 Server URL: ${url}`);
        console.log(`📁 Serving from: ${this.frontendPath}`);
        console.log(`🌐 Host: ${this.host}`);
        console.log(`🔌 Port: ${this.port}`);
        console.log('==========================================');
        console.log('💡 Tips:');
        console.log('  • Press Ctrl+C to stop the server');
        console.log('  • Use AUTO_OPEN=false to disable auto-opening browser');
        console.log('  • Use PORT=8080 to specify a different port');
        console.log('  • Use HOST=0.0.0.0 to allow external connections');
        console.log('==========================================');

        // Auto-open browser if enabled
        if (this.autoOpen) {
          console.log('🌐 Opening browser...');
          open(url).catch(err => {
            console.log('⚠️  Could not auto-open browser:', err.message);
            console.log(`   Please manually open: ${url}`);
          });
        }

        resolve({ server, url, port: this.port, host: this.host });
      });

      // Graceful shutdown
      process.on('SIGINT', () => {
        console.log('\n🛑 Shutting down server...');
        server.close(() => {
          console.log('✅ Server stopped gracefully');
          process.exit(0);
        });
      });

      process.on('SIGTERM', () => {
        console.log('\n🛑 Received SIGTERM, shutting down...');
        server.close(() => {
          console.log('✅ Server stopped gracefully');
          process.exit(0);
        });
      });
    });
  }
}

// CLI usage
if (require.main === module) {
  const server = new PortableServer();
  
  server.start().catch(err => {
    console.error('❌ Failed to start server:', err);
    process.exit(1);
  });
}

module.exports = PortableServer;
