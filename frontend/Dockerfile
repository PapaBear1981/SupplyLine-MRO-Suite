FROM node:20-alpine as build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
# Set the version in package.json
RUN sed -i 's/"version": ".*"/"version": "1.3.0"/' package.json
RUN npm ci

# Copy the rest of the application
COPY . .

# Make the version update script executable
COPY update_version.sh .
RUN chmod +x update_version.sh
RUN ./update_version.sh

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
