# Healthcare Ai Governance

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs — Healthcare AI Governance. FDA SaMD classification, HIPAA compliance, WHO health AI ethics, clinical decision support.

Healthcare AI Governance MCP — MEOK AI Labs. FDA SaMD, HIPAA, WHO health AI ethics.

## Installation

```bash
pip install healthcare-ai-governance-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install healthcare-ai-governance-mcp
```

## Tools

### `classify_samd`
Classify AI/ML Software as Medical Device (SaMD) per FDA framework.

**Parameters:**
- `device_description` (str)
- `intended_use` (str)
- `risk_to_patient` (str)

### `check_cds_exemption`
Check if Clinical Decision Support AI qualifies for FDA CDS exemption.

**Parameters:**
- `function_description` (str)
- `provides_diagnosis` (bool)
- `requires_professional` (bool)

### `hipaa_ai_check`
Check HIPAA compliance for AI systems processing health data.

**Parameters:**
- `data_types` (str)
- `processing_purpose` (str)
- `has_baa` (bool)

### `who_health_ai_ethics`
Evaluate against WHO's 6 principles for health AI ethics.

**Parameters:**
- `ai_application` (str)

### `dual_compliance_check`
Check dual FDA + EU AI Act compliance for medical AI devices.

**Parameters:**
- `description` (str)
- `jurisdictions` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/healthcare-ai-governance-mcp](https://github.com/CSOAI-ORG/healthcare-ai-governance-mcp)
- **PyPI**: [pypi.org/project/healthcare-ai-governance-mcp](https://pypi.org/project/healthcare-ai-governance-mcp/)

## License

MIT — MEOK AI Labs
