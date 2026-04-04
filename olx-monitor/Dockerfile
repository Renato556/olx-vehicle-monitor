ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-python:3.12-alpine3.20
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies for Playwright/Chromium
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    libstdc++

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
RUN chmod +x run.sh

# Environment variables for Playwright to use system Chromium
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Run the application
CMD ["/app/run.sh"]
