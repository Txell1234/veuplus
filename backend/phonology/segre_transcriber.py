from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


RULES_DIR = Path(__file__).parent / "rules"

# Dialect aliases to canonical rule filenames
_DIALECT_ALIASES = {
    # Nord-occidental umbrella (incluye Andorra)
    "andorran": "nordoccidental",
    "andorra": "nordoccidental",
    "northwestern": "nordoccidental",
    "nord-occidental": "nordoccidental",
    "nordoccidental": "nordoccidental",
}


@dataclass
class SegreRules:
    dialect: str
    g2a: List[Dict[str, str]]
    a2a: List[Dict[str, str]]
    redistribution: List[Dict[str, str]]
    char_map: Dict[str, str]


def _load_rules(dialect: str) -> SegreRules:
    canonical = _DIALECT_ALIASES.get(dialect.lower(), dialect.lower())
    rules_path = RULES_DIR / f"{canonical}.json"
    if not rules_path.exists():
        # fallback to central
        rules_path = RULES_DIR / "central.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return SegreRules(
        dialect=data.get("meta", {}).get("dialect", canonical),
        g2a=data.get("g2a", []),
        a2a=data.get("a2a", []),
        redistribution=data.get("redistribution", []),
        char_map=data.get("char_map", {}),
    )


def _apply_g2a(text: str, rules: SegreRules) -> str:
    # Apply multi-grapheme regex rules in order
    phon = text
    for rule in rules.g2a:
        pattern = rule.get("pattern")
        replace = rule.get("replace", "")
        if not pattern:
            continue
        phon = re.sub(pattern, replace, phon)

    # Map remaining single characters using char_map
    out: List[str] = []
    for ch in phon:
        if ch.isspace():
            out.append(" ")
            continue
        mapped = rules.char_map.get(ch, ch)
        out.append(mapped)
    # Join with spaces between phones; collapse multiple spaces
    phon_joined = " ".join(tok for tok in out if tok != "")
    phon_joined = re.sub(r"\s+", " ", phon_joined).strip()
    return phon_joined


def _apply_simple_substitutions(phon: str, subs: List[Dict[str, str]]) -> str:
    out = phon
    for rule in subs:
        pattern = rule.get("pattern")
        replace = rule.get("replace", "")
        if not pattern:
            continue
        out = re.sub(pattern, replace, out)
    return out


def transcribe(text: str, dialect: str = "central") -> List[str]:
    """Transcribe text using SEGRE-like rule pipeline (simplified).

    - Loads dialectal rules from backend/phonology/rules/{dialect}.json
    - Applies GtoA (regex), then char_map for remaining letters
    - Applies AtoA and redistribution substitutions in sequence
    Returns a list of possible transcriptions (single item for now).
    """
    rules = _load_rules(dialect)
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    g2a = _apply_g2a(normalized, rules)
    a2a = _apply_simple_substitutions(g2a, rules.a2a)
    final = _apply_simple_substitutions(a2a, rules.redistribution)
    return [final]


def supports_language(language: Optional[str]) -> bool:
    """Return True only for Catalan (SEGRE se aplica solo a catalán)."""
    if not language:
        return False
    return language.lower() in {"ca", "catalan", "català"}


__all__ = ["transcribe", "supports_language"]


