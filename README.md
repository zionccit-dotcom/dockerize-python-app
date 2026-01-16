# Dockerize a Python Application

> **What you'll create:** A production-ready Docker container for a Python web API, using best practices that companies actually use.

---

## Quick Start

```bash
# 1. Fork this repo to your GitHub account

# 2. Clone YOUR fork
git clone https://github.com/YOUR-USERNAME/dockerize-python-app.git
cd dockerize-python-app

# 3. Complete the challenge (see steps below)

# 4. Push and check your score
git add .
git commit -m "Complete Docker challenge"
git push origin main
# → Check GitHub Actions tab for your score!
```

---

## What is This Challenge?

You have a working Python API. Your job is to **containerize it** so it can run anywhere - your laptop, a server, or the cloud.

**By the end, you'll have:**
- A Dockerfile using multi-stage builds
- An image under 200MB (not 1.2GB!)
- Security best practices (non-root user)
- Docker Compose for local development

---

## Do I Need to Know Docker Already?

**No!** This challenge teaches you Docker from scratch.

**You need:**
- ✅ Basic Python knowledge
- ✅ Completed Challenge 1.1 (RAG Q&A) OR basic Git/terminal skills

**You'll learn:**
- What containers are and why they matter
- How to write Dockerfiles
- Multi-stage builds for smaller images
- Docker Compose for multi-container apps

---

## What You'll Build

| File | What You Create | Points |
|------|-----------------|--------|
| `Dockerfile` | Multi-stage build for the API | 40 |
| `docker-compose.yml` | Local dev environment | 30 |
| `.dockerignore` | Exclude unnecessary files | 10 |
| Security & best practices | Non-root user, health checks | 20 |

---

## Step 0: Install Docker

> ⏱️ **Time:** 10-15 minutes (one-time setup)

### What is Docker?

**Docker** packages your app + all its dependencies into a single "container" that runs the same everywhere.

```
Without Docker:
"It works on my machine!" 😅
→ Different Python versions
→ Missing dependencies
→ Config differences

With Docker:
"It works everywhere!" 🎉
→ Same environment always
→ All dependencies included
→ Identical on laptop, server, cloud
```

### Install Docker Desktop

<details>
<summary>🪟 Windows</summary>

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Download "Docker Desktop for Windows"
3. Run the installer
4. **Important:** Enable WSL 2 when prompted
5. Restart your computer
6. Open Docker Desktop and wait for "Docker is running"

**Verify:**
```bash
docker --version
# Should show: Docker version 24.x or higher
```

</details>

<details>
<summary>🍎 Mac</summary>

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Download for your chip:
   - **Apple Silicon (M1/M2/M3):** "Mac with Apple chip"
   - **Intel:** "Mac with Intel chip"
3. Drag to Applications
4. Open Docker Desktop
5. Wait for "Docker is running"

**Verify:**
```bash
docker --version
```

</details>

<details>
<summary>🐧 Linux</summary>

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify:
docker --version
```

</details>

### Test Docker is Working

```bash
docker run hello-world
```

You should see: "Hello from Docker! This message shows that your installation appears to be working correctly."

✅ **Checkpoint:** Docker is installed and working

---

## Step 1: Understand the App

Before containerizing, let's understand what we're working with.

### The Application

Look at `src/app.py` - it's a simple Flask API:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/greeting/<name>')
def greeting(name):
    return jsonify({"message": f"Hello, {name}!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Run It Locally First

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/app.py
```

Test it: http://localhost:5000/health

✅ **Checkpoint:** App runs locally

---

## Step 2: Understand Docker Concepts

Before writing a Dockerfile, let's understand the key concepts.

### Images vs Containers

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| **Image** | A blueprint/template | A recipe |
| **Container** | A running instance of an image | A cake made from the recipe |

You **build** an image once, then **run** many containers from it.

### Dockerfile Instructions

| Instruction | What It Does | Example |
|-------------|-------------|---------|
| `FROM` | Base image to start from | `FROM python:3.11` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `COPY` | Copy files into image | `COPY . .` |
| `RUN` | Execute a command | `RUN pip install flask` |
| `EXPOSE` | Document which port the app uses | `EXPOSE 5000` |
| `CMD` | Command to run when container starts | `CMD ["python", "app.py"]` |

### A Simple Dockerfile

```dockerfile
# Start from Python base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Document the port
EXPOSE 5000

# Run the app
CMD ["python", "src/app.py"]
```

**This works, but it has problems:**
- ❌ Image is ~1GB (too big!)
- ❌ Runs as root (security risk)
- ❌ No health check
- ❌ Includes unnecessary files

**Your job:** Fix these problems!

---

## Step 3: Write a Multi-Stage Dockerfile

