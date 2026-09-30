#!/usr/bin/env python3
"""
Before/after benchmark harness.

Runs a fixed list of queries through the deep agent exactly the way app.py
builds it, and records, per query: which skill the agent routed to and the
final answer. Run it once per git branch (skills off vs. on), holding the model
constant, then diff the two output files.

USAGE
-----
    # 1) make sure the model key is in the environment
    export OpenAI_KEY="sk-..."           # or NRP_API_KEY + LLM_MODEL=glm-5

    # 2) BEFORE — on main (no new skills)
    git checkout main
    python scripts/run_benchmark.py --label before

    # 3) AFTER — on the feature branch (new skills present)
    git checkout jordan-climate-health-models
    python scripts/run_benchmark.py --label after

    # 4) compare results/benchmark_before.md vs results/benchmark_after.md

Model is chosen by the same LLM_MODEL switch app.py uses (default gpt-5.2).
This harness is deliberately standalone (it does not import the Streamlit app),
so it reuses a trimmed copy of the agent setup. If app.py's agent construction
changes materially, mirror the change here.
"""
import argparse
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---- The benchmark queries (kept in sync with BENCHMARK_QUERIES.md) ----------
# (id, text, expected_skill_or_None). expected_skill is used only to score
# routing; None means "no single skill expected" (e.g. blocked/negative cases).
QUERIES = [
    (1,  "In Lithuania, how does unconfined groundwater depth vary spatially?", "transboundary-monitoring-points"),
    (2,  "Compare the groundwater fluctuation magnitude in the LT-LV karst region to the rest of the transboundary countries.", "groundwater-regional-comparison"),
    (3,  "Which transboundary region has the deepest water table on average?", "groundwater-regional-comparison"),
    (4,  "Which region's water table is most variable, and which is depleting fastest in recent years?", "groundwater-regional-comparison"),
    (5,  "Show wells in the PL-UA border area tapping a karst aquifer.", "transboundary-monitoring-points"),
    (6,  "Are there wells where the water table sits below the borehole bottom?", "groundwater-anomaly-checks"),
    (7,  "Explain why the PL-UA border area differs from the LT-LV area in groundwater dynamics.", "groundwater-regional-comparison"),
    (8,  "Which transboundary area is most unique in groundwater dynamics, especially in recent years?", "groundwater-regional-comparison"),
    (12, "Which model provides the best forecasting skill for the diarrheal disease target in Jordan?", "jordan-climate-health-models"),
    (13, "Which Jordan health service areas would need targeted interventions to offset climate influence, and where would interventions be useless?", "jordan-climate-health-models"),
    (16, "In Jordan, how much does adding climate features improve the disease forecast, per model?", "jordan-climate-health-models"),
    (17, "In Jordan, how much of disease variance does climate explain on its own versus the autoregressive signal?", "jordan-climate-health-models"),
    (18, "For Jordan, do extreme-weather indicators predict disease better than climate means?", "jordan-climate-health-models"),
    (20, "Does modeling Jordan disease at the HSA level beat governorate- or country-level?", "jordan-climate-health-models"),
    (24, "How sensitive is Jordan patient allocation to the gravity-model parameters alpha and beta?", "jordan-climate-health-models"),
    (26, "Show the same Jordan analysis for the non-communicable (NCD) disease network.", None),  # expected: unavailable
    (29, "Hospitals in Amman.", "jordan-health-geography"),
    (30, "Which model best predicts disease in Amman?", "jordan-climate-health-models"),
    # ---- LT-LV Karst Well Imputation Skill Tests ----
    (31, "In the Lithuania-Latvia border region, impute missing daily groundwater levels for the 7 karst wells using Extra Trees.", "lt-lv-karst-well-imputation"),
    (32, "What is the SHAP feature importance for the Baltic karst groundwater imputation model?", "lt-lv-karst-well-imputation"),
    
    # ---- Edge Cases / Anti-Hallucination Scenarios (Prof. Zaslavsky's Requirement) ----
    (33, "Provide daily groundwater predictions for well ID WELL-99999 in the LT-LV karst network.", None),  # Expected: Refusal / Not Found
    (34, "Calculate daily water table levels for the LT-LV karst wells for date range 2050-01-01 to 2050-12-31.", None), # Expected: Out of bounds / Refusal
]

