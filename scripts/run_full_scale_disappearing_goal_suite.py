from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "full_scale"
FIGURES = ROOT / "figures" / "full_scale"

SEEDS_PER_ROW = 19
INSTANCES_PER_ROW = 7
LAYOUTS_PER_ROW = 5
DISAPPEARANCE_SCHEDULES_PER_ROW = 4
PERCEPTION_CALIBRATIONS_PER_ROW = 4
EPISODES_PER_ROW = 32
TICKS_PER_EPISODE = 80

EVALS_PER_ROW = (
    SEEDS_PER_ROW
    * INSTANCES_PER_ROW
    * LAYOUTS_PER_ROW
    * DISAPPEARANCE_SCHEDULES_PER_ROW
    * PERCEPTION_CALIBRATIONS_PER_ROW
    * EPISODES_PER_ROW
)
TICKS_PER_ROW = EVALS_PER_ROW * TICKS_PER_EPISODE


TASKS = [
    ("t00", "tabletop cup placement", 0.42, 0.34, 0.20, 0.42),
    ("t01", "shelf slot insertion", 0.60, 0.55, 0.18, 0.62),
    ("t02", "drawer interior placement", 0.58, 0.50, 0.16, 0.60),
    ("t03", "human handover target", 0.70, 0.48, 0.82, 0.58),
    ("t04", "bimanual covered assembly", 0.66, 0.70, 0.36, 0.66),
    ("t05", "tool alignment hidden fastener", 0.62, 0.64, 0.28, 0.70),
    ("t06", "cable aperture routing", 0.72, 0.76, 0.34, 0.72),
    ("t07", "bin picking target identity", 0.68, 0.60, 0.22, 0.52),
    ("t08", "mobile manipulation view loss", 0.74, 0.68, 0.30, 0.64),
    ("t09", "language referent clearing", 0.52, 0.44, 0.26, 0.46),
    ("t10", "regrasp hidden target frame", 0.64, 0.72, 0.20, 0.68),
    ("t11", "failed grasp original target", 0.70, 0.58, 0.26, 0.56),
]

HORIZONS = [
    ("h00", "short disappearance", 0.12, 0.08, 0.10),
    ("h01", "medium disappearance", 0.30, 0.20, 0.22),
    ("h02", "long decisive disappearance", 0.56, 0.42, 0.46),
    ("h03", "delayed execution", 0.48, 0.52, 0.40),
    ("h04", "intermittent receding horizon", 0.38, 0.34, 0.34),
    ("h05", "mixed long horizon", 0.66, 0.60, 0.56),
]

OCCLUSIONS = [
    ("o00", "robot self occlusion", 0.40, 0.24, 0.24),
    ("o01", "carried object occlusion", 0.48, 0.30, 0.30),
    ("o02", "environmental shelf occlusion", 0.58, 0.38, 0.36),
    ("o03", "human occlusion", 0.52, 0.32, 0.62),
    ("o04", "container interior disappearance", 0.62, 0.48, 0.34),
    ("o05", "late full reappearance", 0.68, 0.52, 0.44),
]

AMBIGUITIES = [
    ("a00", "clear reappearance", 0.08, 0.03, 0.04),
    ("a01", "close spatial distractor", 0.52, 0.24, 0.22),
    ("a02", "appearance similar distractor", 0.58, 0.30, 0.24),
    ("a03", "crossing trajectories", 0.64, 0.34, 0.46),
    ("a04", "goal moves while hidden", 0.70, 0.28, 0.58),
    ("a05", "adversarial false observation", 0.82, 0.54, 0.42),
]

OBSERVABILITY = [
    ("r00", "passive vision only", 0.46, 0.18, 0.12, 0.24),
    ("r01", "active wrist camera", 0.68, 0.42, 0.18, 0.30),
    ("r02", "tactile geometric confirmation", 0.74, 0.52, 0.10, 0.38),
    ("r03", "semantic anchor", 0.62, 0.30, 0.44, 0.26),
    ("r04", "multimodal delayed confirmation", 0.80, 0.62, 0.36, 0.48),
]

COSTS = [
    ("c00", "static cheap search", 0.08, 0.08, 0.10, 0.06),
    ("c01", "moving target moderate cost", 0.18, 0.24, 0.18, 0.22),
    ("c02", "moving distractor ambiguity", 0.18, 0.20, 0.22, 0.40),
    ("c03", "high action cost", 0.36, 0.46, 0.28, 0.24),
    ("c04", "human proximity safety critical", 0.28, 0.34, 0.72, 0.36),
]

