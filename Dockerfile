# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for building wheels etc.)
RUN apt-get update && apt-get install -y build-essential

# Install `uv` as package manager
RUN pip install --no-cache-dir uv

# Copy project metadata and install deps
COPY pyproject.toml .
RUN uv pip install --system -e .

# Copy source code
COPY . .

# Run FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
