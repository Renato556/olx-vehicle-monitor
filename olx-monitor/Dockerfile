ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:3.20
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Python and Chromium dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    libstdc++ \
    bash

# Set working directory
WORKDIR /app

# Setup virtual environment and install requirements
COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
RUN chmod +x run.sh

# Environment variables for Playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Run the application
CMD ["/app/run.sh"]
