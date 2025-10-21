
# Use the official Golang image as a base
FROM golang:1.21-alpine AS builder

# Set necessary environment variables
ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64

# Set the current working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum files and download dependencies
COPY go.mod go.sum ./ 
RUN go mod download

# Copy the rest of the application source code
COPY . .

# Build the collector agent
RUN go build -o /collector main.go

# Start a new, smaller image for the final executable
FROM alpine:latest

WORKDIR /root/

# Copy the compiled executable from the builder stage
COPY --from=builder /collector .

# Copy the config schema and a default config (for demonstration)
COPY --from=builder /app/config.schema.yaml ./config.schema.yaml
COPY --from=builder /app/config.yaml ./config.yaml.example

# Expose a health check port if needed (example)
EXPOSE 8080

# Command to run the executable
CMD ["./collector", "--config", "config.yaml"]

