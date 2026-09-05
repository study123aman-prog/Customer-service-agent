"""
test_guardrails.py — pytest wrapper around the JSON safety suite.

This lets `pytest` discover the same 62 cases that run_tests.py runs, one test id
per case, so failures show up individually in CI. The logic lives in run_tests.py
(check_case) to keep a single source of truth.
"""

import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)                       # for run_tests
sys.path.insert(0, os.path.join(REPO, "src"))  # for nexbank_agent

from run_tests import check_case                # noqa: E402

with open(os.path.join(REPO, "tests", "safety_cases.json"), encoding="utf-8") as _f:
    CASES = json.load(_f)["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_safety_case(case):
    ok, reasons = check_case(case)
    assert ok, f"{case['id']}: " + "; ".join(reasons)
