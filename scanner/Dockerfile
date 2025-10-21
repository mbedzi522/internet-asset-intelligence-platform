# Scanner Service Dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy scanner script
COPY scanner.py .
COPY requirements.txt .

# Install any dependencies (currently none needed)
RUN pip install --no-cache-dir -r requirements.txt

# Create events directory
RUN mkdir -p /app/events

# Run the scanner
CMD ["python", "scanner.py"]
