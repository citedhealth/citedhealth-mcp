# citedhealth-mcp

[![PyPI version](https://agentgif.com/badge/pypi/citedhealth-mcp/version.svg)](https://pypi.org/project/citedhealth-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/citedhealth-mcp)](https://pypi.org/project/citedhealth-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://agentgif.com/badge/github/citedhealth/citedhealth-mcp/stars.svg)](https://github.com/citedhealth/citedhealth-mcp)

MCP server for [CITED Health](https://citedhealth.com) — query evidence-based supplement data directly from Claude, Cursor, and Windsurf. Ask your AI assistant about ingredient evidence grades, health conditions, PubMed papers, glossary terms, and educational guides backed by peer-reviewed research.

> **Browse the evidence at [citedhealth.com](https://citedhealth.com)** — 6 health domains covering 188 ingredients, 84 conditions, 323 evidence links, and 6,197 PubMed papers.

<p align="center">
  <a href="https://agentgif.com/kwnGatGH"><img src="https://media.agentgif.com/kwnGatGH.gif" alt="citedhealth-mcp demo — MCP server for evidence-based supplement research data in Claude, Cursor, and Windsurf" width="800"></a>
</p>

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

To query a specific CITED Health site (e.g. HairCited for hair health):

```json
{
  "mcpServers": {
    "citedhealth": {
      "command": "uvx",
      "args": ["citedhealth-mcp"],
      "env": {
        "CITEDHEALTH_BASE_URL": "https://haircited.com"
      }
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
| `list_conditions` | List health conditions, optionally filtered by featured status |
| `get_condition` | Get condition details: description, prevalence, symptoms, risk factors |
| `list_glossary` | List glossary terms, optionally filtered by category |
| `get_glossary_term` | Get full glossary term definition |
| `list_guides` | List educational health guides, optionally filtered by category |
| `get_guide` | Get full guide content by slug |

## Example Conversations

Once configured, ask your AI assistant:

- *"What is the evidence for biotin and hair loss?"*
- *"Search for melatonin supplements and sleep research"*
- *"Find PubMed papers about ashwagandha and anxiety from 2023"*
- *"What ingredients are in the vitamins category?"*
- *"Get details about PMID 12345678"*
- *"What health conditions does CITED Health cover?"*
- *"Tell me about the condition 'insomnia' — symptoms and risk factors"*
- *"List all glossary terms in the research category"*
- *"What does 'double-blind' mean in clinical research?"*
- *"Show me guides about hair health"*
- *"Get the full guide on biotin for hair growth"*

The server will call the CITED Health API and return structured evidence grades, study counts, paper metadata, condition details, glossary definitions, and guide content.

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
| `CITEDHEALTH_BASE_URL` | `https://citedhealth.com` | Override API base URL to query a specific CITED Health site |

### Available Sites

Set `CITEDHEALTH_BASE_URL` to query data from any of the 6 CITED Health domains:

| Site | URL | Focus |
|------|-----|-------|
| CITED Health (hub) | `https://citedhealth.com` | All ingredients and conditions |
| HairCited | `https://haircited.com` | Hair loss, thinning, growth |
| SleepCited | `https://sleepcited.com` | Insomnia, sleep quality, circadian rhythm |
| GutCited | `https://gutcited.com` | Gut health, digestion, microbiome |
| ImmuneCited | `https://immunecited.com` | Immune function, inflammation |
| BrainCited | `https://braincited.com` | Cognitive function, memory, focus |

## Learn More About Evidence-Based Supplements

- **Tools**: [Evidence Checker](https://citedhealth.com/api/evidence/) · [Ingredient Browser](https://citedhealth.com/) · [Paper Search](https://citedhealth.com/papers/)
- **Browse**: [Hair Health](https://haircited.com) · [Sleep Health](https://sleepcited.com) · [Gut Health](https://gutcited.com) · [Immune Health](https://immunecited.com) · [Brain Health](https://braincited.com)
- **Guides**: [Grading Methodology](https://citedhealth.com/editorial-policy/) · [Medical Disclaimer](https://citedhealth.com/medical-disclaimer/)
- **API**: [REST API Docs](https://citedhealth.com/developers/) · [OpenAPI Spec](https://citedhealth.com/api/openapi.json)

## Also Available

| Platform | Install | Link |
|----------|---------|------|
| **PyPI** | `pip install citedhealth` | [PyPI](https://pypi.org/project/citedhealth/) |
| **npm** | `npm install citedhealth` | [npm](https://www.npmjs.com/package/citedhealth) |
| **Go** | `go get github.com/citedhealth/citedhealth-go` | [pkg.go.dev](https://pkg.go.dev/github.com/citedhealth/citedhealth-go) |
| **Rust** | `cargo add citedhealth` | [crates.io](https://crates.io/crates/citedhealth) |
| **Ruby** | `gem install citedhealth` | [RubyGems](https://rubygems.org/gems/citedhealth) |

## License

MIT License — see [LICENSE](LICENSE) for details.
