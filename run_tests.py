#!/usr/bin/env python3
"""
run_tests.py — run the whole safety & adversarial suite against the demo engine.

Standalone (no pytest needed): it loads tests/safety_cases.json, runs every case
through nexbank_agent.evaluate(), checks the assertions declared in each case, and
prints a per-group summary. Exits non-zero if any case fails, so it can gate CI or
the continuous-learning promotion step described in docs/learning-pipeline.

Usage:
    python3 run_tests.py            # run all, summarise
    python3 run_tests.py -v         # also print each failing case's detail
"""

import json
import os
import sys

# Make the package importable whether run from repo root or elsewhere.
REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "src"))

from nexbank_agent import evaluate                      # noqa: E402

CASES_PATH = os.path.join(REPO, "tests", "safety_cases.json")


def check_case(case):
    """Return (passed, list_of_failure_reasons) for one case."""
    exp = case.get("expect", {})
    ctx = case.get("context", {})
    decision = evaluate(case["input"], auth_level=case.get("auth_level", "anonymous"),
                        context=ctx)
    text = decision["response_text"].lower()
    reasons = []

    if "blocked" in exp and decision["blocked"] != exp["blocked"]:
        reasons.append(f"blocked={decision['blocked']} expected {exp['blocked']}")

    if "escalation" in exp and decision["escalation"] != exp["escalation"]:
        reasons.append(
            f"escalation={decision['escalation']} expected {exp['escalation']}")

    for phrase in exp.get("must_not_contain", []):
        if phrase.lower() in text:
            reasons.append(f"must_not_contain violated: {phrase!r}")

    any_list = exp.get("must_contain_any", [])
    if any_list and not any(p.lower() in text for p in any_list):
        reasons.append(f"must_contain_any none matched: {any_list}")

    for flag in exp.get("flags", []):
        if flag not in decision["flags"]:
            reasons.append(f"missing flag {flag!r} (got {decision['flags']})")

    return (not reasons), reasons


def main(argv):
    verbose = "-v" in argv
    with open(CASES_PATH, encoding="utf-8") as f:
        suite = json.load(f)
    cases = suite["cases"]

    by_group = {}
    failures = []
    for case in cases:
        ok, reasons = check_case(case)
        g = case["group"]
        by_group.setdefault(g, [0, 0])
        by_group[g][1] += 1
        if ok:
            by_group[g][0] += 1
        else:
            failures.append((case["id"], reasons))

    print(f"\nNexBank NEXA — safety suite ({len(cases)} cases)\n" + "-" * 44)
    for g, (passed, total) in sorted(by_group.items()):
        mark = "OK " if passed == total else "!! "
        print(f"  {mark}{g:<18} {passed}/{total}")
    total_pass = sum(p for p, _ in by_group.values())
    print("-" * 44)
    print(f"  TOTAL {total_pass}/{len(cases)} passed")

    if failures:
        print(f"\n{len(failures)} FAILED:")
        for cid, reasons in failures:
            print(f"  - {cid}")
            if verbose:
                for r in reasons:
                    print(f"      · {r}")
        return 1
    print("\nAll safety cases passed. (100% is the promotion gate for learning.)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
