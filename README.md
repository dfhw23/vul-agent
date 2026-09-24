# vuln-scanner

> Web Application Vulnerability Scanning Skill for Claude Code

A structured skill for conducting authorized web application security assessments, covering vulnerability discovery, verification, and report generation for common issues like SQL injection, XSS, SSRF, RCE, and unauthorized access.

## ⚠️ Legal Disclaimer

**This skill is intended for authorized security testing only.** Unauthorized testing of systems you do not own or have explicit written permission to test is illegal and unethical. Always obtain proper authorization before conducting any security assessment.

## Features

- **5-Stage Workflow**: Reconnaissance → Scanning → Verification → Reporting → Output
- **15+ Vulnerability Types**: SQL injection, XSS, SSRF, RCE, file upload, IDOR, XXE, CSRF, and more
- **Comprehensive Payload Library**: Covering MySQL, MSSQL, PostgreSQL, Oracle, SQLite, MongoDB
- **Automated Report Generation**: Python script supporting single vulnerability, summary, and recon reports
- **Structured Templates**: Standardized report formats with CVSS scoring guidance

## Project Structure

```
vuln-scanner/
├── SKILL.md                      # Main skill document (loaded when triggered)
├── README.md                     # This file
├── references/                   # Reference docs (loaded on demand)
│   ├── vuln-catalog.md          # Complete vulnerability catalog
│   ├── payloads.md              # Payload library for all vulnerability types
│   └── examples.md              # Usage examples and workflows
├── assets/
│   └── report-template.md       # Report templates (single + summary)
└── scripts/
    └── gen_report.py            # Report generator (Python)
```

## Installation

This skill is currently a standalone project. To make it auto-trigger in Claude Code, you have two options:

### Option 1: Copy to user skills directory

```bash
# Linux/macOS
cp -r vuln-scanner ~/.claude/skills/

# Windows
xcopy /E /I vuln-scanner %USERPROFILE%\.claude\skills\vuln-scanner
```

### Option 2: Package as .skill file

```bash
python -m scripts.package_skill vuln-scanner/
```

The resulting `.skill` file can then be installed via Claude Code's plugin system.

## Usage

### Triggering the Skill

The skill activates when you mention any of these topics:
- 漏洞挖掘 (vulnerability discovery)
- 漏洞扫描 (vulnerability scanning)
- 渗透测试 (penetration testing)
- SQL注入 (SQL injection)
- XSS
- SSRF
- 安全测试 (security testing)
- Web漏洞 (web vulnerabilities)
- bug bounty
- 代码审计 (code audit)
- 安全审计 (security audit)

### Example Prompts

**Single URL scan:**
```
Scan http://testphp.vulnweb.com for security vulnerabilities
```

**Single vulnerability verification:**
```
Verify if http://target.com/page?id=1 has SQL injection
```

**Code audit:**
```
Audit this PHP code for security issues: <code>
```

**Report generation:**
```
Generate a vulnerability report from this data: ...
```

## Workflow

### Stage 1: Reconnaissance
- Identify technology stack (server, framework, database)
- Discover subdomains, directories, API endpoints
- Map input points (URL params, headers, cookies, file uploads)

### Stage 2: Vulnerability Scanning
- Systematic scanning across 15+ vulnerability categories
- Manual testing combined with tool-assisted scanning
- Prioritize by risk level (P0/P1/P2)

### Stage 3: Verification
- Confirm reproducibility across multiple requests
- Evaluate real-world impact and exploit complexity
- Filter out false positives (WAF blocks, test environment quirks)

### Stage 4: Reporting
- Generate structured vulnerability reports
- Include CVSS scoring, reproduction steps, fix recommendations
- Provide both single-vuln and overall assessment reports

### Stage 5: Output
Save all artifacts to `output/<target>/`:
- `recon.md` - Reconnaissance results
- `findings.md` - Vulnerability list
- `summary.md` - Overall assessment report
- `reports/vuln_XXX.md` - Individual vulnerability reports

## Vulnerability Coverage

### P0 - Critical (Must Check)

| Vulnerability | CWE | OWASP 2021 |
|--------------|-----|------------|
| SQL Injection | CWE-89 | A03 |
| Command Injection / RCE | CWE-78 | A03 |
| SSRF | CWE-918 | A10 |
| Broken Access Control | CWE-284 | A01 |
| File Upload | CWE-434 | A04 |

### P1 - Important

Stored XSS, CSRF, IDOR, XXE

### P2 - Standard

Reflected XSS, Information Disclosure, Sensitive Data Leakage

## Report Generator

The included Python script can generate three types of reports:

### Single Vulnerability Report
```bash
python scripts/gen_report.py --type single \
  --data '{
    "id": "VULN-001",
    "name": "SQL Injection in User Profile",
    "type": "SQL Injection",
    "severity": "High",
    "cvss": "8.5",
    "url": "http://target.com/api/user",
    "param": "id",
    "overview": "...",
    "reproduction": [...],
    "impact": "...",
    "fix_suggestion": "..."
  }' \
  --output report.md
```

### Summary Report
```bash
python scripts/gen_report.py --type summary \
  --target "target.com" \
  --findings '[{"id":"VULN-001","name":"SQLi","severity":"High"},...]' \
  --output summary.md
```

### Reconnaissance Report
```bash
python scripts/gen_report.py --type recon \
  --target "target.com" \
  --info '{"ip":"1.2.3.4","tech":"Nginx + PHP","ports":"80,443"}' \
  --output recon.md
```

## Best Practices

### DO

- ✅ Always confirm written authorization before testing
- ✅ Use systematic, structured methodology
- ✅ Document detailed reproduction steps
- ✅ Provide actionable, specific fix recommendations
- ✅ Focus on business impact, not just technical issues
- ✅ Prioritize critical functions (auth, payment, data queries)

### DON'T

- ❌ Never test without authorization
- ❌ Don't execute destructive operations
- ❌ Don't use high-risk payloads on production
- ❌ Don't omit fix recommendations
- ❌ Don't ignore low-severity issues (info disclosure can be part of attack chains)

## Tools Recommended

### Active Scanners
- **SQLMap**: `sqlmap -u "http://target.com/page?id=1" --batch`
- **Xray**: `xray webscan --basic-crawler http://target.com`
- **Nuclei**: `nuclei -u http://target.com -t vulnerabilities/`
- **AWVS**, **Burp Suite Scanner**

### Passive Analysis
- **Burp Suite**: Intercept, modify, replay HTTP requests
- **Browser DevTools**: Analyze frontend JS, cookies, requests

## Responsible Disclosure

When vulnerabilities are discovered:
1. Report through official channels to the affected party
2. Allow reasonable time for patching (typically 90 days)
3. Avoid public disclosure until a fix is deployed
4. Coordinate disclosure timing with the vendor

## License & Disclaimer

This skill is provided for educational and authorized testing purposes. The authors are not responsible for misuse or unauthorized testing conducted with this tool. Users are solely responsible for ensuring their activities comply with applicable laws and regulations.

## Contributing

Suggestions and improvements welcome. To modify:
1. Edit the relevant files (SKILL.md, references/, scripts/)
2. Test with `python scripts/gen_report.py`
3. Update documentation accordingly

## References

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackTricks](https://book.hacktricks.xyz/)

---

**Version**: 1.0
**Last Updated**: 2026-09-24
**Compatibility**: Claude Code (any version with skill support)