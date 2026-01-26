# ============================================
# Stage 1: Builder - Build React app
# ============================================
FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (production only for smaller build)
RUN npm ci --only=production

# Install TypeScript and build dependencies
RUN npm install --save-dev typescript @vitejs/plugin-react

# Copy source code
COPY . .

# Build Vite app for web deployment
RUN npm run build

# ============================================
# Stage 2: Runtime - Nginx server
# ============================================
FROM nginx:alpine

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
