# Use Ubuntu 24.04 as base image
FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3-full \
    python3-pip \
    python3-venv \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package files
COPY . .

# Install the package in editable mode
RUN pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8080

# Create temp_audio directory
RUN mkdir -p /app/podcastfy/api/temp_audio

# Verify installations
RUN echo "Verifying installations:" && \
    echo "Ubuntu version:" && cat /etc/os-release && \
    echo "FFmpeg version:" && ffmpeg -version && \
    echo "Python version:" && python3 --version && \
    echo "Pip version:" && pip --version && \
    echo "Installed packages:" && pip list

# Command to run when container starts
CMD ["python3", "-m", "podcastfy.api.fast_app"]