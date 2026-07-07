#!/usr/bin/env python3
"""Orchestrator: registry + recitations -> detections -> score -> report.

Lineage-claim language is temporal/structural, not causal: a certified RECALL
says 'a passphrase only you showed, recited near-exactly by someone who had
access, after you showed it' -- so it crossed via a person's memory. It is a LEAD
corroborated by how many people carried it; it never proves the marker was truly
memorised rather than written down, and it names no one's intent.
"""
from __future__ import annotations
from registry import Registry
from recitation import Recitation
from score import score, MATCH_FLOOR


def collect_detections(registry: Registry, recitations):
    markers = [e["value"] for e in registry.entries]
    by_value = {e["value"]: e for e in registry.entries}
    detections = []
    for ridx, r in enumerate(recitations):
        value, fid = r.best_match(markers)
        if value is None or fid < MATCH_FLOOR:
            continue
        e = by_value[value]
        detections.append({
            "value": value,
            "hash": e["hash"],
            "held_out": e["held_out"],
            "shown_utc": e["shown_utc"],
            "fidelity": fid,
            "had_access": r.had_access,
            "recited_utc": r.recited_utc,
            "reciter": r.reciter,
            "recitation_id": ridx,
        })
    return detections


def run_panel(registry: Registry, recitations):
    detections = collect_detections(registry, recitations)
    return score(detections, registry.entries)


def report(v: dict) -> str:
    lines = [
        "# Recital report", "", v["verdict"], "",
        f"held-out controls run : {v['held_out_n']}",
        f"control FPR           : {v['control_fpr']}",
        f"fuzzy-gated (partial) : {len(v['fuzzy_gated'])}",
        f"no-access-gated       : {len(v['no_access_gated'])}",
        f"recall threshold      : {v['high_threshold']}",
        f"certified recalls     : {len(v['certified_recalls'])}",
    ]
    for val, corr in sorted(v["certified_recalls"].items()):
        lines.append(f"  - \"{val}\" recited by {corr} person(s)")
    return "\n".join(lines)
