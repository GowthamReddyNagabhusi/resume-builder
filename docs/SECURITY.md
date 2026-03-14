# Security Policy

## Overview

Resume Builder takes security seriously. This document outlines our security practices, reporting procedures, and best practices for users.

## Reporting Security Vulnerabilities

**DO NOT** open a public GitHub issue for security vulnerabilities.

If you discover a security vulnerability, please email:
`security@resumebuilder.local`

Please include:
- Description of the vulnerability
- Affected component(s)
- Severity (Critical/High/Medium/Low)
- Steps to reproduce (if applicable)
- Proof of concept (if applicable)

We aim to respond within 48 hours and will work with you to understand and fix the issue.

## Security Features

### Authentication & Authorization

**JWT Tokens**:
- Algorithm: HS256 (HMAC with SHA-256)
- Token expiration: 1 hour (configurable)
- Refresh tokens: 7 days (stored securely)
- Tokens signed with strong secret key (minimum 32 bytes)

**Password Security**:
- Hashing: Bcrypt with 12 rounds
- Never stored in plaintext
- Minimum 8 characters required
- Must include uppercase, lowercase, numbers, special characters

**OAuth Integration**:
- Authorization code flow (no implicit flow)
- State parameter verification
- PKCE support for mobile apps
- Access tokens never stored in localStorage

**Session Management**:
- Secure, HTTP-only cookies for sensitive data
- CSRF token validation
- Session timeout after 30 minutes of inactivity
- Automatic session cleanup

### Data Protection

**Encryption**:
- HTTPS/TLS 1.3 in production (required)
- Database encryption at rest (AWS RDS encryption, Azure encryption)
- Encrypted fields for sensitive data (API keys, OAuth tokens)
- AES-256 encryption for credential storage

**Secrets Management**:
- Never hardcode secrets
- Use environment variables
- Use AWS Secrets Manager or Azure Key Vault in production
- Rotate API keys regularly (quarterly minimum)

**Database Security**:
- Parameterized queries to prevent SQL injection
- Row-level security (RLS) for multi-tenancy
- Regular backups (daily)
- Backup encryption and testing

### API Security

**Rate Limiting**:
- 100 requests per minute per user (default)
- 10 requests per minute for AI endpoints
- IP-based rate limiting for unauthenticated endpoints
- Rate limit headers in responses

**Input Validation**:
- Server-side validation (never trust client)
- Type checking with Pydantic
- Length limits on all string fields
- Format validation (email, URL, etc.)
- SQL injection prevention via ORM

**CORS**:
- Explicitly configured allowed origins
- No wildcard (`*`) in production
- Credentials require matching origin
- Preflight requests validated

**API Versioning**:
- All APIs versioned (`/api/v1/...`)
- Deprecated versions removed after 12 months
- Breaking changes announced 6 months in advance

### Frontend Security

**XSS (Cross-Site Scripting) Prevention**:
- React auto-escapes content
- Content Security Policy (CSP) headers
- No `dangerouslySetInnerHTML` unless absolutely necessary
- DOMPurify for sanitizing rich content

**CSRF (Cross-Site Request Forgery) Prevention**:
- CSRF token validation for state-changing operations
- SameSite cookie attribute
- Origin/Referer validation

**Dependency Security**:
- Regular dependency updates
- Vulnerability scanning (npm audit, snyk)
- Security advisories reviewed immediately

### Infrastructure Security

**Network**:
- VPC/VNet for database isolation
- Private subnets for databases
- Security groups restricting inbound traffic
- NAT Gateway for outbound traffic
- DDoS protection (AWS Shield, Azure DDoS Protection)

**Access Control**:
- Least privilege principle
- SSH key-based database access only
- No password-based database access
- IP whitelisting for admin access
- VPN/bastion host for secure administration

**Logging & Monitoring**:
- All API requests logged (without sensitive data)
- Error tracking (Sentry or similar)
- Performance monitoring (New Relic)
- Security monitoring and alerting
- Log retention: 90 days

### CI/CD Security

**Code Review**:
- At least one review required before merge
- Automated tests must pass
- Security scanning enabled

**Dependency Management**:
- Dependency vulnerabilities checked on PR
- Outdated dependencies flagged
- Only official package repositories

**Secrets in CI/CD**:
- Secrets stored in GitHub Secrets or CI tool
- Never logged or exposed
- Rotated regularly

## Best Practices for Users

### When Using Resume Builder

1. **Use Strong Passwords**:
   - At least 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Unique from other services

