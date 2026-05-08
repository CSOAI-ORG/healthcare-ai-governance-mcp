<div align="center">

# Healthcare Ai Governance MCP

**MCP server for healthcare ai governance mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-healthcare-ai-governance-mcp)](https://pypi.org/project/meok-healthcare-ai-governance-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Healthcare Ai Governance MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `classify_samd` | Classify AI/ML Software as Medical Device (SaMD) per FDA framework. |
| `check_cds_exemption` | Check if Clinical Decision Support AI qualifies for FDA CDS exemption. |
| `hipaa_ai_check` | Check HIPAA compliance for AI systems processing health data. |
| `who_health_ai_ethics` | Evaluate against WHO's 6 principles for health AI ethics. |
| `dual_compliance_check` | Check dual FDA + EU AI Act compliance for medical AI devices. |

## Installation

```bash
pip install meok-healthcare-ai-governance-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "healthcare-ai-governance": {
      "command": "python",
      "args": ["-m", "meok_healthcare_ai_governance_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
