
# Build stage
FROM node:22-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm globally and install dependencies with build scripts enabled
RUN npm install -g pnpm && pnpm config set enable-pre-post-scripts true && pnpm install --shamefully-hoist

# Copy source code
COPY . .

# Build the application using pnpm
RUN pnpm build

# Production stage using Nginx
FROM nginx:stable-alpine

# Copy the built React app to Nginx's default public directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration (optional, for SPA routing etc.)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Command to start Nginx (default command for nginx:stable-alpine)
CMD ["nginx", "-g", "daemon off;"]

