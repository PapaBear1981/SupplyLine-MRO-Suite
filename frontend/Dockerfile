# Build stage
FROM node:18-slim as build

# Set environment variables
ENV NODE_ENV=production \
    NPM_CONFIG_LOGLEVEL=warn

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies with exact versions and clean cache
RUN npm ci --production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Create a non-root user to run nginx
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Set proper permissions
RUN chown -R appuser:appgroup /var/cache/nginx && \
    chown -R appuser:appgroup /var/log/nginx && \
    chown -R appuser:appgroup /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R appuser:appgroup /var/run/nginx.pid

# Copy the nginx configuration with security headers
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Set proper permissions for the application files
RUN chown -R appuser:appgroup /usr/share/nginx/html

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
