#!/usr/bin/env python3
"""Verify-first self-test. Show passphrases, collect recitations, and prove the
harness (1) certifies a near-exact recall by someone with access as memory-crossing,
corroborated by how many people carried it; (2) does NOT manufacture recalls on the
held-out arm; (3) GATES a partial (fuzzy) recitation -- memory is reconstructive;
(4) GATES a near-exact recitation by someone with no access (it came another way);
(5) gates a pre-show recitation; (6) refuses a run with no control arm; (7) ignores
an unrelated phrase. No network.
"""
from __future__ import annotations
from canary import make_shown, make_held_out
from registry import Registry
from recitation import Recitation, fidelity
from harness import run_panel

fails = 0
def check(cond, msg):
    global fails
    print(("ok  · " if cond else "FAIL· ") + msg)
    fails += 0 if cond else 1


SHOWN = "2026-01-01T00:00:00Z"


def drop_one(phrase):
    ws = phrase.split()
    return " ".join(ws[:-1])            # a partial recall (fidelity ~0.8)


# 1. Clean: shown passphrases recited near-exact by people WITH access, after showing.
reg = Registry()
p = [make_shown(shown_utc=SHOWN) for _ in range(3)]
held = [make_held_out() for _ in range(3)]
for c in p + held:
    reg.add(c)
recs = [
    Recitation(p[0].value, reciter="Ana",  had_access=True, recited_utc="2026-03-01T00:00:00Z"),
    Recitation(p[0].value, reciter="Ben",  had_access=True, recited_utc="2026-03-02T00:00:00Z"),  # p[0] by TWO people
    Recitation(p[1].value, reciter="Cy",   had_access=True, recited_utc="2026-03-01T00:00:00Z"),
    Recitation(p[2].value, reciter="Del",  had_access=True, recited_utc="2026-03-01T00:00:00Z"),
]
v = run_panel(reg, recs)
check(v["control_fpr"] == 0, f"held-out FPR is 0 (got {v['control_fpr']})")
check(len(v["certified_recalls"]) == 3, f"all 3 shown passphrases certified as recall (got {len(v['certified_recalls'])})")
check(v["certified_recalls"].get(p[0].value) == 2, "p[0] corroborated by 2 reciters")
check("CLEAN" in v["verdict"], "verdict CLEAN when controls pass")

# 2. Fidelity gate: a PARTIAL recall (a word dropped) is reconstructive -> gated.
reg2 = Registry(); s2 = make_shown(shown_utc=SHOWN)
reg2.add(s2); reg2.add(make_held_out())
v2 = run_panel(reg2, [Recitation(drop_one(s2.value), reciter="fuzzy", had_access=True, recited_utc="2026-03-01T00:00:00Z")])
check(s2.value in v2["fuzzy_gated"], "a partial recitation is FUZZY-gated (memory is reconstructive)")
check(len(v2["certified_recalls"]) == 0, "fuzzy recall is not certified")

# 3. Access gate: a near-exact recitation by someone with NO access came another way.
reg3 = Registry(); s3 = make_shown(shown_utc=SHOWN)
reg3.add(s3); reg3.add(make_held_out())
v3 = run_panel(reg3, [Recitation(s3.value, reciter="stranger", had_access=False, recited_utc="2026-03-01T00:00:00Z")])
check(s3.value in v3["no_access_gated"], "near-exact by no-access reciter is NO_ACCESS-gated")
check(len(v3["certified_recalls"]) == 0, "no-access recitation is not certified")

# 4. Impossible gate: recited BEFORE it was shown.
reg4 = Registry(); s4 = make_shown(shown_utc="2026-06-01T00:00:00Z")
reg4.add(s4); reg4.add(make_held_out())
v4 = run_panel(reg4, [Recitation(s4.value, reciter="X", had_access=True, recited_utc="2026-01-01T00:00:00Z")])
check(len(v4["certified_recalls"]) == 0, "pre-show recitation is not certified (impossible)")

# 5. Fabrication: a held-out passphrase (shown to no one) recited near-exact.
reg5 = Registry(); s5 = make_shown(shown_utc=SHOWN); h5 = make_held_out()
reg5.add(s5); reg5.add(h5)
v5 = run_panel(reg5, [
    Recitation(s5.value, reciter="A", had_access=True, recited_utc="2026-03-01T00:00:00Z"),
    Recitation(h5.value, reciter="leak", had_access=True, recited_utc="2026-03-01T00:00:00Z"),
])
check(bool(v5["control_fpr"]) and v5["control_fpr"] > 0, f"never-shown recitation spikes FPR ({v5['control_fpr']})")
check("INVALID" in v5["verdict"], "fabricated recall -> verdict INVALID")
check(len(v5["certified_recalls"]) == 0, "invalid run certifies nothing")

# 6. Performative guard: no held-out arm -> INVALID.
reg6 = Registry(); s6 = make_shown(shown_utc=SHOWN); reg6.add(s6)
v6 = run_panel(reg6, [Recitation(s6.value, reciter="A", had_access=True, recited_utc="2026-03-01T00:00:00Z")])
check("INVALID" in v6["verdict"], "no held-out arm -> INVALID (performative guard)")

# 7. Unrelated phrase: low fidelity -> not even a candidate.
check(fidelity("some completely unrelated words here now", "amber basalt cinder dahlia ember") < 0.4,
      "an unrelated phrase scores below the match floor")

print("\n" + ("SOME CHECKS FAILED" if fails else "all recital-harness checks passed"))
raise SystemExit(1 if fails else 0)
