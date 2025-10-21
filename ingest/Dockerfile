
# Use the official Python image as a base
FROM python:3.11-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for GeoIP database (if used)
RUN mkdir -p /app/geoip

# Create a directory for local archives
RUN mkdir -p /app/archive

# Command to run the ingestion service
CMD ["python", "main.py"]