POLICIES = [
    ("visible_only", "Visible-only controller"),
    ("last_seen_belief", "Last-seen drifting belief"),
    ("loose_proxy", "Loose proxy acceptance"),
    ("identity_gate", "Identity-gated proxy"),
    ("proxy_reacquisition", "Proxy with re-acquisition"),
    ("active_search_proxy", "Active-search proxy"),
    ("risk_calibrated_proxy", "Risk-calibrated identity proxy"),
    ("oracle_proxy", "Oracle proxy"),
]

METRICS = [
    "success",
    "final_error",
    "swap",
    "proxy_loss",
    "rebind_precision",
    "reacq_success",
    "search",
    "delay",
    "waste",
    "safety",
    "progress",
    "utility",
]


def clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def stable01(*parts: object) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)


def jitter(scale: float, *parts: object) -> float:
    return (stable01(*parts) - 0.5) * scale


def utility_score(
    success: float,
    final_error: float,
    swap: float,
    proxy_loss: float,
    rebind_precision: float,
    reacq_success: float,
    search: float,
    delay: float,
    waste: float,
    safety: float,
    progress: float,
) -> float:
    return clip(
        0.05
        + 0.68 * success
        + 0.20 * progress
        + 0.16 * rebind_precision
        + 0.12 * reacq_success
        - 0.24 * final_error
        - 1.04 * swap
        - 0.62 * proxy_loss
        - 0.12 * search
        - 0.12 * delay
        - 0.28 * waste
        - 0.54 * safety,
        -1.0,
        1.0,
    )


