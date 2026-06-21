import re

from .models import SearchAlias


def build_alias_pattern(alias_text):
    parts = re.split(r"\s+", alias_text.strip())
    phrase_pattern = r"\s+".join(re.escape(part) for part in parts if part)
    return re.compile(rf"(?<![A-Za-z0-9_]){phrase_pattern}(?![A-Za-z0-9_])", re.IGNORECASE)


def find_search_alias_candidates(text):
    aliases = (
        SearchAlias.objects.select_related("lexical_item")
        .prefetch_related("lexical_item__usages")
        .all()
    )
    candidates = []

    for alias in aliases:
        pattern = build_alias_pattern(alias.text)
        matches = [
            {
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
            }
            for match in pattern.finditer(text)
        ]
        if not matches:
            continue

        lexical_item = alias.lexical_item
        candidates.append(
            {
                "search_alias": {
                    "id": alias.id,
                    "text": alias.text,
                },
                "lexical_item": {
                    "id": lexical_item.id,
                    "headword": lexical_item.headword,
                },
                "usages": [
                    {
                        "id": usage.id,
                        "meaning": usage.meaning,
                        "explanation": usage.explanation,
                    }
                    for usage in lexical_item.usages.all()
                ],
                "matches": matches,
                "match_count": len(matches),
            }
        )

    return sorted(
        candidates,
        key=lambda candidate: (
            -len(candidate["search_alias"]["text"]),
            candidate["search_alias"]["text"].lower(),
        ),
    )