> ⏱️ **Time:** 30-40 minutes

### What is Multi-Stage Building?

Multi-stage builds use multiple `FROM` statements. Each stage can:
- Install build tools
- Compile code
- Then copy ONLY what's needed to the final image

```
Stage 1 (builder):          Stage 2 (final):
┌─────────────────────┐     ┌─────────────────────┐
│ Full Python image   │     │ Slim Python image   │
│ + build tools       │ ──► │ + just the app      │
│ + source code       │     │ + dependencies      │
│ = 1.2 GB            │     │ = 150 MB            │
└─────────────────────┘     └─────────────────────┘
```

### Your Task

Open `Dockerfile` and implement a multi-stage build.

**Requirements:**
- [ ] Use `python:3.11-slim` for the final image (not full Python)
- [ ] Final image must be under 200MB
- [ ] Run as non-root user
- [ ] Include a health check
- [ ] Don't copy unnecessary files (use `.dockerignore`)

### Step-by-Step Guide

<details>
<summary>💡 Hint 1: Multi-Stage Structure</summary>

```dockerfile
# Stage 1: Builder
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/

# ... rest of your Dockerfile
```

</details>

<details>
<summary>💡 Hint 2: Non-Root User</summary>

Running as root is a security risk. Create a dedicated user:

```dockerfile
# Create non-root user
RUN useradd --create-home appuser
USER appuser
```

But wait! If you copy to `/root/.local`, the non-root user can't access it.

**Fix:** Install packages to a location the user can access:

```dockerfile
# In builder stage:
RUN pip install --prefix=/install -r requirements.txt

# In final stage:
COPY --from=builder /install /usr/local
```

</details>

<details>
<summary>💡 Hint 3: Health Check</summary>

Docker can automatically check if your app is healthy:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

But `curl` isn't installed in slim images! Use Python instead:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1
```

</details>

<details>
<summary>💡 Hint 4: Environment Variables</summary>

Don't hardcode settings. Use environment variables:

```dockerfile
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

EXPOSE $FLASK_RUN_PORT
```

</details>

<details>
<summary>🎯 Full Solution (only if completely stuck!)</summary>

```dockerfile
# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11 AS builder

WORKDIR /app

# Install dependencies to a specific location
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Final (Production)
# ============================================
FROM python:3.11-slim

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Set environment variables
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Document the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "src/app.py"]
```

</details>

### Test Your Dockerfile

```bash
# Build the image
docker build -t myapp .

# Check image size (should be < 200MB)
docker images myapp

# Run the container
docker run -p 5000:5000 myapp

# Test it
curl http://localhost:5000/health
```

### Common Mistakes

| Error | Cause | Fix |
|-------|-------|-----|
| `pip: command not found` | Wrong base image | Use `python:3.11-slim`, not `alpine` |
| Permission denied | Running as non-root but files owned by root | Use `COPY --chown=appuser:appuser` |
| Health check fails | `curl` not installed | Use Python urllib instead |
| Image too big | Using full Python image | Use `python:3.11-slim` in final stage |

---

## Step 4: Create .dockerignore

> ⏱️ **Time:** 5 minutes

### Why .dockerignore?

When you run `docker build`, Docker sends ALL files to the build context. A `.dockerignore` file excludes unnecessary files, making builds faster and images smaller.

### Your Task

Create `.dockerignore` with these patterns:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
ENV/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose*.yml
.dockerignore

# Tests (not needed in production image)
tests/
pytest.ini

# Misc
*.md
*.txt
!requirements.txt
```

**Note:** `!requirements.txt` means "DO include requirements.txt" (exception to `*.txt`).

---

## Step 5: Create Docker Compose

> ⏱️ **Time:** 20-30 minutes

### What is Docker Compose?

Docker Compose lets you define multi-container applications in a YAML file.

**Without Compose:**
```bash
docker network create mynet
docker run -d --name db --network mynet postgres
docker run -d --name app --network mynet -p 5000:5000 myapp
# Lots of commands to remember!
```

**With Compose:**
```bash
docker-compose up
# One command does everything!
```

### Your Task

Create `docker-compose.yml` that:
- [ ] Runs your API
- [ ] Runs a Redis cache (for future use)
- [ ] Sets up networking between them
- [ ] Uses volumes for development (live reload)

### Step-by-Step Guide

<details>
<summary>💡 Hint 1: Basic Structure</summary>

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
```

</details>

<details>
<summary>💡 Hint 2: Add Redis</summary>

```yaml
services:
  api:
    # ... your api config
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

</details>

<details>
<summary>💡 Hint 3: Development Volumes</summary>

For development, mount your code so changes reflect immediately:

```yaml
services:
  api:
    volumes:
      - ./src:/app/src:ro  # Mount source code (read-only)
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
```

