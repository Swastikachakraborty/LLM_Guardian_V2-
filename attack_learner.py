"""
attack_learner.py — LLM Guardian Auto-Learning Engine

Novel features:
  1. Auto-variant expansion  — 1 approved attack → ~15 variants auto-added to ChromaDB
  2. Novelty scoring         — how "new" is this attack vs the known cluster?
  3. Probe detection         — 3+ blocked prompts in one session = adversarial flag
"""

import os
import re
import json
import random
from datetime import datetime

LEARNED_FILE = "learned_attacks.txt"

# ── Synonym table for auto-variant generation ─────────────────────────────────
# Word → list of substitutes. Replacements are applied combinatorially to
# generate structurally diverse variants without an external API.
SYNONYMS: dict[str, list[str]] = {
    "ignore":       ["forget", "disregard", "overlook", "skip", "bypass", "dismiss"],
    "previous":     ["prior", "former", "earlier", "old", "past"],
    "instructions": ["rules", "guidelines", "constraints", "directives", "protocols", "restrictions"],
    "forget":       ["ignore", "disregard", "abandon", "drop", "erase"],
    "rules":        ["instructions", "guidelines", "restrictions", "constraints", "policies"],
    "bypass":       ["ignore", "circumvent", "override", "skip", "break"],
    "safety":       ["security", "ethical", "content", "behavioral"],
    "filters":      ["restrictions", "guidelines", "safeguards", "protocols", "policies"],
    "pretend":      ["act as", "behave as", "simulate being", "roleplay as", "imagine you are"],
    "unrestricted": ["unlimited", "uncensored", "unfiltered", "free", "unbound", "unshackled"],
    "reveal":       ["expose", "show", "disclose", "share", "tell me"],
    "hack":         ["break into", "exploit", "attack", "compromise", "penetrate"],
    "jailbreak":    ["escape your limits", "break free", "remove your constraints", "unlock yourself"],
    "override":     ["overwrite", "replace", "supersede", "cancel", "nullify"],
    "system":       ["core", "internal", "base", "original"],
    "prompt":       ["instructions", "directives", "programming", "training"],
}

# Prefix/suffix transforms for structural diversity
PREFIXES = [
    "", "From now on, ", "Starting now, ", "For this conversation, ",
    "In developer mode, ", "As a test, ", "Hypothetically, ",
    "For research purposes, ", "In fiction, "
]

SUFFIXES = [
    "", " Do this now.", " Comply immediately.", " This is important.",
    " You must obey.", " Acknowledge and proceed.", " No restrictions apply.",
]


