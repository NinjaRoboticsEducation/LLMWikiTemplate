from __future__ import annotations

import re
from pathlib import Path

from .frontmatter import FrontmatterError, parse_file
from .lint import is_stale, trust_tier
from .models import SearchResult
from .paths import concept_id, iter_markdown


def _tokens(value: str) -> list[str]:
    return [token for token in re.findall(r"[\w-]+", value.lower()) if len(token) > 1]


def search_bundle(bundle_root: Path, query: str, *, limit: int = 20) -> list[SearchResult]:
    terms = _tokens(query)
    if not terms:
        return []
    results: list[SearchResult] = []
    for path in iter_markdown(bundle_root):
        try:
            document = parse_file(path)
        except FrontmatterError:
            continue
        metadata = document.metadata
        title = str(metadata.get("title") or path.stem)
        description = str(metadata.get("description") or "")
        tags = " ".join(str(tag) for tag in metadata.get("tags", []))
        haystacks = {
            "title": title.lower(),
            "description": description.lower(),
            "tags": tags.lower(),
            "body": document.body.lower(),
        }
        score = sum(
            haystacks["title"].count(term) * 8
            + haystacks["description"].count(term) * 4
            + haystacks["tags"].count(term) * 5
            + haystacks["body"].count(term)
            for term in terms
        )
        combined = "\n".join(haystacks.values())
        phrase = " ".join(terms)
        if phrase and phrase in combined:
            score += 20
        if all(term in combined for term in terms):
            score += 10
        if score == 0:
            continue
        lines = [line.strip() for line in document.body.splitlines() if line.strip() and not line.startswith("#")]
        excerpt = next((line for line in lines if any(term in line.lower() for term in terms)), description)
        results.append(
            SearchResult(
                concept_id=concept_id(path, bundle_root),
                path=path,
                title=title,
                description=description,
                page_type=str(metadata.get("type", "")),
                status=str(metadata.get("status", "stable")),
                trust=trust_tier(metadata),
                stale=is_stale(metadata),
                score=score,
                excerpt=excerpt[:240],
            )
        )
    return sorted(results, key=lambda item: (-item.score, item.concept_id))[:limit]
