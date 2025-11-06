# Build stage
FROM node:20-slim AS build

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install dependencies with clean npm cache
RUN npm ci --quiet && \
    npm cache clean --force

# Copy application code
COPY . .

# Accept build argument for API URL
ARG VITE_API_URL=http://localhost:5000
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Install curl for healthcheck and grant nginx permission to bind privileged ports
RUN apk add --no-cache curl libcap && \
    setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Set proper permissions and create nginx cache and runtime directories
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    mkdir -p /var/cache/nginx/client_temp /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp /run && \
    chown -R nginx:nginx /var/cache/nginx /run && \
    chmod -R 755 /var/cache/nginx /run

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

USER nginx

CMD ["nginx", "-g", "daemon off;"]
