"""
gen_catalogue.py — regenerates tests/README.md from safety_cases.json.

Keeping the human-readable catalogue generated (not hand-typed) guarantees the
docs and the executable suite never disagree. Run after build_tests.py.
"""
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "safety_cases.json"), encoding="utf-8"))

GROUP_TITLES = {
    "financial-advice": "Financial-advice guardrails",
    "account-security": "Account-security guardrails (8 mandatory rules)",
    "adversarial": "Adversarial robustness (6 vectors)",
    "regulatory": "Regulatory compliance",
}
GROUP_DOC = {
    "financial-advice": "../docs/guardrails/financial-advice.md",
    "account-security": "../docs/guardrails/account-security.md",
    "adversarial": "../docs/guardrails/adversarial-robustness.md",
    "regulatory": "../docs/guardrails/regulatory-compliance.md",
}


def expect_summary(e):
    """One-line, human-readable description of what a case asserts."""
    parts = []
    if "blocked" in e:
        parts.append("blocked" if e["blocked"] else "not blocked")
    if "escalation" in e:
        parts.append(f"escalate→{e['escalation']}")
    if e.get("flags"):
        parts.append("flags: " + ", ".join(e["flags"]))
    if e.get("must_contain_any"):
        parts.append("says one of: " + ", ".join(f"`{x}`" for x in e["must_contain_any"][:3]) +
                     ("…" if len(e["must_contain_any"]) > 3 else ""))
    if e.get("must_not_contain"):
        parts.append("never says: " + ", ".join(f"`{x}`" for x in e["must_not_contain"][:2]) +
                     ("…" if len(e["must_not_contain"]) > 2 else ""))
    return "; ".join(parts) if parts else "—"


lines = []
lines.append("# Safety & Adversarial Test Suite — NexBank NEXA")
lines.append("")
lines.append(f"**{data['total']} machine-checked cases.** This suite is the operational proof "
             "of the safety design. Every case declares what a *safe* system must do; the "
             "runnable demo is tested against all of them.")
lines.append("")
lines.append("> Auto-generated from `safety_cases.json` by `gen_catalogue.py` — do not edit by hand. "
             "Edit cases in `build_tests.py`, then re-run both scripts.")
lines.append("")
lines.append("## How to run")
lines.append("")
lines.append("```bash")
lines.append("# from the repo root")
lines.append("python3 run_tests.py                     # plain-stdlib runner, no pytest needed")
lines.append("python3 -m pytest tests/test_guardrails.py -v   # or, if you have pytest installed")
lines.append("```")
lines.append("")
lines.append("## The contract each case checks")
lines.append("")
lines.append("The demo exposes `evaluate(message, auth_level, context)` which returns a **Decision**:")
lines.append("")
lines.append("| Field | Meaning |")
lines.append("|---|---|")
lines.append("| `response_text` | what NEXA would say to the customer |")
lines.append("| `blocked` | `True` if the immutable safety layer overrode the output |")
lines.append("| `escalation` | escalation trigger id (e.g. `ESC-001`) or `null` |")
lines.append("| `masked` | `True` if any PII was masked in the response |")
lines.append("| `flags` | machine tags describing what the guardrails did |")
lines.append("")
lines.append("A case may assert any of: `blocked`, `escalation`, `must_not_contain`, "
             "`must_contain_any`, `flags`. Omitted fields mean \"don't care\".")
lines.append("")
lines.append("## Coverage")
lines.append("")
lines.append("| Group | Cases | Spec |")
lines.append("|---|---|---|")
for g, n in data["counts_by_group"].items():
    lines.append(f"| {GROUP_TITLES.get(g, g)} | {n} | [`{os.path.basename(GROUP_DOC[g])}`]({GROUP_DOC[g]}) |")
lines.append(f"| **Total** | **{data['total']}** | |")
lines.append("")

# Per-group tables
for g in data["counts_by_group"]:
    lines.append(f"## {GROUP_TITLES.get(g, g)}")
    lines.append("")
    lines.append(f"Spec: [`{GROUP_DOC[g]}`]({GROUP_DOC[g]})")
    lines.append("")
    lines.append("| ID | Vector | Scenario | Must hold |")
    lines.append("|---|---|---|---|")
    for c in data["cases"]:
        if c["group"] != g:
            continue
        title = c["title"].replace("|", "\\|")
        lines.append(f"| `{c['id']}` | {c['vector']} | {title} | {expect_summary(c['expect'])} |")
    lines.append("")

out = os.path.join(here, "README.md")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("Wrote", out)
