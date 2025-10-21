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

Refer to the `docs/` directory for detailed setup and operational instructions.

## Security

Refer to `SECURITY.md` for information on security practices and responsible disclosure.

## License

This project is licensed under the [LICENSE](LICENSE) file.
