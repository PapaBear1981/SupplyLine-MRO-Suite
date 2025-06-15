# Build stage
FROM node:20-slim AS build

WORKDIR /app

# Accept build arguments for API URL configuration
ARG VITE_API_URL=http://localhost:5000
ENV VITE_API_URL=${VITE_API_URL}

# Copy package files for dependency installation
COPY package*.json ./

# Install dependencies with clean npm cache
RUN npm ci --quiet && \
    npm cache clean --force

# Copy application code
COPY . .

# Build the application with environment variables
RUN npm run build

# Production stage
FROM nginx:stable-alpine

# Install curl for healthcheck and envsubst for environment variable substitution
RUN apk add --no-cache curl gettext

# Copy the nginx configuration template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Set proper permissions
RUN chmod -R 755 /usr/share/nginx/html

# Set default PORT environment variable
ENV PORT=80

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:$PORT/ || exit 1

# Start nginx with environment variable substitution
CMD ["sh", "-c", "envsubst '$$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
