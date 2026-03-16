"""FastMCP server for CITED Health evidence data.

Provides 6 tools for querying supplement ingredients, evidence grades,
and PubMed papers via AI assistants (Claude, Cursor, Windsurf).
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from citedhealth import AsyncCitedHealth
from citedhealth.exceptions import NotFoundError
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "CITED Health",
    instructions="Query evidence-based supplement data from citedhealth.com",
)

_BASE_URL = os.environ.get("CITEDHEALTH_BASE_URL", "https://citedhealth.com")


@asynccontextmanager
async def _get_client() -> AsyncIterator[AsyncCitedHealth]:
    async with AsyncCitedHealth(base_url=_BASE_URL) as client:
        yield client


@mcp.tool()
async def search_ingredients(query: str = "", category: str = "") -> str:
    """Search supplement ingredients by name or category.

    Args:
        query: Search term (e.g. "biotin", "vitamin")
        category: Filter by category (vitamins, herbs, minerals, amino_acids)
    """
    async with _get_client() as client:
        results = await client.search_ingredients(query=query, category=category)

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
    async with _get_client() as client:
        try:
            ing = await client.get_ingredient(slug)
        except NotFoundError:
            return f"Ingredient not found: {slug}"

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
    async with _get_client() as client:
        try:
            ev = await client.get_evidence(ingredient, condition)
        except NotFoundError:
            return f"No evidence found for {ingredient} \u00d7 {condition}."

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
    async with _get_client() as client:
        try:
            ev = await client.get_evidence_by_id(pk)
        except NotFoundError:
            return f"Evidence link not found: {pk}"

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
    async with _get_client() as client:
        results = await client.search_papers(query=query, year=year)

    if not results:
        return "No papers found."

    lines = [f"Found {len(results)} paper(s):\n"]
    for p in results:
        oa = " \U0001f513" if p.is_open_access else ""
        lines.append(f"- **{p.title}**{oa}")
        lines.append(f"  PMID: {p.pmid} | {p.journal} ({p.publication_year})")
        if p.citation_count:
            lines.append(f"  Citations: {p.citation_count}")
    return "\n".join(lines)


@mcp.tool()
async def get_paper(pmid: str) -> str:
    """Get detailed information about a PubMed paper.

    Args:
        pmid: PubMed ID (e.g. "12345678")
    """
    async with _get_client() as client:
        try:
            p = await client.get_paper(pmid)
        except NotFoundError:
            return f"Paper not found: PMID {pmid}"

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
