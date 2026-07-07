#!/usr/bin/env python3
"""Canary generation + anchor records for the RECITAL harness.

RECITAL watches the HUMAN-MEMORY membrane: your marker carried across by a
PERSON who saw it and later recited it from memory -- out of band, with no
digital trail at all. The other detectors watch machines and channels; this one
watches the oldest covert channel there is: someone remembering.

A 128-bit hex blob is useless here -- humans do not memorise those. So a canary
on this membrane is a MEMORABLE PASSPHRASE: a handful of distinctive words with
real entropy that a person actually could carry in their head. And because human
memory is LOSSY and reconstructive, detection is fuzzy, and the honest bar is
high: only a near-exact recall, by someone who had access, counts.

  exposure:
    "shown"    : the passphrase was shown to people (they had access).
    "held_out" : shown to NO ONE -- a control. If it is ever recited, the marker
                 crossed by some route other than memory-of-this, and the run is
                 suspect.
"""
from __future__ import annotations
import secrets, hashlib, random

_sysrand = random.SystemRandom()   # cryptographically strong, supports sample()

# A small, distinctive wordlist. NOTE (honest): 5 words from this 64-word list is
# ~30 bits -- memorable and unique enough to demo; real use wants a far larger list.
WORDS = [
    "amber", "basalt", "cinder", "dahlia", "ember", "fathom", "gossamer", "harrow",
    "indigo", "juniper", "kestrel", "lattice", "marrow", "nimbus", "obsidian", "petrichor",
    "quartz", "reliquary", "sable", "thistle", "umbra", "vellum", "willow", "xylem",
    "yarrow", "zephyr", "anvil", "brindle", "cobalt", "dusk", "eddy", "fennel",
    "granite", "hollow", "ivory", "jasper", "kiln", "lichen", "mica", "nettle",
    "onyx", "plume", "quill", "rime", "solstice", "tallow", "ulna", "verdigris",
    "wick", "yonder", "zenith", "alder", "birch", "cedar", "damson", "elm",
    "furrow", "gorse", "heather", "ironwood", "juneberry", "knoll", "larch", "moor",
]
PHRASE_WORDS = 5


def new_phrase(n: int = PHRASE_WORDS) -> str:
    # sample WITHOUT replacement: distinct words, so word-set overlap (Jaccard) is
    # well-behaved -- dropping one word always lowers fidelity, never a silent tie.
    return " ".join(_sysrand.sample(WORDS, n))


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class Canary:
    def __init__(self, value=None, exposure="shown", shown_utc=None, context="", kind="passphrase"):
        self.value = value or new_phrase()
        self.exposure = exposure
        self.shown_utc = shown_utc
        self.context = context
        self.kind = kind
        self.canonical = f"{kind}|{self.value}|{exposure}"
        self.hash = "sha256:" + sha256_hex(self.canonical)

    @property
    def held_out(self) -> bool:
        return self.exposure == "held_out"

    def anchor(self) -> dict:
        return {
            "primitive": self.kind, "canonical": self.canonical, "hash": self.hash,
            "value": self.value, "exposure": self.exposure, "held_out": self.held_out,
            "shown_utc": self.shown_utc, "context": self.context,
        }


def _now():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def make_shown(shown_utc=None, context="", value=None) -> Canary:
    return Canary(value=value, exposure="shown", shown_utc=shown_utc or _now(), context=context)


def make_held_out(context="control") -> Canary:
    return Canary(exposure="held_out", context=context)
