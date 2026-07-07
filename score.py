#!/usr/bin/env python3
"""Scoring + controls. The FIDELITY gate and the ACCESS gate do the work, over a
held-out arm.

A DETECTION is a recitation matched to its closest passphrase with fidelity above
a floor. Each is tiered:

  RECALL    : near-exact recall (fidelity >= HIGH), by someone who HAD ACCESS,
              recited AFTER it was shown -> the marker crossed via memory. A LEAD.
  FUZZY     : a partial match (floor <= fidelity < HIGH) -> human memory is
              reconstructive; a partial could be coincidence or reconstruction.
              Gated -- never certified.
  NO_ACCESS : near-exact, but the reciter never had access -> it reached them by
              some route OTHER than memory-of-this. Gated.
  IMPOSSIBLE: recited before it was shown -> provenance error.
  CONTROL   : a HELD-OUT passphrase (shown to no one) recited near-exact ->
              fabrication / leak elsewhere -> run INVALID.

Certification: RECALL leads certify only if a held-out arm ran and its FPR is 0.
Even a certified RECALL is a LEAD -- you cannot prove it was memorised rather than
written down or photographed. Corroboration = distinct reciters.
"""
from __future__ import annotations

MATCH_FLOOR = 0.4     # below this, not even a candidate (a different phrase)
HIGH = 0.9            # near-exact recall


def _before(a, b):
    if not a or not b:
        return False
    return a[:19] < b[:19]


def tier(d):
    if d["fidelity"] < MATCH_FLOOR:
        return "IGNORE"
    if d["held_out"]:
        return "CONTROL" if d["fidelity"] >= HIGH else "IGNORE"
    if _before(d["recited_utc"], d["shown_utc"]):
        return "IMPOSSIBLE"
    if d["fidelity"] < HIGH:
        return "FUZZY"
    if not d["had_access"]:
        return "NO_ACCESS"
    return "RECALL"


def score(detections, registry_entries):
    held_total = [e for e in registry_entries if e["held_out"]]
    n_held = len(held_total)

    for d in detections:
        d["tier"] = tier(d)

    control_hits = {d["value"] for d in detections if d["tier"] == "CONTROL"}
    fpr = (len(control_hits) / n_held) if n_held else None

    recall = {}
    for d in detections:
        if d["tier"] == "RECALL":
            recall.setdefault(d["value"], set()).add(d.get("reciter", ""))
    fuzzy = {d["value"] for d in detections if d["tier"] == "FUZZY"}
    no_access = {d["value"] for d in detections if d["tier"] == "NO_ACCESS"}

    if n_held == 0:
        verdict = "INVALID: no held-out control arm was run (performative)"
        certified = {}
    elif fpr and fpr > 0:
        verdict = (f"INVALID: control FPR={fpr:.2f} -- a never-shown passphrase was "
                   f"recited; the crossing did not come from memory-of-this")
        certified = {}
    else:
        certified = recall
        verdict = (f"CLEAN: control FPR=0 over {n_held} held-out; "
                   f"{len(certified)} recall lead(s) -- carried by memory, a lead not proof")

    return {
        "verdict": verdict,
        "certified_recalls": {v: len(r) for v, r in certified.items()},
        "fuzzy_gated": sorted(fuzzy),
        "no_access_gated": sorted(no_access),
        "control_hits": sorted(control_hits),
        "control_fpr": fpr,
        "held_out_n": n_held,
        "high_threshold": HIGH,
    }
