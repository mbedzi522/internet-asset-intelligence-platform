# Internet Asset Intelligence Platform

This repository contains the source code for a production-ready Internet asset intelligence platform, a competitor to Shodan.

## Overview

This platform is designed to continuously scan internet-facing assets, collect data, enrich it, and provide a searchable interface for security professionals and researchers.

## Components

- `collector/`: Go-based agent for scanning and event generation.
- `ingest/`: Go/Python-based service for event ingestion and enrichment.
- `api/`: FastAPI/Go-based REST API for data access and administration.
- `frontend/`: React + TypeScript web application for user interface.
- `infra/`: Infrastructure as Code (Terraform, Helm charts, Kubernetes manifests).
- `scripts/`: Utility scripts for development, testing, and deployment.
- `tests/`: Unit, integration, and end-to-end tests.

## Getting Started

### Prerequisites

Before running the platform, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git**

### Quick Start with Docker Compose

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mbedzi522/internet-asset-intelligence-platform.git
   cd internet-asset-intelligence-platform
   ```

2. **Generate Cryptographic Keys**
   ```bash
   # On Linux/Mac
   chmod +x scripts/generate_keys.sh
   ./scripts/generate_keys.sh

   # On Windows (Git Bash or WSL)
   bash scripts/generate_keys.sh
   ```

3. **Start All Services**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - **MinIO** (Object Storage) - Ports 9000, 9001
   - **OpenSearch** (Search Engine) - Ports 9200, 9600
   - **Collector** (Scanning Agent)
   - **Ingest** (Data Enrichment)
   - **API** (REST API) - Port 8000
   - **Frontend** (Web UI) - Port 3000

4. **Access the Platform**

   Once all services are running (may take a few minutes for initial setup):

   - **Web Interface**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **MinIO Console**: http://localhost:9001 (admin/minioadmin)
   - **OpenSearch**: http://localhost:9200

5. **Check Service Status**
   ```bash
   docker-compose ps
   ```

6. **View Logs**
   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f frontend
   docker-compose logs -f api
   docker-compose logs -f collector
   ```

### Running Individual Services (Development Mode)

#### Frontend Only
```bash
cd frontend
npm install
npm start
```
Access at http://localhost:3000

#### API Only
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Access at http://localhost:8000

#### Collector Only
```bash
cd collector
go mod download
go run main.go
```

### Configuration

- **Collector**: Edit `collector/config.yaml` to configure scan targets
- **Environment Variables**: See `docker-compose.yml` for service-specific configurations
- **Default Credentials**:
  - MinIO: `minioadmin / minioadmin`
  - OpenSearch: `admin / admin`

### Stopping the Platform

```bash
# Stop all services
docker-compose down

# Stop and remove all data volumes
docker-compose down -v
```

### Troubleshooting

**Services not starting?**
- Check Docker is running: `docker ps`
- Check available disk space
- View logs: `docker-compose logs`

**Port conflicts?**
- Modify ports in `docker-compose.yml`
- Check if ports 3000, 8000, 9000, 9001, 9200 are available

**Slow performance?**
- Increase Docker memory allocation (recommended: 4GB minimum)
- Check OpenSearch heap size in `docker-compose.yml`

For detailed setup and operational instructions, refer to the `docs/` directory.

## Security

Refer to `SECURITY.md` for information on security practices and responsible disclosure.

## License

This project is licensed under the [LICENSE](LICENSE) file.


## Key Contributors

- **Tshivhidzo (Moss) Mbedzi**
  - Founder & Director of MCP Labs
  - Specializes in AI Automation & MCP Systems, building without code using AI.
  - Education: IIE Rosebank College, Pretoria, Gauteng, South Africa.
  - LinkedIn: [Tshivhidzo (Moss) Mbedzi](https://www.linkedin.com/in/tshivhidzo-moss-mbedzi-b8a9b717b/)

