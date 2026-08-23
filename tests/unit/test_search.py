from __future__ import annotations

from llmwiki.search import search_bundle

from conftest import valid_page


def test_search_returns_structured_ranked_results(project) -> None:
    _, config = project
    strong = config.bundle_root / "concepts" / "robotics.md"
    weak = config.bundle_root / "concepts" / "other.md"
    strong.write_text(valid_page("Robotics", "Robotics combines sensing, planning, and control."), encoding="utf-8")
    weak.write_text(valid_page("Other", "A passing mention of robotics."), encoding="utf-8")
    results = search_bundle(config.bundle_root, "robotics", limit=5)
    assert results[0].concept_id == "concepts/robotics"
    assert results[0].status == "draft"
    assert results[0].trust == "unverified"
