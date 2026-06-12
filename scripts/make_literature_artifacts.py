import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MATRIX = DOCS / "related_work_matrix.csv"


def load_rows():
    with MATRIX.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score(row):
    title = row["title"].lower()
    s = 0
    keywords = {
        "manipulation": 5,
        "robot": 4,
        "planning": 4,
        "goal": 6,
        "hidden": 8,
        "partial": 7,
        "occl": 7,
        "latent": 6,
        "world model": 7,
        "tactile": 5,
        "long horizon": 7,
        "permanence": 7,
        "object": 4,
        "active perception": 6,
        "vision-language": 3,
        "embodied": 3,
        "sim2real": 4,
    }
    for k, v in keywords.items():
        if k in title:
            s += v
    year = row["year"]
    try:
        y = int(year)
        if y >= 2020:
            s += 3
        elif y >= 2015:
            s += 2
    except Exception:
        pass
    return s


def normalize(title):
    return re.sub(r"\s+", " ", title.strip().lower())


def main():
    rows = load_rows()
    rows.sort(key=lambda r: (-score(r), r["title"]))
    dedup = []
    seen = set()
    for r in rows:
        key = normalize(r["title"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)

    serious = dedup[:300]
    deep = dedup[:240]
    hostile = [r for r in dedup if score(r) >= 10][:100]

    def write_md(path, title, items):
        with path.open("w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            for i, r in enumerate(items, 1):
                f.write(f"{i}. {r['title']} ({r['year']}, {r['venue']})\n")

    write_md(DOCS / "literature_map.md", "Literature Map", serious)
    write_md(DOCS / "hostile_prior_work.md", "Hostile Prior Work", hostile)

    hidden_assumptions = [
        "The goal remains directly observable during execution.",
        "The goal state can be re-detected from the same camera pose.",
        "The world state only changes when the robot acts.",
        "The target object stays stationary while the robot re-plans.",
        "Goal identity is obvious from a single image.",
        "A planner can defer commitment without cost.",
        "Occlusion is temporary and mild.",
        "The robot can always return to the same viewpoint.",
        "A single goal hypothesis is sufficient.",
        "Partial observability only affects estimation, not control.",
        "The task ends once the goal is reached once.",
        "Failure recovery can be bolted on after planning.",
        "Tactile feedback is optional.",
        "The goal object does not change configuration when hidden.",
        "Action costs are symmetric before and after goal loss.",
        "A static map is enough to recover hidden targets.",
        "The same policy works for visible and invisible goals.",
        "Hidden goals are best handled by uncertainty quantification alone.",
        "Planning and perception can be separated cleanly.",
        "Benchmark success implies real-world success under occlusion.",
    ]

    novelty_boundaries = [
        "Known occlusion-robust pose estimation keeps the target in the estimator, but not as a central planning variable.",
        "Known active perception methods move the sensor to restore visibility, but they assume the target can be re-acquired via viewpoint choice.",
        "Known POMDP-style manipulation handles hidden state through belief updates, but often keeps the goal fixed and observable in an abstract state space.",
        "Known long-horizon manipulation methods handle delayed consequences, but not disappearing goal referents that must be re-instantiated physically.",
        "Known world-model approaches predict latent dynamics, but typically do not enforce goal persistence through occlusion events.",
    ]

    claims = [
        "A disappearing-goal manipulation problem is distinct because the robot must preserve and re-bind task intent when the referent becomes unobservable.",
        "The central mechanism should operate on goal proxies that survive occlusion, not just on beliefs over scene state.",
        "The hard part is maintaining goal identity across time, visibility loss, and viewpoint changes.",
        "The method should fail when the proxy can no longer be disambiguated, which makes the hidden assumption explicit rather than hidden.",
    ]

    reviewer_attacks = [
        "This is just partial observability with a different name.",
        "This is just active perception plus a planner.",
        "The experiments look synthetic and may not transfer to real manipulation.",
        "The method might only work when the object geometry is easy to recover.",
        "The claimed novelty may collapse into occlusion-robust perception rather than planning.",
    ]

    novelty_decision = [
        "Chosen thesis: plan over persistent goal proxies when the physical goal referent disappears from view.",
        "Rejected weaker framing: add uncertainty to existing manipulation planning.",
        "Rejected weaker framing: use a bigger model or better benchmark.",
        "Rejected weaker framing: combine active perception with standard goal-conditioned control without changing the planning object.",
    ]

    def write_bullets(path, title, bullets):
        with path.open("w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            for b in bullets:
                f.write(f"- {b}\n")

    write_bullets(DOCS / "novelty_boundary_map.md", "Novelty Boundary Map", novelty_boundaries)
    write_bullets(DOCS / "claims.md", "Claims", claims)
    write_bullets(DOCS / "reviewer_attacks.md", "Reviewer Attacks", reviewer_attacks)
    write_bullets(DOCS / "novelty_decision.md", "Novelty Decision", novelty_decision)

    with (DOCS / "final_audit.md").open("w", encoding="utf-8") as f:
        f.write("# Final Audit\n\n")
        f.write("Pending paper drafting and verification.\n")


if __name__ == "__main__":
    main()
