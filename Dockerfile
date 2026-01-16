# ============================================
# Dockerize Python App Challenge
# ============================================
#
# YOUR TASK: Create a production-ready Dockerfile
#
# Requirements:
# 1. Use multi-stage build (builder + final stages)
# 2. Final image must be under 200MB
# 3. Run as non-root user (security)
# 4. Include a health check
# 5. Use python:3.11-slim for the final image
#
# Hints:
# - Stage 1 (builder): Install dependencies
# - Stage 2 (final): Copy only what's needed
# - Use --prefix=/install with pip to control where packages go
# - Create a user with: RUN useradd --create-home appuser
# - Health check can use Python urllib (curl not in slim image)
#
# ============================================

# TODO: Implement your Dockerfile here!
#
# Delete everything below and write your own.
# See README.md for step-by-step hints.

# This is a BROKEN starter - it works but has problems:
# - Image is too big (~1GB)
# - Runs as root (insecure)
# - No health check
# - No multi-stage build

FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python", "src/app.py"]
