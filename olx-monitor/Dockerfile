ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest
FROM $BUILD_FROM

# Install Python, pip and system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    libcurl \
    curl-dev \
    gcc \
    musl-dev \
    bash \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application files
COPY . .
RUN chmod +x run.sh

# Run the application
CMD ["/app/run.sh"]