2. **Enable Two-Factor Authentication** (when available):
   - Use authenticator app (Google Authenticator, Authy)
   - Save recovery codes securely
   - Don't lose access to second factor device

3. **Review Connected Accounts**:
   - Check what permissions OAuth apps have
   - Review connected applications regularly
   - Disconnect unused integrations

4. **Keep API Keys Safe**:
   - Never share API keys
   - Regenerate compromised keys immediately
   - Use scoped API keys with minimal permissions

5. **Monitor Account Activity**:
   - Check login history regularly (when available)
   - Enable email notifications for login
   - Alert on unusual activity from new locations

6. **Browser Security**:
   - Keep browser updated
   - Use HTTPS only (never HTTP)
   - Install security extensions (uBlock Origin, etc.)
   - Clear cookies/cache regularly

7. **Device Security**:
   - Keep OS and software updated
   - Use antivirus/antimalware
   - Enable full-disk encryption
   - Logout when finished

### If Your Account Is Compromised

1. Change password immediately
2. Review connected third-party apps
3. Check API keys and regenerate if needed
4. Review login history
5. Enable two-factor authentication
6. Contact support: `support@resumebuilder.local`

## Compliance

Resume Builder adheres to:

- **GDPR**: EU General Data Protection Regulation
  - Right to access, deletion, portability
  - Data processing agreements with processors
  - Privacy policy available

- **CCPA**: California Consumer Privacy Act
  - User rights to know, delete, opt-out
  - Data sale opt-out support

- **SOC 2 Type II** (roadmap)
  - Security, availability, processing integrity
  - Confidentiality, privacy controls

## Data Protection

### Data Collection

We collect:
- Basic profile (email, name)
- Career data (education, experience, skills, projects)
- Generated resumes
- Usage analytics (anonymized)

We do NOT collect:
- Passwords (only hashed)
- Credit card details (payments via third-party)
- Sensitive personal data beyond what needed

### Data Retention

- Active accounts: Data retained while active
- Deleted accounts: Purged after 30 days (review period)
- Backups: Retained for 90 days
- Logs: Retained for 90 days

### Data Sharing

We do NOT:
- Sell user data
- Share data with advertisers
- Share data without consent
- Use data for training ML models (unless opted in)

We may share data with:
- Service providers (AWS, email provider) under contract
- Legal authorities with lawful order
- Co-processors (Firebase, etc.) under agreement

## Security Updates

- Security patches released ASAP (not on release schedule)
- Urgent patches require no additional testing
- Users informed of security updates
- Update status dashboard available

## Vulnerability Disclosure

### Timeline

1. **Report Received**: Acknowledged within 48 hours
2. **Verification**: Confirmed within 5 days
3. **Fix Development**: Patch created
4. **Testing**: Thoroughly tested
5. **Release**: Deployed ASAP (typically within 2 weeks)
6. **Disclosure**: Researcher credited (if desired)

### Public Disclosure

- Responsible disclosure followed
- 90-day window before public disclosure
- Researcher credited in security advisories
- CVE request if applicable

## Security Testing

We conduct:
- **Penetration Testing**: Quarterly
- **Vulnerability Scanning**: Monthly
- **Dependency Audits**: Weekly
- **Code Review**: Every PR
- **Security Training**: Annual

## Contact & Support

**Security Incidents**: `security@resumebuilder.local`
**General Support**: `support@resumebuilder.local`
**Privacy Questions**: `privacy@resumebuilder.local`

## Acknowledgments

We thank the security researchers who have responsibly disclosed vulnerabilities.

---

**Last Updated**: January 15, 2024
**Version**: 1.0

---

## Security Checklist for Deployment

Before deploying to production:

- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS/TLS enabled with valid certificate
- [ ] Database encryption enabled
- [ ] Regular backups configured
- [ ] Database access restricted to VPC only
- [ ] RLS (Row-Level Security) enabled
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] CSRF tokens enabled
- [ ] Security headers set (CSP, X-Frame-Options, etc.)
- [ ] Logging enabled and monitored
- [ ] Error handling doesn't leak sensitive info
- [ ] Dependency vulnerabilities checked
- [ ] Code scanned for secrets (git-secrets)
- [ ] Admin accounts secured with 2FA
- [ ] Monitoring and alerting configured
- [ ] Incident response plan in place
- [ ] Security policy documented
- [ ] Legal review completed (GDPR, etc.)
- [ ] Security disclosure policy published

---

**Security is everyone's responsibility. Thank you for helping keep Resume Builder safe!**
