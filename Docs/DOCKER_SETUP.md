# Docker Setup Guide for ClinIQ

This guide explains how to run ClinIQ using Docker, so you don't need to install Node.js or Python dependencies directly on your system.

## Prerequisites

- **Docker Desktop** installed on your system
  - Download from: https://www.docker.com/products/docker-desktop/
  - Install and make sure Docker Desktop is running

## Quick Start

### 1. Build and Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build the backend (Flask API) container
- Build the frontend (React) container
- Start both services
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

### 2. Run in Detached Mode (Background)

```bash
docker-compose up -d --build
```

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### 4. Stop the Services

```bash
docker-compose down
```

## Individual Container Commands

### Run Backend Only

```bash
# Build backend image
docker build -f Dockerfile.backend -t cliniq-backend .

# Run backend container
docker run -p 5000:5000 \
  -v "${PWD}/.chromadb:/app/.chromadb" \
  -v "${PWD}/uploads:/app/uploads" \
  cliniq-backend
```

### Run Frontend Only

```bash
# Build frontend image
cd frontend
docker build -t cliniq-frontend .

# Run frontend container
docker run -p 3000:3000 \
  -v "${PWD}:/app" \
  -v /app/node_modules \
  cliniq-frontend
```

## Development Mode

The Docker setup includes volume mounts for development:

- **Backend**: Code changes require container restart
- **Frontend**: Code changes are hot-reloaded automatically

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

## Troubleshooting

### Port Already in Use

If ports 3000 or 5000 are already in use:

1. Edit `docker-compose.yml`
2. Change the port mappings:
   ```yaml
   ports:
     - "3001:3000"  # Frontend on different port
     - "5001:5000"  # Backend on different port
   ```

### Rebuild After Dependency Changes

If you modify `package.json` or `requirements.txt`:

```bash
docker-compose up --build --force-recreate
```

### Clear Docker Cache

```bash
# Remove all containers and images
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose up --build
```

### Check Container Status

```bash
# List running containers
docker-compose ps

# Check container logs
docker-compose logs backend
docker-compose logs frontend
```

### Access Container Shell

```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh
```

## Production Build

For production, you'll want to build optimized images:

### Frontend Production Build

Edit `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Production

Use a production WSGI server like Gunicorn:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
```

## File Structure

```
.
├── docker-compose.yml      # Orchestrates both services
├── Dockerfile.backend      # Backend container definition
├── frontend/
│   ├── Dockerfile          # Frontend container definition
│   └── .dockerignore       # Files to exclude from build
└── .dockerignore           # Root level ignore file
```

## Environment Variables

You can set environment variables in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - FLASK_ENV=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  frontend:
    environment:
      - VITE_BACKEND_ENDPOINT=http://backend:5000
```

## Benefits of Docker Setup

✅ **No local Node.js installation needed**  
✅ **No local Python environment setup**  
✅ **Consistent environment across machines**  
✅ **Easy to share and deploy**  
✅ **Isolated dependencies**  
✅ **Easy cleanup** (just `docker-compose down`)

## Next Steps

1. Install Docker Desktop
2. Run `docker-compose up --build`
3. Open http://localhost:3000 in your browser
4. Start using ClinIQ!