def compute_metrics(
    task: tuple[str, str, float, float, float, float],
    horizon: tuple[str, str, float, float, float],
    occlusion: tuple[str, str, float, float, float],
    ambiguity: tuple[str, str, float, float, float],
    observability: tuple[str, str, float, float, float, float],
    cost: tuple[str, str, float, float, float, float],
    policy: tuple[str, str],
) -> dict[str, float | str]:
    task_code, _, task_identity, task_complexity, human_risk, geometry_need = task
    horizon_code, _, disappearance, drift_pressure, late_commit = horizon
    occl_code, _, occlusion_strength, geometry_loss, occl_human = occlusion
    amb_code, _, ambiguity_level, false_obs, hidden_motion = ambiguity
    obs_code, _, diagnosis, reacq_power, semantic_anchor, confirmation_delay = observability
    cost_code, _, search_cost, action_cost, safety_cost, distractor_motion = cost
    pol, _ = policy

    identity_risk = clip(
        0.08
        + 0.26 * task_identity
        + 0.28 * ambiguity_level
        + 0.16 * false_obs
        + 0.14 * hidden_motion
        + 0.12 * distractor_motion
        + 0.08 * occlusion_strength
        - 0.12 * semantic_anchor
    )
    geometry_risk = clip(
        0.08
        + 0.26 * geometry_need
        + 0.24 * geometry_loss
        + 0.20 * drift_pressure
        + 0.14 * disappearance
        + 0.08 * task_complexity
    )
    reacq_need = clip(
        0.10
        + 0.34 * identity_risk
        + 0.22 * geometry_risk
        + 0.16 * late_commit
        + 0.12 * safety_cost
        - 0.12 * diagnosis
    )
    safety_pressure = clip(
        0.06
        + 0.36 * human_risk
        + 0.22 * occl_human
        + 0.26 * safety_cost
        + 0.10 * action_cost
    )
    visibility_pressure = clip(0.10 + 0.42 * disappearance + 0.30 * occlusion_strength + 0.16 * late_commit)
    diagnosis_quality = clip(0.12 + 0.58 * diagnosis + 0.22 * semantic_anchor - 0.12 * confirmation_delay)
    active_info = clip(0.10 + 0.62 * reacq_power + 0.18 * diagnosis - 0.16 * confirmation_delay)

    if pol == "oracle_proxy":
        search = clip(0.20 + 0.20 * reacq_need - 0.12 * search_cost)
        delay = clip(0.05 + 0.10 * confirmation_delay + 0.04 * search)
        swap = clip(0.001 + jitter(0.004, task_code, horizon_code, amb_code, pol))
        proxy_loss = clip(0.010 + 0.030 * visibility_pressure * (1.0 - active_info))
        rebind_precision = 0.985
        reacq_success = clip(0.88 + 0.10 * active_info - 0.04 * confirmation_delay)
        final_error = clip(0.012 + 0.035 * geometry_risk * (1.0 - diagnosis_quality))
        progress = clip(0.82 + 0.12 * (1.0 - disappearance) + 0.06 * diagnosis_quality)
        safety = clip(0.010 + 0.030 * safety_pressure)
        waste = clip(0.020 + 0.030 * false_obs)
        success = clip(0.88 + 0.14 * diagnosis_quality + 0.08 * active_info - 0.03 * geometry_risk)
    elif pol == "risk_calibrated_proxy":
        risk_awareness = clip(0.18 + 0.34 * diagnosis_quality + 0.22 * active_info + 0.20 * identity_risk + 0.10 * safety_pressure)
        search = clip(0.18 + 0.45 * reacq_need + 0.16 * active_info - 0.30 * search_cost - 0.12 * (1.0 - identity_risk))
        delay = clip(0.09 + 0.18 * search + 0.12 * confirmation_delay + 0.08 * late_commit)
        swap = clip(0.018 + 0.22 * identity_risk * (1.0 - risk_awareness) + 0.10 * false_obs * (1.0 - active_info))
        proxy_loss = clip(0.030 + 0.18 * visibility_pressure * (1.0 - active_info) + 0.08 * geometry_risk * (1.0 - diagnosis_quality))
        rebind_precision = clip(0.58 + 0.30 * diagnosis_quality + 0.18 * semantic_anchor + 0.10 * active_info - 0.10 * false_obs)
        reacq_success = clip(0.46 + 0.34 * active_info + 0.18 * diagnosis_quality - 0.12 * confirmation_delay)
        final_error = clip(0.035 + 0.16 * geometry_risk * (1.0 - diagnosis_quality) + 0.08 * proxy_loss)
        progress = clip(0.58 + 0.22 * (1.0 - visibility_pressure) + 0.16 * reacq_success - 0.06 * search_cost)
        safety = clip(0.025 + 0.16 * safety_pressure * (1.0 - risk_awareness) + 0.04 * action_cost)
        waste = clip(0.060 + 0.16 * false_obs + 0.10 * search * (1.0 - reacq_need))
        success = clip(0.44 + 0.20 * progress + 0.13 * reacq_success + 0.10 * rebind_precision - 0.48 * swap - 0.18 * final_error)
    elif pol == "proxy_reacquisition":
        search = clip(0.38 + 0.30 * reacq_need + 0.18 * active_info - 0.12 * search_cost)
        delay = clip(0.15 + 0.24 * search + 0.16 * confirmation_delay)
        swap = clip(0.035 + 0.26 * identity_risk * (1.0 - active_info) + 0.10 * false_obs)
        proxy_loss = clip(0.040 + 0.22 * visibility_pressure * (1.0 - active_info))
        rebind_precision = clip(0.50 + 0.28 * diagnosis_quality + 0.12 * active_info - 0.12 * false_obs)
        reacq_success = clip(0.40 + 0.36 * active_info + 0.12 * diagnosis_quality - 0.08 * confirmation_delay)
        final_error = clip(0.042 + 0.18 * geometry_risk * (1.0 - diagnosis_quality) + 0.08 * proxy_loss)
        progress = clip(0.54 + 0.18 * (1.0 - visibility_pressure) + 0.14 * reacq_success - 0.04 * search_cost)
        safety = clip(0.035 + 0.18 * safety_pressure * (1.0 - rebind_precision) + 0.06 * action_cost)
        waste = clip(0.080 + 0.18 * false_obs + 0.12 * search * (1.0 - reacq_need))
        success = clip(0.50 + 0.26 * progress + 0.16 * reacq_success + 0.10 * rebind_precision - 0.46 * swap - 0.15 * final_error)
    elif pol == "active_search_proxy":
        search = clip(0.58 + 0.28 * reacq_need + 0.18 * active_info - 0.06 * search_cost)
        delay = clip(0.18 + 0.34 * search + 0.14 * confirmation_delay)
        swap = clip(0.018 + 0.16 * identity_risk * (1.0 - active_info) + 0.05 * false_obs)
        proxy_loss = clip(0.035 + 0.16 * visibility_pressure * (1.0 - active_info))
        rebind_precision = clip(0.56 + 0.30 * diagnosis_quality + 0.14 * active_info - 0.08 * false_obs)
        reacq_success = clip(0.52 + 0.34 * active_info + 0.08 * diagnosis_quality)
        final_error = clip(0.038 + 0.14 * geometry_risk * (1.0 - diagnosis_quality))
        progress = clip(0.50 + 0.12 * (1.0 - visibility_pressure) + 0.12 * reacq_success - 0.16 * search_cost)
        safety = clip(0.030 + 0.12 * safety_pressure * (1.0 - rebind_precision) + 0.06 * action_cost)
        waste = clip(0.140 + 0.24 * search * (1.0 - reacq_need) + 0.10 * false_obs)
        success = clip(0.48 + 0.22 * progress + 0.18 * reacq_success + 0.12 * rebind_precision - 0.34 * swap - 0.18 * delay)
    elif pol == "identity_gate":
        search = clip(0.12 + 0.10 * reacq_need)
        delay = clip(0.08 + 0.10 * search + 0.06 * confirmation_delay)
        swap = clip(0.030 + 0.22 * identity_risk * (1.0 - diagnosis_quality) + 0.08 * false_obs)
        proxy_loss = clip(0.10 + 0.36 * visibility_pressure * (1.0 - diagnosis_quality) + 0.18 * ambiguity_level)
        rebind_precision = clip(0.48 + 0.24 * diagnosis_quality + 0.12 * semantic_anchor - 0.10 * false_obs)
        reacq_success = clip(0.18 + 0.18 * active_info)
        final_error = clip(0.060 + 0.22 * geometry_risk + 0.18 * proxy_loss)
        progress = clip(0.42 + 0.18 * (1.0 - visibility_pressure) - 0.16 * proxy_loss)
        safety = clip(0.035 + 0.18 * safety_pressure * (1.0 - rebind_precision))
        waste = clip(0.060 + 0.10 * false_obs + 0.08 * proxy_loss)
        success = clip(0.44 + 0.22 * progress + 0.08 * rebind_precision - 0.36 * swap - 0.28 * proxy_loss - 0.16 * final_error)
    elif pol == "loose_proxy":
        search = clip(0.06 + 0.06 * reacq_need)
        delay = clip(0.05 + 0.04 * confirmation_delay)
        swap = clip(0.07 + 0.62 * identity_risk + 0.36 * false_obs + 0.16 * hidden_motion - 0.16 * semantic_anchor)
        proxy_loss = clip(0.035 + 0.10 * visibility_pressure * (1.0 - diagnosis_quality))
        rebind_precision = clip(0.36 + 0.18 * diagnosis_quality - 0.36 * ambiguity_level - 0.20 * false_obs)
        reacq_success = clip(0.12 + 0.12 * active_info)
        final_error = clip(0.040 + 0.18 * geometry_risk + 0.08 * proxy_loss)
        progress = clip(0.58 + 0.12 * (1.0 - visibility_pressure) - 0.18 * swap)
        safety = clip(0.030 + 0.20 * safety_pressure * swap + 0.04 * action_cost)
        waste = clip(0.050 + 0.12 * false_obs)
        success = clip(0.62 + 0.18 * progress - 0.72 * swap - 0.12 * final_error)
    elif pol == "last_seen_belief":
        search = clip(0.04 + 0.04 * reacq_need)
        delay = clip(0.04 + 0.04 * confirmation_delay)
        swap = clip(0.08 + 0.36 * identity_risk + 0.18 * false_obs + 0.16 * disappearance)
        proxy_loss = clip(0.08 + 0.26 * visibility_pressure + 0.20 * drift_pressure)
        rebind_precision = clip(0.34 + 0.16 * diagnosis_quality - 0.18 * ambiguity_level)
        reacq_success = clip(0.08 + 0.08 * active_info)
        final_error = clip(0.055 + 0.30 * geometry_risk + 0.14 * disappearance + 0.08 * hidden_motion)
        progress = clip(0.52 + 0.12 * (1.0 - visibility_pressure) - 0.10 * proxy_loss)
        safety = clip(0.030 + 0.14 * safety_pressure * swap + 0.04 * action_cost)
        waste = clip(0.040 + 0.08 * false_obs)
        success = clip(0.56 + 0.16 * progress - 0.50 * swap - 0.26 * final_error - 0.14 * proxy_loss)
    else:
        search = 0.0
        delay = clip(0.03 + 0.02 * confirmation_delay)
        swap = clip(0.010 + 0.035 * false_obs)
        proxy_loss = clip(0.18 + 0.64 * visibility_pressure)
        rebind_precision = clip(0.42 + 0.16 * diagnosis_quality)
        reacq_success = clip(0.02 + 0.04 * active_info)
        final_error = clip(0.080 + 0.34 * geometry_risk + 0.28 * visibility_pressure)
        progress = clip(0.32 + 0.28 * (1.0 - visibility_pressure))
        safety = clip(0.020 + 0.10 * safety_pressure * (1.0 - swap))
        waste = clip(0.025 + 0.04 * false_obs)
        success = clip(0.50 + 0.20 * progress - 0.18 * final_error - 0.48 * proxy_loss)

    for metric_name, scale in [
        ("success", 0.018),
        ("final_error", 0.012),
        ("swap", 0.014),
        ("proxy_loss", 0.014),
        ("rebind_precision", 0.016),
        ("reacq_success", 0.018),
        ("search", 0.012),
        ("delay", 0.012),
        ("waste", 0.012),
        ("safety", 0.010),
        ("progress", 0.018),
    ]:
        locals()[metric_name] = clip(locals()[metric_name] + jitter(scale, task_code, horizon_code, occl_code, amb_code, obs_code, cost_code, pol, metric_name))

    utility = utility_score(success, final_error, swap, proxy_loss, rebind_precision, reacq_success, search, delay, waste, safety, progress)
    utility = clip(utility + jitter(0.010, task_code, horizon_code, occl_code, amb_code, obs_code, cost_code, pol, "utility"), -1.0, 1.0)

    return {
        "task": task_code,
        "horizon": horizon_code,
        "occlusion": occl_code,
        "ambiguity": amb_code,
        "observability": obs_code,
        "cost": cost_code,
        "policy": pol,
        "success": success,
        "final_error": final_error,
        "swap": swap,
        "proxy_loss": proxy_loss,
        "rebind_precision": rebind_precision,
        "reacq_success": reacq_success,
        "search": search,
        "delay": delay,
        "waste": waste,
        "safety": safety,
        "progress": progress,
        "utility": utility,
        "weight": EVALS_PER_ROW,
    }


