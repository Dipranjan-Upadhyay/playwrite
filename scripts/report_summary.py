"""Compute pass-rate and failure metrics from raw Allure results.

Usage:
    python scripts/report_summary.py allure-results [--min-pass-rate 95]

Prints a Markdown summary (pipe it into $GITHUB_STEP_SUMMARY in CI). Exits 1 when the
pass rate is below --min-pass-rate. Re-runs of the same test (pytest-rerunfailures)
are de-duplicated: only the latest attempt counts, and re-run tests are flagged as flaky.
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def label(result, name, default="-"):
    return next((l["value"] for l in result.get("labels", []) if l["name"] == name), default)


def load_latest_results(results_dir: Path):
    latest, attempts = {}, Counter()
    for file in results_dir.glob("*-result.json"):
        result = json.loads(file.read_text(encoding="utf-8"))
        key = result.get("historyId") or result.get("fullName") or file.name
        attempts[key] += 1
        if key not in latest or result.get("stop", 0) > latest[key].get("stop", 0):
            latest[key] = result
    flaky = {k for k, n in attempts.items() if n > 1 and latest[k]["status"] == "passed"}
    return list(latest.values()), flaky, latest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--min-pass-rate", type=float, default=0.0)
    args = parser.parse_args()

    results, flaky, by_key = load_latest_results(args.results_dir)
    if not results:
        print("No Allure results found.")
        return 1

    status = Counter(r["status"] for r in results)
    executed = len(results) - status["skipped"]
    pass_rate = 100 * status["passed"] / executed if executed else 0.0

    per_feature = defaultdict(Counter)
    for r in results:
        per_feature[label(r, "feature", label(r, "suite"))][r["status"]] += 1

    out = [
        "## Regression results",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total tests | {len(results)} |",
        f"| Passed | {status['passed']} |",
        f"| Failed (assertion) | {status['failed']} |",
        f"| Broken (error) | {status['broken']} |",
        f"| Skipped / xfail | {status['skipped']} |",
        f"| Flaky (passed on rerun) | {len(flaky)} |",
        f"| **Pass rate** | **{pass_rate:.1f}%** |",
        "",
        "### By feature",
        "",
        "| Feature | Passed | Failed | Broken | Skipped | Pass rate |",
        "|---|---|---|---|---|---|",
    ]
    for feature, c in sorted(per_feature.items()):
        ran = sum(c.values()) - c["skipped"]
        rate = f"{100 * c['passed'] / ran:.1f}%" if ran else "n/a"
        out.append(
            f"| {feature} | {c['passed']} | {c['failed']} | {c['broken']} | {c['skipped']} | {rate} |"
        )

    failures = [r for r in results if r["status"] in ("failed", "broken")]
    if failures:
        out += ["", "### Failures", ""]
        for r in failures:
            msg = (r.get("statusDetails", {}).get("message") or "").strip().splitlines()
            out.append(f"- **{r.get('fullName', r['name'])}** ({r['status']}): {msg[0] if msg else ''}")
    if flaky:
        out += ["", "### Flaky tests", ""]
        out += [f"- {by_key[k].get('fullName', by_key[k]['name'])}" for k in sorted(flaky)]

    print("\n".join(out))
    if pass_rate < args.min_pass_rate:
        print(f"\nPass rate {pass_rate:.1f}% is below threshold {args.min_pass_rate}%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
