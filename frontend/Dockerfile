# ============ BUILD STAGE ============
# Build React application

FROM node:20-alpine as builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --no-audit --no-fund

# Copy source code
COPY . .

# Build production bundle
RUN npm run build

# ============ RUNTIME STAGE ============
# Serve with nginx

FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder
COPY --from=builder /build/dist /usr/share/nginx/html

# Create non-root user
RUN adduser -D -u 101 nginx-runner && \
    chown -R nginx-runner:nginx-runner /usr/share/nginx/html

USER nginx-runner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:3000/ || exit 1

# Expose port
EXPOSE 3000

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
