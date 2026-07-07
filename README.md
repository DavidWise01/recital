# recital — did your marker cross by human memory

A membership-detection harness for the **human-memory membrane**. Every sibling
watches a machine or a channel; this one watches the oldest covert channel there
is: **a person remembering**. Your marker seen by someone, carried out of the
building in their head, and later **recited** — no digital trail at all.

## Why the marker is a passphrase, and the match is fuzzy

Humans do not memorise 128-bit hex. So a canary on this membrane is a **memorable
passphrase** — a handful of distinctive words with real entropy. And because human
memory is **lossy and reconstructive**, detection is fuzzy: recitations are scored
by word-overlap (Jaccard) against each passphrase, and the honest bar is high.

## The controls

1. **The held-out arm.** Passphrases shown to **no one**. If one is ever recited
   near-exactly, the marker reached that person by some route other than
   memory-of-this — the run is INVALID.
2. **The fidelity gate.** Only a **near-exact** recall (`≥ 0.9`) counts. A partial
   match is **FUZZY** — gated, because reconstructive memory (or coincidence) can
   produce a partial with no real crossing.
3. **The access gate.** The reciter must have **had access**. A near-exact recall
   by someone who never saw it means it reached them another way — **NO_ACCESS**,
   gated.
4. **Corroboration, not proof.** A recall's strength is how many **independent
   people** carried it. Even a certified recall is a **lead** — you can't prove it
   was memorised rather than written down or photographed.

## Files

| File | Closure-Loop layer | Role |
|------|--------------------|------|
| `canary.py` | Detection | memorable passphrases (words, real entropy) |
| `registry.py` | Anchoring | what was shown, to signal access, and when |
| `recitation.py` | Comparison | what a person reproduced + fuzzy (Jaccard) match |
| `score.py` | Witness | held-out arm, fidelity gate, access gate, corroboration |
| `harness.py` | Lineage | recitations → detections → score; not causal |
| `selftest.py` | — | show-then-recite proof, no network |

## Verify first

```bash
python selftest.py
```

Proves, no network: a near-exact recall by someone with access, after showing, is
certified and corroborated; a held-out passphrase recited near-exactly spikes FPR
and the run is refused; a **partial** recitation is FUZZY-gated; a near-exact recall
by a **no-access** reciter is gated; a pre-show recitation isn't certified; a run
with no control arm is refused; and an unrelated phrase falls below the match floor.

## What a certified recall does and does not mean

Does: a passphrase only you showed, recited **near-exactly** by someone who **had
access**, **after** you showed it — with a held-out arm proving the harness isn't
fabricating. It crossed via a person's memory.

Does not: prove it was truly memorised (vs written down or photographed), name
anyone's intent, or prove theft. A corroborated **lead**, and a negative means little.

## Honest limits

- **Memorised vs copied is unprovable** — a recall is a human-carried crossing, not
  proof of the mechanism.
- **Entropy is bounded by memorability** — a passphrase people can actually carry has
  far less entropy than a hex canary; use a large wordlist and note it.
- This is the **human-memory** membrane only. See the map for the others.

---
David Lee Wise / ROOT0 / TriPod LLC · CC-BY-ND-4.0