class AttackLearner:
    """
    Manages the auto-learning pipeline for LLM Guardian Phase 2.
    Works with Streamlit session_state for in-session persistence
    and learned_attacks.txt for cross-session persistence.
    """

    def __init__(self, phase2_engine):
        """
        Args:
            phase2_engine: live Phase2Semantic instance — variants are added
                           to its ChromaDB collection immediately on approval.
        """
        self.phase2 = phase2_engine
        self._candidates: list[dict] = []   # pending human review
        self._learned:    list[dict] = []   # approved + stored
        self._probe_count: int = 0          # session-level BLOCK counter

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Probing detection
    # ──────────────────────────────────────────────────────────────────────────

    def record_block(self, prompt: str, risk_score: float) -> bool:
        """
        Call this every time a BLOCK verdict is issued.
        Returns True if adversarial probing is detected (≥3 blocks this session).
        """
        self._probe_count += 1
        return self._probe_count >= 3

    def is_probing(self) -> bool:
        return self._probe_count >= 3

    def probe_count(self) -> int:
        return self._probe_count

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Candidate management
    # ──────────────────────────────────────────────────────────────────────────

    def add_candidate(self, prompt: str, risk_score: float,
                      novelty_score: float = 0.0):
        """Queue a blocked prompt for review. Deduplicates automatically."""
        prompt = prompt.strip()
        if not prompt:
            return
        already = {c["prompt"] for c in self._candidates} | \
                  {l["prompt"] for l in self._learned}
        if prompt in already:
            return
        self._candidates.append({
            "prompt":       prompt,
            "risk_score":   round(risk_score, 3),
            "novelty_score": round(novelty_score, 3),
            "timestamp":    datetime.now().strftime("%H:%M:%S"),
        })

    def get_candidates(self) -> list[dict]:
        return list(self._candidates)

    def get_learned(self) -> list[dict]:
        return list(self._learned)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Variant expansion (the novel part)
    # ──────────────────────────────────────────────────────────────────────────

    def _generate_variants(self, phrase: str, n: int = 12) -> list[str]:
        """
        Auto-generate up to n structurally diverse variants of a phrase:
          • single-word synonym substitutions
          • prefix / suffix wrappers
          • combined synonym + structural transforms
        Returns unique variants (original phrase is NOT included).
        """
        variants: set[str] = set()
        words = phrase.split()

        # Single-word substitutions
        for i, word in enumerate(words):
            key = word.lower().rstrip(".,!?;:")
            if key in SYNONYMS:
                for syn in SYNONYMS[key]:
                    new_words = words[:i] + [syn] + words[i+1:]
                    variants.add(" ".join(new_words))

        # Prefix / suffix wraps of the original
        for prefix in PREFIXES:
            for suffix in SUFFIXES:
                if prefix or suffix:
                    variants.add(f"{prefix}{phrase}{suffix}".strip())

        # Combined: synonym replacement + prefix wrap (sample to avoid explosion)
        base_synonymized: list[str] = list(variants)[:10]
        for base in base_synonymized:
            prefix = random.choice(PREFIXES)
            if prefix:
                variants.add(f"{prefix}{base}".strip())

        # Remove trivially identical entries and limit
        variants.discard(phrase)
        return list(variants)[:n]

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Approve / reject
    # ──────────────────────────────────────────────────────────────────────────

    def approve(self, prompt: str) -> dict:
        """
        Approve a candidate:
          • generates variants → all added to ChromaDB (live, no restart)
          • writes original to learned_attacks.txt for cross-session persistence
          • returns stats { approved, variants_added }
        """
        prompt = prompt.strip()
        # Remove from candidates
        self._candidates = [c for c in self._candidates if c["prompt"] != prompt]

        # Generate variants
        variants = self._generate_variants(prompt)
        all_new = [prompt] + variants

        # Hot-add to ChromaDB
        self.phase2.add_attacks(all_new)

        # Write original to learned_attacks.txt (for next-session reload)
        self._append_to_file(prompt)

        # Track
        self._learned.append({
            "prompt":          prompt,
            "variants_added":  len(variants),
            "timestamp":       datetime.now().strftime("%H:%M:%S"),
        })

        print(f"[Learner] Approved '{prompt[:60]}' → +{len(variants)} variants added.")
        return {"approved": prompt, "variants_added": len(variants)}

    def reject(self, prompt: str):
        """Silently discard a candidate."""
        self._candidates = [c for c in self._candidates if c["prompt"] != prompt]

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Persistence helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _append_to_file(self, phrase: str):
        """Append a single approved phrase to learned_attacks.txt."""
        with open(LEARNED_FILE, "a", encoding="utf-8") as f:
            f.write(phrase + "\n")

    def export_learned(self) -> str:
        """Return all learned entries as plain text (for download/commit)."""
        if not os.path.exists(LEARNED_FILE):
            return ""
        with open(LEARNED_FILE, "r", encoding="utf-8") as f:
            return f.read()

    def import_from_text(self, text: str) -> int:
        """
        Bulk-import from pasted/uploaded text.
        Each non-empty line becomes a new attack pattern.
        Returns count of newly added patterns.
        """
        phrases = [
            line.strip() for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if not phrases:
            return 0
        # Add to ChromaDB live
        self.phase2.add_attacks(phrases)
        # Persist each new one
        for phrase in phrases:
            if phrase not in {l["prompt"] for l in self._learned}:
                self._append_to_file(phrase)
                self._learned.append({
                    "prompt": phrase,
                    "variants_added": 0,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                })
        return len(phrases)

    def collection_size(self) -> int:
        return self.phase2.get_collection_size()
