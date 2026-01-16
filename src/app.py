"""
Simple Flask API for Docker Challenge
=====================================
This is the application you will containerize.
DO NOT MODIFY this file - focus on the Dockerfile and docker-compose.yml
"""

from flask import Flask, jsonify
import os
import redis
from datetime import datetime

app = Flask(__name__)

# Redis connection (optional - for docker-compose challenge)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = None

def get_redis():
    """Get Redis client (lazy initialization)."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(redis_url)
            redis_client.ping()
        except:
            redis_client = None
    return redis_client


@app.route('/')
def home():
    """Home endpoint."""
    return jsonify({
        "app": "Docker Challenge API",
        "version": "1.0.0",
        "endpoints": ["/health", "/api/greeting/<name>", "/api/counter"]
    })


@app.route('/health')
def health():
    """Health check endpoint - used by Docker HEALTHCHECK."""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "app": "ok"
        }
    }

    # Check Redis if available
    r = get_redis()
    if r:
        try:
            r.ping()
            status["checks"]["redis"] = "ok"
        except:
            status["checks"]["redis"] = "unavailable"
    else:
        status["checks"]["redis"] = "not configured"

    return jsonify(status)


@app.route('/api/greeting/<name>')
def greeting(name):
    """Greeting endpoint."""
    return jsonify({
        "message": f"Hello, {name}!",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/counter')
def counter():
    """Counter endpoint - demonstrates Redis usage."""
    r = get_redis()

    if r:
        try:
            count = r.incr('visit_counter')
            return jsonify({
                "count": count,
                "storage": "redis"
            })
        except Exception as e:
            return jsonify({
                "error": str(e),
                "storage": "redis"
            }), 500
    else:
        # Fallback without Redis
        return jsonify({
            "message": "Redis not available - counter not persistent",
            "storage": "none"
        })


@app.route('/api/info')
def info():
    """System info endpoint - useful for debugging containers."""
    import platform
    import sys

    return jsonify({
        "python_version": sys.version,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "user": os.getenv('USER', os.getenv('USERNAME', 'unknown')),
        "environment": os.getenv('FLASK_ENV', 'production')
    })


if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', '0') == '1'

    print(f"Starting server on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
