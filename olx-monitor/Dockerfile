ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.20
FROM ${BUILD_FROM}

# Install Python 3 and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-requests \
    chromium \
    chromium-chromedriver

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy application files
COPY app/ ./app/
COPY run.sh .
RUN chmod +x run.sh

# Run the application
CMD ["/app/run.sh"]
