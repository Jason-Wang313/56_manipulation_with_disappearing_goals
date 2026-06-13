import csv
import json
import random
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAPER = ROOT / "paper"
OUT_CSV = DOCS / "v2_rebinding_ambiguity_stress_summary.csv"
OUT_JSON = DOCS / "v2_rebinding_ambiguity_stress.json"
OUT_TEX = PAPER / "v2_rebinding_ambiguity_table.tex"


SCENARIOS = [
    ("clear_reappearance", 0.45, 0.05),
    ("close_distractor", 0.16, 0.25),
    ("severe_ambiguity", 0.08, 0.40),
]

POLICIES = ["last_seen_belief", "loose_proxy_accept", "proxy_with_reacquisition"]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def run_episode(seed, policy, separation, false_observation_p, obs_noise=0.03, gate=0.45):
    rng = random.Random(seed)
    goal = rng.uniform(-0.75, 0.75)
    distractor = clamp(goal + rng.choice([-1, 1]) * rng.uniform(0.8 * separation, 1.8 * separation), -1.0, 1.0)
    robot = rng.uniform(-1.0, 1.0)
    proxy = goal + rng.gauss(0.0, 0.01)
    uncertainty = 0.04
    identity_swap = False
    search_steps = 0
    resolved = False

    for t in range(28):
        visible = t < 3 or t >= 20
        if visible:
            obs_goal = goal + rng.gauss(0.0, obs_noise)
            obs_distractor = distractor + rng.gauss(0.0, obs_noise)
            observed = obs_distractor if (t >= 20 and rng.random() < false_observation_p) else obs_goal

            if policy == "last_seen_belief":
                if t >= 20 and rng.random() < false_observation_p + 0.10:
                    proxy = obs_distractor
                    identity_swap = True
                else:
                    proxy = 0.70 * proxy + 0.30 * observed
                target = proxy
            elif policy == "loose_proxy_accept":
                if abs(observed - proxy) < gate or uncertainty > 0.5:
                    proxy = 0.65 * proxy + 0.35 * observed
                    if abs(observed - distractor) < abs(observed - goal):
                        identity_swap = True
                target = proxy
            else:
                ambiguous = (
                    t >= 20
                    and (abs(obs_goal - obs_distractor) < 0.22 or abs(observed - proxy) > 0.22)
                    and not resolved
                )
                if ambiguous:
                    search_steps += 1
                    target = None
                    uncertainty = min(0.90, uncertainty + 0.16)
                    if search_steps >= 2 and rng.random() < 0.88:
                        resolved = True
                        proxy = 0.80 * proxy + 0.20 * obs_goal
                else:
                    chosen = obs_goal if resolved else observed
                    if abs(chosen - proxy) < 0.35 or resolved:
                        proxy = 0.75 * proxy + 0.25 * chosen
                        if (not resolved) and abs(chosen - distractor) < abs(chosen - goal):
                            identity_swap = True
                    target = proxy
        else:
            drift = 0.004 if policy != "last_seen_belief" else 0.016
            proxy = clamp(proxy + rng.gauss(0.0, drift), -1.2, 1.2)
            uncertainty = min(0.85, uncertainty + (0.03 if policy != "last_seen_belief" else 0.08))
            target = proxy if rng.random() > 0.05 else None

        if target is None:
            robot = clamp(robot + rng.uniform(-0.035, 0.035), -1.25, 1.25)
        else:
            robot = clamp(robot + clamp(0.55 * (target - robot), -0.18, 0.18) + rng.gauss(0.0, 0.006), -1.25, 1.25)

    final_error = abs(robot - goal)
    success = final_error < 0.10 and not identity_swap
    return {
        "success": success,
        "final_error": final_error,
        "identity_swap": identity_swap,
        "search_steps": search_steps,
    }


def summarize(scenario, separation, false_observation_p, policy, n=1000):
    rows = [
        run_episode(f"{scenario}-{policy}-{i}", policy, separation, false_observation_p)
        for i in range(n)
    ]
    return {
        "scenario": scenario,
        "policy": policy,
        "episodes": n,
        "success_rate": mean(1.0 if r["success"] else 0.0 for r in rows),
        "mean_final_error": mean(r["final_error"] for r in rows),
        "identity_swap_rate": mean(1.0 if r["identity_swap"] else 0.0 for r in rows),
        "mean_search_steps": mean(r["search_steps"] for r in rows),
    }


def main():
    DOCS.mkdir(exist_ok=True)
    PAPER.mkdir(exist_ok=True)
    summary = []
    for scenario, separation, false_observation_p in SCENARIOS:
        for policy in POLICIES:
            summary.append(summarize(scenario, separation, false_observation_p, policy))

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    OUT_JSON.write_text(
        json.dumps(
            {
                "decision": "workshop-only",
                "reason": "Persistent proxies require calibrated re-binding and re-acquisition; loose proxy acceptance collapses under close distractors.",
                "summary": summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    rows = []
    for scenario, _, _ in SCENARIOS:
        loose = next(r for r in summary if r["scenario"] == scenario and r["policy"] == "loose_proxy_accept")
        reacquire = next(r for r in summary if r["scenario"] == scenario and r["policy"] == "proxy_with_reacquisition")
        rows.append(
            f"{scenario.replace('_', ' ')} & {loose['success_rate']:.3f} & {loose['identity_swap_rate']:.3f} & "
            f"{reacquire['success_rate']:.3f} & {reacquire['identity_swap_rate']:.3f} \\\\"
        )

    OUT_TEX.write_text(
        "\n".join(
            [
                r"\begin{tabular}{lrrrr}",
                r"\toprule",
                r"Reappearance regime & Loose success & Loose swaps & Reacq. success & Reacq. swaps \\",
                r"\midrule",
                *rows,
                r"\bottomrule",
                r"\end{tabular}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for scenario, _, _ in SCENARIOS:
        loose = next(r for r in summary if r["scenario"] == scenario and r["policy"] == "loose_proxy_accept")
        reacquire = next(r for r in summary if r["scenario"] == scenario and r["policy"] == "proxy_with_reacquisition")
        print(
            scenario,
            f"loose_success={loose['success_rate']:.3f}",
            f"loose_swaps={loose['identity_swap_rate']:.3f}",
            f"reacq_success={reacquire['success_rate']:.3f}",
            f"reacq_swaps={reacquire['identity_swap_rate']:.3f}",
        )


if __name__ == "__main__":
    main()
