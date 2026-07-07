#!/usr/bin/env python3
"""Recitations = Detection + Comparison.

A RECITATION is what a person reproduced from memory -- text you obtained out of
band (they wrote it down for you, said it aloud, typed it). Each carries who
recited it, whether that person ever HAD ACCESS to the marker, and when.

Human memory is lossy, so detection is FUZZY: we normalise to words and score
overlap (Jaccard) between the recitation and each passphrase. Exact recall -> 1.0;
a dropped or swapped word drops it fast. The fidelity gate lives in score.py.
"""
from __future__ import annotations
import re
from dataclasses import dataclass


def normalize(text: str):
    return set(w for w in re.findall(r"[a-z0-9]+", text.lower()) if w)


def fidelity(recitation: str, marker: str) -> float:
    """Jaccard overlap of the word sets. 1.0 = exact recall (order-independent)."""
    a, b = normalize(recitation), normalize(marker)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass
class Recitation:
    text: str                    # what the person reproduced
    reciter: str = "someone"     # who
    had_access: bool = True      # did this person ever see the marker?
    recited_utc: str | None = None
    source: str = ""

    def best_match(self, markers):
        """Return (marker_value, fidelity) for the closest marker."""
        best = (None, 0.0)
        for m in markers:
            f = fidelity(self.text, m)
            if f > best[1]:
                best = (m, f)
        return best