</details>

<details>
<summary>💡 Hint 4: Health Checks in Compose</summary>

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
```

</details>

<details>
<summary>🎯 Full Solution</summary>

```yaml
version: '3.8'

services:
  # Python API
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./src:/app/src:ro
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

volumes:
  redis_data:
```

</details>

### Test Docker Compose

```bash
# Start everything
docker-compose up --build

# In another terminal, test the API
curl http://localhost:5000/health

# Stop everything
docker-compose down
```

---

## Step 6: Run Tests & Submit

### Local Testing

```bash
python run.py
```

You'll see:
```
  ============================================================
    🐳 Dockerize Python App Challenge
  ============================================================

  ✅ [Step 1] Dockerfile exists
  ✅ [Step 2] Multi-stage build used
  ✅ [Step 3] Image size < 200MB (142MB)
  ✅ [Step 4] Non-root user configured
  ✅ [Step 5] Health check defined
  ✅ [Step 6] .dockerignore exists
  ✅ [Step 7] docker-compose.yml works

  Overall Progress:
  ████████████████████ 100% (7/7 steps)

  🎉 CHALLENGE COMPLETE!
```

### Submit to GitHub

```bash
git add .
git commit -m "Complete Docker challenge"
git push origin main
```

Check the **Actions** tab for your score!

---

## Understanding Docker (For DevOps Students)

### Key Concepts You Learned

| Concept | What It Is | Why It Matters |
|---------|-----------|----------------|
| **Image** | Packaged app + dependencies | Consistent deployments |
| **Container** | Running instance | Isolated, reproducible |
| **Multi-stage** | Build in one image, run in another | Smaller final images |
| **Layers** | Each instruction creates a layer | Caching, efficiency |
| **Non-root** | Don't run as root | Security |
| **Health check** | App self-reporting | Orchestration, monitoring |

### Docker Commands Cheat Sheet

```bash
# Build
docker build -t myapp .              # Build image
docker build -t myapp:v1.0 .         # Build with tag

# Run
docker run myapp                     # Run container
docker run -d myapp                  # Run in background
docker run -p 5000:5000 myapp        # Map port
docker run -e VAR=value myapp        # Set env var
docker run -v ./src:/app/src myapp   # Mount volume

# Manage
docker ps                            # List running containers
docker ps -a                         # List all containers
docker stop <id>                     # Stop container
docker rm <id>                       # Remove container
docker logs <id>                     # View logs

# Images
docker images                        # List images
docker rmi <image>                   # Remove image
docker image prune                   # Remove unused images

# Compose
docker-compose up                    # Start all services
docker-compose up -d                 # Start in background
docker-compose up --build            # Rebuild images
docker-compose down                  # Stop all services
docker-compose logs                  # View all logs
```

### What You Can Say in Interviews

> "I containerized a Python application using Docker multi-stage builds, reducing the image size from 1.2GB to 150MB. I implemented security best practices including running as a non-root user, added health checks for orchestration compatibility, and created a Docker Compose configuration for local development with Redis. I understand Docker layers, caching, and how to optimize builds."

---

## Troubleshooting

<details>
<summary>❌ "docker: command not found"</summary>

Docker Desktop is not installed or not in PATH.

1. Install Docker Desktop (see Step 0)
2. Make sure it's running (look for whale icon)
3. Restart your terminal

</details>

<details>
<summary>❌ "Cannot connect to Docker daemon"</summary>

Docker Desktop is installed but not running.

1. Open Docker Desktop
2. Wait for "Docker is running"
3. Try again

</details>

<details>
<summary>❌ Image is too big (> 200MB)</summary>

Check these:
1. Using `python:3.11-slim` in final stage?
2. Using `--no-cache-dir` with pip?
3. Not copying unnecessary files?
4. `.dockerignore` configured?

</details>

<details>
<summary>❌ Health check keeps failing</summary>

1. Is the app actually running? Check logs: `docker logs <container_id>`
2. Is the health endpoint correct? `/health` not `/healthz`
3. Is curl installed? Use Python urllib instead

</details>

---

## What You Learned

By completing this challenge:

- ✅ **Docker basics** - Images, containers, builds
- ✅ **Dockerfile writing** - Instructions and best practices
- ✅ **Multi-stage builds** - Smaller, production-ready images
- ✅ **Security** - Non-root users, minimal images
- ✅ **Docker Compose** - Multi-container development
- ✅ **Health checks** - Self-reporting apps

---

## Next Challenge

Continue your DevOps journey:
- **1.3 CI/CD Pipeline** - Automate testing and deployment

Or revisit:
- **1.1 RAG Document Q&A** - Learn Git and GitHub Actions

Good luck! 🐳
