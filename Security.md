# Security Policy

The **ClinIQ - Clinical Q&A AI Assistant** blueprint does not include production-grade security controls.

This repository is not secure by default and must not be used in production without a comprehensive security review.

## Known Considerations

- **API keys**: `OPENAI_API_KEY` and `LLM_API_KEY` are loaded from `.env` or environment variables. Never commit `.env` to version control.
- **CORS**: CORS is configured to allow all origins by default (`*`). Restrict to specific origins in any non-local deployment.
- **Clinical data privacy**: Clinical documents and queries are sent to OpenAI's API. Do not use cloud APIs with protected health information (PHI) or personally identifiable information (PII) without proper safeguards.
- **HIPAA compliance**: This application is NOT HIPAA-compliant by default. Implementing HIPAA compliance requires:
  - Business Associate Agreements (BAA) with service providers
  - Encryption at rest and in transit
  - Access controls and audit logging
  - Data retention and disposal policies
- **Uploaded documents**: Files are stored locally in the `uploads/` directory. Implement proper access controls and encryption for sensitive data.
- **Vector database**: ChromaDB stores document embeddings locally. Ensure proper permissions and consider encryption for sensitive deployments.

## User Responsibilities

Users are responsible for implementing appropriate:

- Authentication and authorization mechanisms
- Encryption and secure data storage
- Network-level access controls and firewall rules
- Monitoring, logging, and auditing
- Regulatory and compliance safeguards relevant to their deployment environment (HIPAA, GDPR, etc.)
- Data anonymization and de-identification for clinical data
- Secure API key management and rotation policies

## Reporting a Vulnerability

If you discover a security vulnerability in this blueprint, please report it privately to the Cloud2 Labs maintainers rather than opening a public issue.
