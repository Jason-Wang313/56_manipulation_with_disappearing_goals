import csv
import math
import random
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build"
OUT.mkdir(exist_ok=True)


def simulate(policy, seed, n_episodes=400):
    rng = random.Random(seed)
    stats = {"success": 0, "steps": [], "reacquire": 0, "lost": 0}
    traces = []
    for _ in range(n_episodes):
        robot = rng.uniform(-1.0, 1.0)
        goal = rng.uniform(-1.0, 1.0)
        proxy = goal
        visible = True
        hidden_step = rng.randint(6, 12)
        for t in range(20):
            if t == hidden_step:
                visible = False
                stats["lost"] += 1
            if policy == "naive":
                target = goal if visible else None
            else:
                if visible:
                    proxy = goal
                target = proxy
            if target is None:
                robot += rng.uniform(-0.05, 0.05)
            else:
                robot += max(-0.25, min(0.25, 0.6 * (target - robot)))
            robot = max(-1.2, min(1.2, robot))
            if visible and abs(robot - goal) < 0.08:
                stats["success"] += 1
                stats["steps"].append(t + 1)
                break
            if not visible and policy == "proxy" and abs(robot - proxy) < 0.12:
                stats["reacquire"] += 1
                traces.append((seed, t, robot, proxy))
        else:
            stats["steps"].append(20)
    return stats


def summarize(stats):
    n = max(1, len(stats["steps"]))
    return {
        "success_rate": stats["success"] / n,
        "mean_steps": sum(stats["steps"]) / n,
        "reacquire_rate": stats["reacquire"] / max(1, stats["lost"]),
    }


def main():
    rows = []
    for seed, policy in enumerate(["naive", "proxy"], start=7):
        stats = simulate(policy, seed)
        row = {"policy": policy, **summarize(stats)}
        rows.append(row)

    with (OUT / "disappearing_goal_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    labels = [r["policy"] for r in rows]
    success = [r["success_rate"] for r in rows]
    reacq = [r["reacquire_rate"] for r in rows]
    x = range(len(labels))
    plt.figure(figsize=(5.5, 3.2))
    plt.bar([i - 0.15 for i in x], success, width=0.3, label="success")
    plt.bar([i + 0.15 for i in x], reacq, width=0.3, label="reacquire")
    plt.xticks(list(x), labels)
    plt.ylim(0, 1.05)
    plt.ylabel("rate")
    plt.title("Disappearing-goal toy study")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(OUT / "disappearing_goal_demo.png", dpi=200)


if __name__ == "__main__":
    main()
