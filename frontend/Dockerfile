# Stage 1: Build the app
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the app
RUN npm run build

# Stage 2: Serve the built app with a lightweight web server
FROM node:20-alpine AS runner

WORKDIR /app

# Install a simple static file server
RUN npm install -g serve

# Copy built files from builder
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./

# Expose the port (change if your app uses a different port)
EXPOSE 4173

# Start the app
CMD ["serve", "-s", "build", "-l", "4173"]
