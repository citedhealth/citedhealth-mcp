# citedhealth-mcp

[![PyPI](https://img.shields.io/pypi/v/citedhealth-mcp)](https://pypi.org/project/citedhealth-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/citedhealth-mcp)](https://pypi.org/project/citedhealth-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

MCP server for [CITED Health](https://citedhealth.com) — query evidence-based supplement data directly from Claude, Cursor, and Windsurf. Ask your AI assistant about ingredient evidence grades, PubMed papers, and health conditions backed by peer-reviewed research.

> **Browse the evidence at [citedhealth.com](https://citedhealth.com)** — grades for 74 ingredients, 30 conditions, and 2,881 PubMed papers.

## Table of Contents

- [Install](#install)
- [Configure](#configure)
  - [Claude Desktop](#claude-desktop)
  - [Cursor](#cursor)
  - [Windsurf](#windsurf)
- [Available Tools](#available-tools)
- [Example Conversations](#example-conversations)
- [Evidence Grades](#evidence-grades)
- [Environment Variables](#environment-variables)
- [Also Available](#also-available)
- [License](#license)

## Install

```bash
pip install citedhealth-mcp
```

Or with `uvx` (no install needed):

```bash
uvx citedhealth-mcp
```

## Configure

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "citedhealth": {
      "command": "uvx",
      "args": ["citedhealth-mcp"]
    }
  }
}
```

Or if installed with pip:

```json
{
  "mcpServers": {
    "citedhealth": {
      "command": "citedhealth-mcp"
    }
  }
}
```

### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "citedhealth": {
      "command": "uvx",
      "args": ["citedhealth-mcp"]
    }
  }
}
```

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "citedhealth": {
      "command": "uvx",
      "args": ["citedhealth-mcp"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `search_ingredients` | Search supplement ingredients by name or category |
| `get_ingredient` | Get detailed info: mechanism, dosage, forms |
| `search_evidence` | Look up the evidence grade for an ingredient-condition pair |
| `get_evidence` | Get a specific evidence link by ID |
| `search_papers` | Search PubMed-indexed papers by title or year |
| `get_paper` | Get full paper details by PubMed ID |

## Example Conversations

Once configured, ask your AI assistant:

- *"What is the evidence for biotin and hair loss?"*
- *"Search for melatonin supplements and sleep research"*
- *"Find PubMed papers about ashwagandha and anxiety from 2023"*
- *"What ingredients are in the vitamins category?"*
- *"Get details about PMID 12345678"*

The server will call the CITED Health API and return structured evidence grades, study counts, and paper metadata.

## Evidence Grades

CITED Health uses an A-F grading system based on the quality and consistency of peer-reviewed evidence:

| Grade | Label | Criteria |
|-------|-------|----------|
| **A** | Strong Evidence | Multiple RCTs/meta-analyses, consistent positive results |
| **B** | Good Evidence | Some RCTs or strong observational studies |
| **C** | Mixed Evidence | Conflicting results or limited study quality |
| **D** | Weak Evidence | Mostly observational, small sample sizes |
| **F** | No Evidence | No credible studies supporting the claim |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CITEDHEALTH_BASE_URL` | `https://citedhealth.com` | Override API base URL (for testing or self-hosted) |

## Also Available

| Package | Install | Description |
|---------|---------|-------------|
| **citedhealth-mcp** | `pip install citedhealth-mcp` | This package — MCP server for AI assistants |
| **citedhealth** | `pip install citedhealth` | Python client for direct API access |

- [CITED Health API Docs](https://citedhealth.com/developers/)
- [OpenAPI Spec](https://citedhealth.com/api/openapi.json)

## License

MIT License — see [LICENSE](LICENSE) for details.
