# Docker Advanced Reference

## Multi-Stage Builds

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

## Networking

### Create Network

```bash
docker network create mynet
docker network create --driver bridge mynet
docker network ls
docker network inspect mynet
```

### Connect Containers

```bash
docker run -d --name web --network mynet nginx
docker run -d --name db --network mynet postgres

# web can reach db at hostname "db"
```

### Compose Networking

```yaml
services:
  web:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend

networks:
  frontend:
  backend:
```

## Volumes

### Named Volumes

```bash
docker volume create mydata
docker run -v mydata:/app/data myimage

# List/inspect
docker volume ls
docker volume inspect mydata
```

### Bind Mounts

```bash
docker run -v $(pwd):/app myimage
docker run -v /host/path:/container/path:ro myimage  # Read-only
```

### tmpfs (Memory)

```bash
docker run --tmpfs /tmp myimage
```

## Resource Limits

```bash
# Memory
docker run -m 512m myimage
docker run --memory-swap 1g myimage

# CPU
docker run --cpus 2 myimage
docker run --cpu-shares 512 myimage
```

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1
```

```yaml
# docker-compose.yml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## Image Optimization

### Layer Caching

```dockerfile
# Bad: Busts cache on any code change
COPY . .
RUN npm install

# Good: Dependencies cached separately
COPY package*.json ./
RUN npm ci
COPY . .
```

### Reduce Size

```dockerfile
# Use alpine
FROM node:18-alpine

# Multi-stage (don't include build tools in final image)

# Clean up in same layer
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
 && rm -rf /var/lib/apt/lists/*

# Use .dockerignore
```

### .dockerignore

```
node_modules
.git
*.md
.env
dist
coverage
```

## Compose Profiles

```yaml
services:
  web:
    image: myapp

  debug:
    image: myapp-debug
    profiles: ["debug"]

  test:
    image: myapp-test
    profiles: ["test"]
```

```bash
docker compose up                    # Only web
docker compose --profile debug up    # web + debug
```

## Compose Override

```yaml
# docker-compose.yml (base)
services:
  web:
    image: myapp
    ports:
      - "80:80"

# docker-compose.override.yml (auto-loaded)
services:
  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "3000:80"
```

## BuildKit

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Or in daemon.json
{ "features": { "buildkit": true } }

# Build with BuildKit features
docker build --secret id=mysecret,src=secret.txt .
```

## Registry

```bash
# Login
docker login registry.example.com

# Tag for registry
docker tag myapp:latest registry.example.com/myapp:latest

# Push
docker push registry.example.com/myapp:latest

# Pull
docker pull registry.example.com/myapp:latest
```

## Debugging Containers

```bash
# Attach to running
docker attach container_name

# Shell into running
docker exec -it container_name sh

# Inspect
docker inspect container_name
docker inspect --format '{{.State.Health.Status}}' container_name

# Logs
docker logs -f --tail 100 container_name

# Events
docker events --filter container=container_name

# Resource usage
docker stats container_name
```