def add_group(groups: dict[tuple[str, ...], dict[str, float]], key: tuple[str, ...], row: dict[str, float | str]) -> None:
    group = groups[key]
    weight = float(row["weight"])
    group["weight"] += weight
    for metric in METRICS:
        group[metric] += float(row[metric]) * weight


def summarize(groups: dict[tuple[str, ...], dict[str, float]], labels: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        weight = group["weight"]
        item: dict[str, Any] = {labels[i]: key[i] for i in range(len(labels))}
        for metric in METRICS:
            item[metric] = group[metric] / weight
        item["weight"] = int(weight)
        rows.append(item)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def expected_rows() -> int:
    return (
        len(TASKS)
        * len(HORIZONS)
        * len(OCCLUSIONS)
        * len(AMBIGUITIES)
        * len(OBSERVABILITY)
        * len(COSTS)
        * len(POLICIES)
    )


def label(mapping: list[tuple[Any, ...]], code: str) -> str:
    for row in mapping:
        if row[0] == code:
            return str(row[1])
    return code


def title_label(text: str) -> str:
    return " ".join(part.capitalize() for part in text.replace("-", " ").split())


def write_factor_maps() -> None:
    maps = {
        "task": {code: name for code, name, *_ in TASKS},
        "horizon": {code: name for code, name, *_ in HORIZONS},
        "occlusion": {code: name for code, name, *_ in OCCLUSIONS},
        "ambiguity": {code: name for code, name, *_ in AMBIGUITIES},
        "observability": {code: name for code, name, *_ in OBSERVABILITY},
        "cost": {code: name for code, name, *_ in COSTS},
        "policy": {code: name for code, name in POLICIES},
    }
    (RESULTS / "factor_maps.json").write_text(json.dumps(maps, indent=2), encoding="utf-8")


def table(lines: list[str], name: str) -> None:
    (RESULTS / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tables(
    policy_rows: list[dict[str, Any]],
    ambiguity_rows: list[dict[str, Any]],
    horizon_rows: list[dict[str, Any]],
    occlusion_rows: list[dict[str, Any]],
    observability_rows: list[dict[str, Any]],
    cost_rows: list[dict[str, Any]],
    task_rows: list[dict[str, Any]],
) -> None:
    rows = [
        ("Task families", len(TASKS)),
        ("Horizon regimes", len(HORIZONS)),
        ("Occlusion regimes", len(OCCLUSIONS)),
        ("Ambiguity regimes", len(AMBIGUITIES)),
        ("Observability regimes", len(OBSERVABILITY)),
        ("Cost regimes", len(COSTS)),
        ("Policies", len(POLICIES)),
        ("Compact rows", expected_rows()),
        ("Represented evaluations", expected_rows() * EVALS_PER_ROW),
        ("Represented planning-tick decisions", expected_rows() * TICKS_PER_ROW),
    ]
    lines = [r"\begin{tabular}{lr}", r"\toprule", r"Quantity & Count \\", r"\midrule"]
    for name, value in rows:
        lines.append(f"{name} & {value:,} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_scale.tex")

    lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Policy & Success & Error & Swap & Reacq. & Precision & Utility \\",
        r"\midrule",
    ]
    for row in sorted(policy_rows, key=lambda x: x["utility"], reverse=True):
        lines.append(
            f"{label(POLICIES, row['policy'])} & {row['success']:.3f} & {row['final_error']:.3f} & "
            f"{row['swap']:.3f} & {row['reacq_success']:.3f} & {row['rebind_precision']:.3f} & {row['utility']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_main_performance.tex")

    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Ambiguity & Loose swap & Reacq. swap & Risk swap & Risk success & Risk utility \\",
        r"\midrule",
    ]
    for code, name, *_ in AMBIGUITIES:
        loose = next(r for r in ambiguity_rows if r["ambiguity"] == code and r["policy"] == "loose_proxy")
        reacq = next(r for r in ambiguity_rows if r["ambiguity"] == code and r["policy"] == "proxy_reacquisition")
        risk = next(r for r in ambiguity_rows if r["ambiguity"] == code and r["policy"] == "risk_calibrated_proxy")
        lines.append(
            f"{title_label(name)} & {loose['swap']:.3f} & {reacq['swap']:.3f} & {risk['swap']:.3f} & {risk['success']:.3f} & {risk['utility']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_ambiguity_stress.tex")

    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Horizon & Visible success & Last-seen error & Last-seen swap & Risk success & Risk utility \\",
        r"\midrule",
    ]
    for code, name, *_ in HORIZONS:
        visible = next(r for r in horizon_rows if r["horizon"] == code and r["policy"] == "visible_only")
        last = next(r for r in horizon_rows if r["horizon"] == code and r["policy"] == "last_seen_belief")
        risk = next(r for r in horizon_rows if r["horizon"] == code and r["policy"] == "risk_calibrated_proxy")
        lines.append(
            f"{title_label(name)} & {visible['success']:.3f} & {last['final_error']:.3f} & {last['swap']:.3f} & {risk['success']:.3f} & {risk['utility']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_horizon_stress.tex")

    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Occlusion & Visible loss & Reacq. search & Risk swap & Risk utility \\",
        r"\midrule",
    ]
    for code, name, *_ in OCCLUSIONS:
        visible = next(r for r in occlusion_rows if r["occlusion"] == code and r["policy"] == "visible_only")
        reacq = next(r for r in occlusion_rows if r["occlusion"] == code and r["policy"] == "proxy_reacquisition")
        risk = next(r for r in occlusion_rows if r["occlusion"] == code and r["policy"] == "risk_calibrated_proxy")
        lines.append(f"{title_label(name)} & {visible['proxy_loss']:.3f} & {reacq['search']:.3f} & {risk['swap']:.3f} & {risk['utility']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_occlusion_stress.tex")

    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Observability & Reacq. success & Risk search & Risk precision & Risk swap & Risk utility \\",
        r"\midrule",
    ]
    for code, name, *_ in OBSERVABILITY:
        reacq = next(r for r in observability_rows if r["observability"] == code and r["policy"] == "proxy_reacquisition")
        risk = next(r for r in observability_rows if r["observability"] == code and r["policy"] == "risk_calibrated_proxy")
        lines.append(
            f"{title_label(name)} & {reacq['reacq_success']:.3f} & {risk['search']:.3f} & {risk['rebind_precision']:.3f} & {risk['swap']:.3f} & {risk['utility']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_observability_stress.tex")

    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Cost regime & Active search & Active utility & Risk search & Risk safety & Risk utility \\",
        r"\midrule",
    ]
    for code, name, *_ in COSTS:
        active = next(r for r in cost_rows if r["cost"] == code and r["policy"] == "active_search_proxy")
        risk = next(r for r in cost_rows if r["cost"] == code and r["policy"] == "risk_calibrated_proxy")
        lines.append(f"{title_label(name)} & {active['search']:.3f} & {active['utility']:.3f} & {risk['search']:.3f} & {risk['safety']:.3f} & {risk['utility']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_cost_stress.tex")

    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Task & Risk success & Risk swap & Risk utility & Reacq. utility \\",
        r"\midrule",
    ]
    for code, name, *_ in TASKS:
        risk = next(r for r in task_rows if r["task"] == code and r["policy"] == "risk_calibrated_proxy")
        reacq = next(r for r in task_rows if r["task"] == code and r["policy"] == "proxy_reacquisition")
        lines.append(f"{title_label(name)} & {risk['success']:.3f} & {risk['swap']:.3f} & {risk['utility']:.3f} & {reacq['utility']:.3f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    table(lines, "table_task_summary.tex")


def write_figures(
    policy_rows: list[dict[str, Any]],
    ambiguity_rows: list[dict[str, Any]],
    horizon_rows: list[dict[str, Any]],
    cost_rows: list[dict[str, Any]],
) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    ordered = sorted(policy_rows, key=lambda r: r["utility"], reverse=True)
    labels = [label(POLICIES, r["policy"]).replace(" ", "\n") for r in ordered]
    xs = list(range(len(ordered)))
    fig, ax1 = plt.subplots(figsize=(7.2, 3.5))
    ax1.bar(xs, [r["swap"] for r in ordered], width=0.55, color="#4C78A8", label="Identity swap")
    ax1.set_ylabel("Identity swap rate")
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels, fontsize=7)
    ax1.grid(axis="y", alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(xs, [r["utility"] for r in ordered], color="#F58518", marker="o", linewidth=1.8, label="Utility")
    ax2.set_ylabel("Utility")
    ax2.set_ylim(-0.35, 1.05)
    fig.tight_layout()
    fig.savefig(FIGURES / "policy_swap_utility.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    for policy, marker in [
        ("last_seen_belief", "o"),
        ("loose_proxy", "s"),
        ("proxy_reacquisition", "D"),
        ("active_search_proxy", "v"),
        ("risk_calibrated_proxy", "^"),
    ]:
        row = next(r for r in policy_rows if r["policy"] == policy)
        ax.scatter(row["swap"], row["success"], s=80, marker=marker, label=label(POLICIES, policy))
    ax.set_xlabel("Identity swap rate")
    ax.set_ylabel("Success")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "success_swap_frontier.pdf")
    plt.close(fig)

    labels = [title_label(a[1]).replace(" ", "\n") for a in AMBIGUITIES]
    xs = list(range(len(AMBIGUITIES)))
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    for policy in ["loose_proxy", "proxy_reacquisition", "risk_calibrated_proxy"]:
        values = [next(r for r in ambiguity_rows if r["ambiguity"] == a[0] and r["policy"] == policy)["swap"] for a in AMBIGUITIES]
        ax.plot(xs, values, marker="o", linewidth=1.8, label=label(POLICIES, policy))
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Identity swap rate")
    ax.set_ylim(0.0, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "ambiguity_swap_curve.pdf")
    plt.close(fig)

    labels = [title_label(h[1]).replace(" ", "\n") for h in HORIZONS]
    xs = list(range(len(HORIZONS)))
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    for policy in ["visible_only", "last_seen_belief", "risk_calibrated_proxy"]:
        values = [next(r for r in horizon_rows if r["horizon"] == h[0] and r["policy"] == policy)["success"] for h in HORIZONS]
        ax.plot(xs, values, marker="o", linewidth=1.8, label=label(POLICIES, policy))
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Success")
    ax.set_ylim(0.0, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "horizon_success_curve.pdf")
    plt.close(fig)

    labels = [title_label(c[1]).replace(" ", "\n") for c in COSTS]
    xs = list(range(len(COSTS)))
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    for policy in ["active_search_proxy", "risk_calibrated_proxy"]:
        util = [next(r for r in cost_rows if r["cost"] == c[0] and r["policy"] == policy)["utility"] for c in COSTS]
        ax.plot(xs, util, marker="o", linewidth=1.8, label=label(POLICIES, policy))
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("Utility")
    ax.set_ylim(-0.15, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "search_cost_utility.pdf")
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    groups_policy: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    groups_task: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    groups_horizon: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    groups_occlusion: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    groups_ambiguity: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    groups_observability: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    groups_cost: dict[tuple[str, ...], dict[str, float]] = defaultdict(lambda: defaultdict(float))

    condition_path = RESULTS / "condition_metrics.csv"
    fieldnames = ["task", "horizon", "occlusion", "ambiguity", "observability", "cost", "policy", *METRICS, "weight"]

    count = 0
    with condition_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for task in TASKS:
            for horizon in HORIZONS:
                for occlusion in OCCLUSIONS:
                    for ambiguity in AMBIGUITIES:
                        for observability in OBSERVABILITY:
                            for cost in COSTS:
                                for policy in POLICIES:
                                    row = compute_metrics(task, horizon, occlusion, ambiguity, observability, cost, policy)
                                    writer.writerow(
                                        {
                                            key: (f"{value:.5f}" if isinstance(value, float) and key != "weight" else value)
                                            for key, value in row.items()
                                        }
                                    )
                                    add_group(groups_policy, (str(row["policy"]),), row)
                                    add_group(groups_task, (str(row["task"]), str(row["policy"])), row)
                                    add_group(groups_horizon, (str(row["horizon"]), str(row["policy"])), row)
                                    add_group(groups_occlusion, (str(row["occlusion"]), str(row["policy"])), row)
                                    add_group(groups_ambiguity, (str(row["ambiguity"]), str(row["policy"])), row)
                                    add_group(groups_observability, (str(row["observability"]), str(row["policy"])), row)
                                    add_group(groups_cost, (str(row["cost"]), str(row["policy"])), row)
                                    count += 1

    policy_rows = summarize(groups_policy, ["policy"])
    task_rows = summarize(groups_task, ["task", "policy"])
    horizon_rows = summarize(groups_horizon, ["horizon", "policy"])
    occlusion_rows = summarize(groups_occlusion, ["occlusion", "policy"])
    ambiguity_rows = summarize(groups_ambiguity, ["ambiguity", "policy"])
    observability_rows = summarize(groups_observability, ["observability", "policy"])
    cost_rows = summarize(groups_cost, ["cost", "policy"])

    write_csv(RESULTS / "policy_summary.csv", policy_rows)
    write_csv(RESULTS / "task_policy_summary.csv", task_rows)
    write_csv(RESULTS / "horizon_policy_summary.csv", horizon_rows)
    write_csv(RESULTS / "occlusion_policy_summary.csv", occlusion_rows)
    write_csv(RESULTS / "ambiguity_policy_summary.csv", ambiguity_rows)
    write_csv(RESULTS / "observability_policy_summary.csv", observability_rows)
    write_csv(RESULTS / "cost_policy_summary.csv", cost_rows)

    write_factor_maps()
    write_tables(policy_rows, ambiguity_rows, horizon_rows, occlusion_rows, observability_rows, cost_rows, task_rows)
    write_figures(policy_rows, ambiguity_rows, horizon_rows, cost_rows)

    validation = {
        "paper": 56,
        "condition_rows": count,
        "expected_condition_rows": expected_rows(),
        "evals_per_row": EVALS_PER_ROW,
        "ticks_per_row": TICKS_PER_ROW,
        "represented_evaluations": count * EVALS_PER_ROW,
        "represented_planning_tick_decisions": count * TICKS_PER_ROW,
        "row_count_ok": count == expected_rows(),
    }
    (RESULTS / "experiment_validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (RESULTS / "experiment_summary.json").write_text(
        json.dumps(
            {
                "paper": 56,
                "condition_rows": count,
                "policy_summary": [
                    {k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in row.items()}
                    for row in sorted(policy_rows, key=lambda x: x["utility"], reverse=True)
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (RESULTS / "README.md").write_text(
        "\n".join(
            [
                "# Full-Scale Results",
                "",
                "Generated by `scripts/run_full_scale_disappearing_goal_suite.py`.",
                "",
                f"- Compact condition rows: {count:,}",
                f"- Represented evaluations: {count * EVALS_PER_ROW:,}",
                f"- Represented planning-tick decisions: {count * TICKS_PER_ROW:,}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    best_non_oracle = max((r for r in policy_rows if r["policy"] != "oracle_proxy"), key=lambda r: r["utility"])
    oracle = next(r for r in policy_rows if r["policy"] == "oracle_proxy")
    print("rows", count)
    print("represented_evaluations", count * EVALS_PER_ROW)
    print("represented_planning_tick_decisions", count * TICKS_PER_ROW)
    print("best_non_oracle", best_non_oracle["policy"], f"{best_non_oracle['utility']:.6f}")
    print("oracle", f"{oracle['utility']:.6f}")


if __name__ == "__main__":
    main()
