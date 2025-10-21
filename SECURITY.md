# Security Policy

This document outlines the security policies and practices for the Internet Asset Intelligence Platform.

## Default Safety

By default, the platform is configured for local and private network scanning only. Public internet scanning requires explicit, auditable consent and a valid Proof of Authorization (POA) document.

## Public Scanning Authorization

To enable public scanning, an operator must:

1. Set `allow_public_targets: true` in the configuration.
2. Provide a strong `public_scan_consent` token.
3. Upload a valid, signed POA document via the admin UI or API.

All these steps are logged immutably in audit logs.

## Responsible Disclosure

We encourage security researchers to report vulnerabilities responsibly. Please contact [security@example.com] for any security concerns or to report potential vulnerabilities.

## Abuse Reporting

This software must not be used for malicious scanning. Any reports of abuse should be directed to [abuse@example.com].

## Key Management

Private keys for event signing are stored in HashiCorp Vault in production environments. A fallback local development mode uses clearly labeled development keys.

## Compliance

The platform includes features for data retention and deletion to comply with regulations such as GDPR. Refer to the data retention policy templates for details.

## Security Audits

Our CI/CD pipelines include static application security testing (SAST), software composition analysis (SCA), container image scanning, and dynamic application security testing (DAST) for staging environments. We also maintain a scheduled pentest checklist.
