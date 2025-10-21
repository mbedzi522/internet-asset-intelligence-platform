# Deliverables

This document tracks the progress and completion of features for the Internet Asset Intelligence Platform.

## Week 1 Milestones (Completed)

- [x] Repo skeleton
- [x] Collector basic probes
- [x] Collector event signing
- [x] Collector local object store upload
- [x] Collector config + safety gating

## Week 2 Milestones (Completed)

- [x] Ingestion consumer with signature verification
- [x] Enrichment stubs (GeoIP, TLS, CVE rules)
- [x] Risk scoring (initial)
- [x] Write to OpenSearch (placeholder logic)
- [x] OpenSearch index mapping (placeholder logic)

## Week 3 Milestones (Partially Completed)

- [x] API (basic search + detail)
- [x] Frontend (basic search + detail)
- [ ] CI setup (skipped due to Docker environment issues)
- [ ] Acceptance tests (skipped due to Docker environment issues)
- [x] Docs (initial - architecture.md, README.md, SECURITY.md, ETHICS.md)
- [ ] Terraform + Helm skeleton for staging (skeletons created, not tested)

## Following 4-8 Weeks (Pending)

- [ ] Production hardening
- [ ] Vault integration
- [ ] Security scans
- [ ] Monitoring
- [ ] Legal templates

## Current Status and Known Issues

All core services (Collector, Ingest, API, Frontend) have been developed and their Dockerfiles are prepared. However, attempts to bring up the entire stack using `docker-compose up -d` within the sandbox environment have been unsuccessful due to a persistent Docker networking error related to `iptables`:

```
failed to solve: rpc error: code = Unknown desc = process "/bin/sh -c npm install -g serve" did not complete successfully: failed to create endpoint ... on network bridge: Unable to enable DIRECT ACCESS FILTERING - DROP rule: (iptables failed: iptables --wait -t raw -A PREROUTING -d 172.17.0.2 ! -i docker0 -j DROP: iptables v1.8.7 (legacy): can't initialize iptables table `raw': Table does not exist (do you need to insmod?)
Perhaps iptables or your kernel needs to be upgraded.
 (exit status 3))
```

This issue appears to be a system-level Docker configuration problem within the sandbox, preventing containers from building and running correctly. As such, the full end-to-end deployment and testing using `docker-compose` could not be completed within this environment.

**Next Steps:**

To proceed, the Docker environment issue would need to be resolved. This might involve:

1.  **Manual Deployment:** Building and running each Docker image individually and manually configuring their network to bypass `docker-compose`'s bridge networking issues.
2.  **External Environment:** Deploying the `docker-compose.yml` and associated Dockerfiles in a different environment (e.g., a local machine with a fully functional Docker setup or a cloud VM).
3.  **Sandbox Troubleshooting:** Further investigation into the sandbox's kernel modules or Docker daemon configuration, which is beyond the scope of typical application development.

The code is structured and documented to allow for easy deployment in a working Docker environment. Acceptance tests (`scripts/run_acceptance_tests.sh`) are in place but could not be executed due to the environment limitations. The frontend build process was successfully completed outside of Docker, and the resulting `dist` folder can be served by any static web server.