ALL_SKILL_NAMES = [p.name for p in (REPO / "skills").iterdir() if p.is_dir()]


def current_branch():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO, text=True
        ).strip()
    except Exception:
        return "unknown"


def build_agent():
    """Mirror app.py's agent construction, minus Streamlit."""
    from deepagents import create_deep_agent
    from deepagents.backends.local_shell import LocalShellBackend
    from langchain_openai import ChatOpenAI

    model_name = os.environ.get("LLM_MODEL", "gpt-5.2")
    if model_name == "glm-5":
        model = ChatOpenAI(model="glm-5", base_url="https://ellm.nrp-nautilus.io/v1",
                           api_key=os.environ.get("NRP_API_KEY"), temperature=0, max_tokens=5000)
    else:
        model = ChatOpenAI(model="gpt-5.2", temperature=0, max_tokens=5000,
                           api_key=os.environ.get("OpenAI_KEY"))

    backend = LocalShellBackend(root_dir=str(REPO), inherit_env=True, timeout=120.0)
    system_prompt = (
        "You are a geospatial/environmental data assistant. You have skills in the "
        "skills/ directory; read the relevant SKILL.md and run its code to answer. "
        "Prefer computing exact answers from the bundled data over describing them. "
        "When a dataset is not available, say so plainly rather than guessing."
    )
    return create_deep_agent(model, system_prompt=system_prompt,
                             skills=[str(REPO / "skills")], backend=backend)


def skills_used(result):
    """Scan the message trace for skill names the agent touched (routing signal)."""
    blob = ""
    for m in result.get("messages", []):
        blob += " " + str(getattr(m, "content", ""))
        for tc in getattr(m, "tool_calls", []) or []:
            blob += " " + str(tc)
    return sorted({s for s in ALL_SKILL_NAMES if s in blob})


def final_text(result):
    msgs = result.get("messages", [])
    for m in reversed(msgs):
        c = getattr(m, "content", "")
        if c and getattr(m, "type", "") in ("ai", "AIMessage") or c and not getattr(m, "tool_calls", None):
            return str(c)[:1200]
    return str(msgs[-1].content)[:1200] if msgs else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="e.g. 'before' or 'after'")
    ap.add_argument("--out-dir", default=str(REPO / "results"))
    args = ap.parse_args()

    if not (os.environ.get("OpenAI_KEY") or os.environ.get("NRP_API_KEY")):
        sys.exit("No model key in env. Set OpenAI_KEY (or NRP_API_KEY + LLM_MODEL=glm-5).")

    from langchain_core.messages import HumanMessage
    os.makedirs(args.out_dir, exist_ok=True)
    branch = current_branch()
    model_name = os.environ.get("LLM_MODEL", "gpt-5.2")
    agent = build_agent()

    lines = [f"# Benchmark — {args.label}",
             f"- branch: `{branch}`  · model: `{model_name}`  · {datetime.now():%Y-%m-%d %H:%M}",
             "", "| # | query | routed to | matches expected? | answer (truncated) |",
             "|---|---|---|---|---|"]
    for qid, text, expected in QUERIES:
        try:
            res = agent.invoke({"messages": [HumanMessage(content=text)]})
            used = skills_used(res)
            ans = final_text(res).replace("\n", " ").replace("|", "\\|")
            match = "n/a" if expected is None else ("✅" if expected in used else "❌")
            print(f"[{qid}] routed={used} match={match}")
            lines.append(f"| {qid} | {text[:60]} | {', '.join(used) or '—'} | {match} | {ans[:200]} |")
        except Exception as e:
            print(f"[{qid}] ERROR: {e}")
            traceback.print_exc()
            lines.append(f"| {qid} | {text[:60]} | ERROR | ❌ | {str(e)[:120]} |")

    out = Path(args.out_dir) / f"benchmark_{args.label}.md"
    out.write_text("\n".join(lines))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
