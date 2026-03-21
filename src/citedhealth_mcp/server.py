"""FastMCP server for CITED Health evidence data.

Provides 12 tools for querying supplement ingredients, evidence grades,
PubMed papers, health conditions, glossary terms, and educational guides
via AI assistants (Claude, Cursor, Windsurf).
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from citedhealth import AsyncCitedHealth
from citedhealth.exceptions import CitedHealthError, NotFoundError, RateLimitError
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "citedhealth",
    instructions="Query evidence-based supplement data from citedhealth.com",
)


@asynccontextmanager
async def _get_client() -> AsyncIterator[AsyncCitedHealth]:
    base_url = os.environ.get("CITEDHEALTH_BASE_URL", "https://citedhealth.com")
    async with AsyncCitedHealth(base_url=base_url) as client:
        yield client


def _api_error(err: CitedHealthError) -> str:
    if isinstance(err, RateLimitError):
        return f"Rate limited. Please retry after {err.retry_after} seconds."
    return f"API error: {err}"


@mcp.tool()
async def search_ingredients(query: str = "", category: str = "") -> str:
    """Search supplement ingredients by name or category.

    Args:
        query: Search term (e.g. "biotin", "vitamin")
        category: Filter by category (vitamins, herbs, minerals, amino_acids)
    """
    try:
        async with _get_client() as client:
            results = await client.search_ingredients(query=query, category=category)
    except CitedHealthError as e:
        return _api_error(e)

    if not results:
        return "No ingredients found."

    lines = [f"Found {len(results)} ingredient(s):\n"]
    for ing in results:
        featured = " \u2605" if ing.is_featured else ""
        lines.append(f"- **{ing.name}** (`{ing.slug}`){featured}")
        if ing.category:
            lines.append(f"  Category: {ing.category}")
        if ing.mechanism:
            lines.append(f"  Mechanism: {ing.mechanism}")
    return "\n".join(lines)


@mcp.tool()
async def get_ingredient(slug: str) -> str:
    """Get detailed information about a supplement ingredient.

    Args:
        slug: Ingredient slug (e.g. "biotin", "melatonin", "saw-palmetto")
    """
    try:
        async with _get_client() as client:
            ing = await client.get_ingredient(slug)
    except NotFoundError:
        return f"Ingredient not found: {slug}"
    except CitedHealthError as e:
        return _api_error(e)

    lines = [
        f"# {ing.name}",
        "",
        f"- **Slug**: {ing.slug}",
        f"- **Category**: {ing.category or 'N/A'}",
        f"- **Mechanism**: {ing.mechanism or 'N/A'}",
    ]
    if ing.forms:
        lines.append(f"- **Forms**: {', '.join(ing.forms)}")
    if ing.recommended_dosage:
        lines.append("- **Dosage**:")
        for use, dose in ing.recommended_dosage.items():
            lines.append(f"  - {use}: {dose}")
    return "\n".join(lines)


@mcp.tool()
async def search_evidence(ingredient: str, condition: str) -> str:
    """Look up the evidence grade for an ingredient-condition pair.

    Args:
        ingredient: Ingredient slug (e.g. "biotin")
        condition: Condition slug (e.g. "hair-loss")
    """
    try:
        async with _get_client() as client:
            ev = await client.get_evidence(ingredient, condition)
    except NotFoundError:
        return f"No evidence found for {ingredient} \u00d7 {condition}."
    except CitedHealthError as e:
        return _api_error(e)

    lines = [
        f"# {ev.ingredient.name} for {ev.condition.name}",
        "",
        f"**Grade {ev.grade}** \u2014 {ev.grade_label}",
        "",
        f"- Studies: {ev.total_studies}",
        f"- Participants: {ev.total_participants:,}",
        f"- Direction: {ev.direction}",
        "",
        f"**Summary**: {ev.summary}",
    ]
    return "\n".join(lines)


@mcp.tool()
async def get_evidence(pk: int) -> str:
    """Get a specific evidence link by its ID.

    Args:
        pk: Evidence link ID (integer)
    """
    try:
        async with _get_client() as client:
            ev = await client.get_evidence_by_id(pk)
    except NotFoundError:
        return f"Evidence link not found: {pk}"
    except CitedHealthError as e:
        return _api_error(e)

    return (
        f"# {ev.ingredient.name} for {ev.condition.name}\n\n"
        f"**Grade {ev.grade}** \u2014 {ev.grade_label}\n\n"
        f"Studies: {ev.total_studies} | Participants: {ev.total_participants:,}\n"
        f"Direction: {ev.direction}\n\n"
        f"{ev.summary}"
    )


@mcp.tool()
async def search_papers(query: str = "", year: int | None = None) -> str:
    """Search PubMed-indexed papers by title or publication year.

    Args:
        query: Search in paper title (e.g. "melatonin sleep")
        year: Filter by publication year (e.g. 2024)
    """
    try:
        async with _get_client() as client:
            results = await client.search_papers(query=query, year=year)
    except CitedHealthError as e:
        return _api_error(e)

    if not results:
        return "No papers found."

    lines = [f"Found {len(results)} paper(s):\n"]
    for p in results:
        oa = " \U0001f513" if p.is_open_access else ""
        lines.append(f"- **{p.title}**{oa}")
        lines.append(f"  PMID: {p.pmid} | {p.journal} ({p.publication_year})")
        lines.append(f"  Citations: {p.citation_count}")
    return "\n".join(lines)


@mcp.tool()
async def get_paper(pmid: str) -> str:
    """Get detailed information about a PubMed paper.

    Args:
        pmid: PubMed ID (e.g. "12345678")
    """
    try:
        async with _get_client() as client:
            p = await client.get_paper(pmid)
    except NotFoundError:
        return f"Paper not found: PMID {pmid}"
    except CitedHealthError as e:
        return _api_error(e)

    lines = [
        f"# {p.title}",
        "",
        f"- **PMID**: {p.pmid}",
        f"- **Journal**: {p.journal}",
        f"- **Year**: {p.publication_year}",
        f"- **Type**: {p.study_type or 'N/A'}",
        f"- **Citations**: {p.citation_count}",
        f"- **Open Access**: {'Yes' if p.is_open_access else 'No'}",
        f"- **PubMed**: {p.pubmed_link}",
    ]
    return "\n".join(lines)


@mcp.tool()
async def list_conditions(is_featured: bool | None = None) -> str:
    """List health conditions available on a CITED Health site.

    Args:
        is_featured: Filter by featured status (true/false), or omit for all
    """
    try:
        async with _get_client() as client:
            results = await client.list_conditions(is_featured=is_featured)
    except CitedHealthError as e:
        return _api_error(e)

    if not results:
        return "No conditions found."

    lines = [f"Found {len(results)} condition(s):\n"]
    for c in results:
        featured = " \u2605" if c.is_featured else ""
        lines.append(f"- **{c.name}** (`{c.slug}`){featured}")
        if c.prevalence:
            lines.append(f"  Prevalence: {c.prevalence}")
    return "\n".join(lines)


@mcp.tool()
async def get_condition(slug: str) -> str:
    """Get detailed information about a health condition.

    Args:
        slug: Condition slug (e.g. "hair-loss", "insomnia", "acne")
    """
    try:
        async with _get_client() as client:
            c = await client.get_condition(slug)
    except NotFoundError:
        return f"Condition not found: {slug}"
    except CitedHealthError as e:
        return _api_error(e)

    lines = [
        f"# {c.name}",
        "",
        f"- **Slug**: {c.slug}",
        f"- **Description**: {c.description or 'N/A'}",
        f"- **Prevalence**: {c.prevalence or 'N/A'}",
    ]
    if c.symptoms:
        lines.append(f"- **Symptoms**: {', '.join(c.symptoms)}")
    if c.risk_factors:
        lines.append(f"- **Risk Factors**: {', '.join(c.risk_factors)}")
    return "\n".join(lines)


@mcp.tool()
async def list_glossary(category: str = "") -> str:
    """List glossary terms from the CITED Health knowledge base.

    Args:
        category: Filter by category (e.g. "supplements", "research"), or omit for all
    """
    try:
        async with _get_client() as client:
            results = await client.list_glossary(category=category or None)
    except CitedHealthError as e:
        return _api_error(e)

    if not results:
        return "No glossary terms found."

    lines = [f"Found {len(results)} glossary term(s):\n"]
    for t in results:
        abbr = f" ({t.abbreviation})" if t.abbreviation else ""
        lines.append(f"- **{t.term}**{abbr} (`{t.slug}`)")
        if t.short_definition:
            lines.append(f"  {t.short_definition}")
    return "\n".join(lines)


@mcp.tool()
async def get_glossary_term(slug: str) -> str:
    """Get the full definition of a glossary term.

    Args:
        slug: Glossary term slug (e.g. "rct", "bioavailability", "double-blind")
    """
    try:
        async with _get_client() as client:
            t = await client.get_glossary_term(slug)
    except NotFoundError:
        return f"Glossary term not found: {slug}"
    except CitedHealthError as e:
        return _api_error(e)

    lines = [
        f"# {t.term}",
        "",
    ]
    if t.abbreviation:
        lines.append(f"- **Abbreviation**: {t.abbreviation}")
    if t.category:
        lines.append(f"- **Category**: {t.category}")
    lines.append("")
    lines.append(t.definition or t.short_definition or "No definition available.")
    return "\n".join(lines)


@mcp.tool()
async def list_guides(category: str = "") -> str:
    """List educational health guides from CITED Health.

    Args:
        category: Filter by category (e.g. "hair", "sleep"), or omit for all
    """
    try:
        async with _get_client() as client:
            results = await client.list_guides(category=category or None)
    except CitedHealthError as e:
        return _api_error(e)

    if not results:
        return "No guides found."

    lines = [f"Found {len(results)} guide(s):\n"]
    for g in results:
        cat = f" [{g.category}]" if g.category else ""
        lines.append(f"- **{g.title}** (`{g.slug}`){cat}")
        if g.meta_description:
            lines.append(f"  {g.meta_description}")
    return "\n".join(lines)


@mcp.tool()
async def get_guide(slug: str) -> str:
    """Get the full content of a health guide.

    Args:
        slug: Guide slug (e.g. "biotin-for-hair-growth", "melatonin-sleep-guide")
    """
    try:
        async with _get_client() as client:
            g = await client.get_guide(slug)
    except NotFoundError:
        return f"Guide not found: {slug}"
    except CitedHealthError as e:
        return _api_error(e)

    lines = [
        f"# {g.title}",
        "",
    ]
    if g.category:
        lines.append(f"**Category**: {g.category}")
        lines.append("")
    lines.append(g.content or "No content available.")
    return "\n".join(lines)
