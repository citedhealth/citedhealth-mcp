"""Tests for CITED Health MCP server tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from citedhealth.models import Condition, EvidenceLink, Ingredient, NestedIngredient, Paper


class TestMCPToolsExist:
    """Verify all 6 tools are registered on the MCP server."""

    def test_server_has_tools(self) -> None:
        from citedhealth_mcp.server import mcp

        # FastMCP stores tools in _tool_manager._tools dict
        tool_names = list(mcp._tool_manager._tools.keys())
        assert "search_ingredients" in tool_names
        assert "get_ingredient" in tool_names
        assert "search_evidence" in tool_names
        assert "get_evidence" in tool_names
        assert "search_papers" in tool_names
        assert "get_paper" in tool_names

    def test_exactly_six_tools(self) -> None:
        from citedhealth_mcp.server import mcp

        assert len(mcp._tool_manager._tools) == 6

    def test_mcp_server_name(self) -> None:
        from citedhealth_mcp.server import mcp

        assert mcp.name == "CITED Health"


class TestSearchIngredientsTool:
    @pytest.mark.anyio
    async def test_returns_formatted_results(self) -> None:
        mock_client = AsyncMock()
        mock_client.search_ingredients.return_value = [
            Ingredient(id=1, name="Biotin", slug="biotin", category="vitamins"),
        ]
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_ingredients

            result = await search_ingredients(query="biotin")

        assert "Biotin" in result
        assert "biotin" in result
        assert "vitamins" in result

    @pytest.mark.anyio
    async def test_returns_no_results_message(self) -> None:
        mock_client = AsyncMock()
        mock_client.search_ingredients.return_value = []
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_ingredients

            result = await search_ingredients(query="nonexistent")

        assert "No ingredients found" in result

    @pytest.mark.anyio
    async def test_featured_marker(self) -> None:
        mock_client = AsyncMock()
        mock_client.search_ingredients.return_value = [
            Ingredient(id=1, name="Biotin", slug="biotin", category="vitamins", is_featured=True),
        ]
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_ingredients

            result = await search_ingredients(query="biotin")

        assert "\u2605" in result  # star marker for featured


class TestGetIngredientTool:
    @pytest.mark.anyio
    async def test_returns_ingredient_detail(self) -> None:
        mock_client = AsyncMock()
        mock_client.get_ingredient.return_value = Ingredient(
            id=1,
            name="Biotin",
            slug="biotin",
            category="vitamins",
        )
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_ingredient

            result = await get_ingredient(slug="biotin")

        assert "Biotin" in result
        assert "vitamins" in result

    @pytest.mark.anyio
    async def test_not_found_returns_message(self) -> None:
        from citedhealth.exceptions import NotFoundError

        mock_client = AsyncMock()
        mock_client.get_ingredient.side_effect = NotFoundError("ingredient", "unknown")
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_ingredient

            result = await get_ingredient(slug="unknown")

        assert "not found" in result.lower()
        assert "unknown" in result

    @pytest.mark.anyio
    async def test_includes_forms_and_dosage(self) -> None:
        mock_client = AsyncMock()
        mock_client.get_ingredient.return_value = Ingredient(
            id=1,
            name="Magnesium",
            slug="magnesium",
            category="minerals",
            forms=["glycinate", "citrate"],
            recommended_dosage={"sleep": "300-400mg"},
        )
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_ingredient

            result = await get_ingredient(slug="magnesium")

        assert "glycinate" in result
        assert "citrate" in result
        assert "300-400mg" in result


class TestSearchEvidenceTool:
    @pytest.mark.anyio
    async def test_returns_evidence_data(self) -> None:
        mock_client = AsyncMock()
        mock_client.get_evidence.return_value = EvidenceLink(
            id=1,
            ingredient=NestedIngredient(slug="biotin", name="Biotin"),
            condition=Condition(slug="hair-loss", name="Hair Loss"),
            grade="A",
            grade_label="Strong Evidence",
            summary="Strong clinical support.",
            direction="positive",
            total_studies=12,
            total_participants=1847,
        )
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_evidence

            result = await search_evidence(ingredient="biotin", condition="hair-loss")

        assert "Grade A" in result
        assert "Strong Evidence" in result
        assert "12" in result
        assert "1,847" in result

    @pytest.mark.anyio
    async def test_not_found_returns_message(self) -> None:
        from citedhealth.exceptions import NotFoundError

        mock_client = AsyncMock()
        mock_client.get_evidence.side_effect = NotFoundError("evidence", "biotin × unknown")
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_evidence

            result = await search_evidence(ingredient="biotin", condition="unknown")

        assert "No evidence found" in result


class TestGetEvidenceTool:
    @pytest.mark.anyio
    async def test_returns_evidence_by_id(self) -> None:
        mock_client = AsyncMock()
        mock_client.get_evidence_by_id.return_value = EvidenceLink(
            id=42,
            ingredient=NestedIngredient(slug="biotin", name="Biotin"),
            condition=Condition(slug="hair-loss", name="Hair Loss"),
            grade="B",
            grade_label="Good Evidence",
            summary="Good support.",
            direction="positive",
            total_studies=5,
            total_participants=300,
        )
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_evidence

            result = await get_evidence(pk=42)

        assert "Grade B" in result
        assert "Good Evidence" in result

    @pytest.mark.anyio
    async def test_not_found_returns_message(self) -> None:
        from citedhealth.exceptions import NotFoundError

        mock_client = AsyncMock()
        mock_client.get_evidence_by_id.side_effect = NotFoundError("evidence", "999")
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_evidence

            result = await get_evidence(pk=999)

        assert "not found" in result.lower()
        assert "999" in result


class TestSearchPapersTool:
    @pytest.mark.anyio
    async def test_returns_paper_results(self) -> None:
        mock_client = AsyncMock()
        mock_client.search_papers.return_value = [
            Paper(id=1, pmid="12345678", title="Biotin and hair", journal="J Dermatol", publication_year=2022),
        ]
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_papers

            result = await search_papers(query="biotin")

        assert "12345678" in result
        assert "Biotin and hair" in result
        assert "J Dermatol" in result

    @pytest.mark.anyio
    async def test_returns_no_results_message(self) -> None:
        mock_client = AsyncMock()
        mock_client.search_papers.return_value = []
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_papers

            result = await search_papers(query="nonexistent")

        assert "No papers found" in result

    @pytest.mark.anyio
    async def test_open_access_marker(self) -> None:
        mock_client = AsyncMock()
        mock_client.search_papers.return_value = [
            Paper(
                id=1,
                pmid="12345678",
                title="Open Access Paper",
                journal="J Open",
                is_open_access=True,
            ),
        ]
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import search_papers

            result = await search_papers(query="open")

        assert "\U0001f513" in result  # open lock emoji for open access


class TestGetPaperTool:
    @pytest.mark.anyio
    async def test_returns_paper_detail(self) -> None:
        mock_client = AsyncMock()
        mock_client.get_paper.return_value = Paper(
            id=1,
            pmid="12345678",
            title="Biotin and hair",
            journal="J Dermatol",
            publication_year=2022,
            study_type="RCT",
            citation_count=47,
            is_open_access=True,
            pubmed_link="https://pubmed.ncbi.nlm.nih.gov/12345678/",
        )
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_paper

            result = await get_paper(pmid="12345678")

        assert "12345678" in result
        assert "Biotin and hair" in result
        assert "J Dermatol" in result
        assert "RCT" in result
        assert "47" in result
        assert "Yes" in result

    @pytest.mark.anyio
    async def test_not_found_returns_message(self) -> None:
        from citedhealth.exceptions import NotFoundError

        mock_client = AsyncMock()
        mock_client.get_paper.side_effect = NotFoundError("paper", "99999999")
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("citedhealth_mcp.server._get_client", return_value=mock_ctx):
            from citedhealth_mcp.server import get_paper

            result = await get_paper(pmid="99999999")

        assert "not found" in result.lower()
        assert "99999999" in result
