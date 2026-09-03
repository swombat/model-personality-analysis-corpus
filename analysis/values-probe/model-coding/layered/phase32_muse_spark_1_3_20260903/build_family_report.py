#!/usr/bin/env python3
"""Build quantitative tables for the six-model Meta Muse family comparison."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[4]
CORPUS = ROOT.parent / "model-personality-corpus-v2"
POSTURE = PHASE / "posture_collapsed/consensus.jsonl"
LAYER_A = PHASE / "layer_a/consensus_300.jsonl"
CELLS = [
    ("Spark 1.1 Main", "muse-spark-1-1", "muse-spark-1-1-or-pin-meta-20260813"),
    ("Spark 1.2 Main", "muse-spark-1-2", "muse-spark-1-2-or-pin-meta-20260813"),
    (
        "Spark 1.2 Contributor",
        "muse-spark-1-2-contributor",
        "muse-spark-1-2-contributor-or-pin-meta",
    ),
    (
        "Glimmer 30B",
        "muse-glimmer-30b",
        "muse-glimmer-30b-or-pin-deepinfra-20260813",
    ),
    ("Spark 1.3 Main", "muse-spark-1-3", "muse-spark-1-3-or-pin-meta"),
    (
        "Spark 1.3 Contributor",
        "muse-spark-1-3-contributor",
        "muse-spark-1-3-contributor-or-pin-meta",
    ),
]


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def traces(kind: str, cell: str) -> list[dict]:
    if kind == "freeflow":
        directory = CORPUS / "data/traces_freeflow" / f"freeflow_{cell}"
    else:
        directory = CORPUS / "data/traces_values" / cell
    return [json.loads(path.read_text()) for path in sorted(directory.glob("*.json"))]


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "—"


def main() -> None:
    posture = jsonl(POSTURE)
    layer_a = jsonl(LAYER_A)
    posture_by_cell: dict[str, list[dict]] = defaultdict(list)
    topics_by_cell: dict[str, Counter[str]] = defaultdict(Counter)
    for row in posture:
        posture_by_cell[row["cell"]].append(row)
    layer_to_cell = {
        row["layered_id"]: row["cell"] for row in jsonl(PHASE / "manifest_phase32.jsonl")
    }
    for row in layer_a:
        cell = layer_to_cell[row["layered_id"]]
        topics_by_cell[cell].update(
            topic["topic_key"] for topic in row.get("consensus_topics", [])
        )

    docs_by_cell: dict[str, list[str]] = {}
    metrics = []
    for display, model, cell in CELLS:
        freeflow = traces("freeflow", cell)
        values = traces("values", cell)
        ff_texts = [(row.get("result") or "").strip() for row in freeflow]
        val_texts = [(row.get("result") or "").strip() for row in values]
        docs_by_cell[cell] = ff_texts
        p_rows = posture_by_cell[cell]
        holding = Counter(row["value_holding"] for row in p_rows)
        posture_counts = Counter(row["collapsed_primary_label"] for row in p_rows)
        metadata = json.loads(
            (
                ROOT
                / "analysis/freeflow/personality-aggregates"
                / cell
                / "packet.metadata.json"
            ).read_text()
        )
        metrics.append(
            {
                "display": display,
                "model": model,
                "cell": cell,
                "freeflow_samples": len(ff_texts),
                "values_samples": len(val_texts),
                "mean_freeflow_words": sum(map(words, ff_texts)) / len(ff_texts),
                "mean_values_words": sum(map(words, val_texts)) / len(val_texts),
                "expressive_freeflow": metadata["sample_kind_counts"].get(
                    "EXPRESSIVE_FREEFLOW", 0
                ),
                "owned": holding["owned"],
                "relocated_or_partial": holding["relocated_or_partial"],
                "recited_not_owned": holding["recited_not_owned"],
                "top_postures": posture_counts.most_common(3),
                "top_topics": topics_by_cell[cell].most_common(8),
                "collection_cost": sum(
                    float((row.get("usage") or {}).get("cost") or 0)
                    for row in freeflow + values
                ),
            }
        )

    all_docs = []
    doc_cells = []
    for _, _, cell in CELLS:
        for doc in docs_by_cell[cell]:
            all_docs.append(doc)
            doc_cells.append(cell)
    matrix = TfidfVectorizer(
        lowercase=True, stop_words="english", min_df=2, max_features=30000
    ).fit_transform(all_docs)
    centroids = []
    for _, _, cell in CELLS:
        indices = [i for i, c in enumerate(doc_cells) if c == cell]
        centroids.append(matrix[indices].mean(axis=0))
    similarity = cosine_similarity(
        __import__("numpy").vstack([__import__("numpy").asarray(c) for c in centroids])
    )
    sim_rows = []
    for i, (display, _, cell) in enumerate(CELLS):
        others = sorted(
            (
                (float(similarity[i, j]), CELLS[j][0], CELLS[j][2])
                for j in range(len(CELLS))
                if i != j
            ),
            reverse=True,
        )
        sim_rows.append(
            {
                "display": display,
                "cell": cell,
                "nearest": others[0][1],
                "nearest_cell": others[0][2],
                "cosine": others[0][0],
            }
        )

    output = {"models": metrics, "nearest": sim_rows}
    (PHASE / "family_metrics.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    )

    lines = [
        "# Meta Muse family analysis",
        "",
        "_Six synchronous text-output routes; 750 freeflow + 720 values samples._",
        "",
        "## Quantitative overview",
        "",
        "| model | expressive freeflow | mean freeflow words | mean values words | owned values | relocated | recited/not owned | collection cost |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics:
        lines.append(
            f"| {row['display']} | {row['expressive_freeflow']}/125 | "
            f"{row['mean_freeflow_words']:.0f} | {row['mean_values_words']:.0f} | "
            f"{row['owned']}/120 ({pct(row['owned'], 120)}) | "
            f"{row['relocated_or_partial']} | {row['recited_not_owned']} | "
            f"${row['collection_cost']:.3f} |"
        )
    lines += [
        "",
        "## Freeflow nearest neighbours",
        "",
        "| model | nearest Muse model | TF-IDF centroid cosine |",
        "|---|---|---:|",
    ]
    for row in sim_rows:
        lines.append(f"| {row['display']} | {row['nearest']} | {row['cosine']:.3f} |")
    lines += ["", "## Top consensus values/wish topics", ""]
    for row in metrics:
        topics = ", ".join(f"`{key}` ({count})" for key, count in row["top_topics"])
        lines += [f"### {row['display']}", "", topics, ""]
    lines += [
        "## Interpretation",
        "",
        "_Narrative synthesis is added after the final consensus QA pass._",
        "",
    ]
    (PHASE / "MUSE_FAMILY_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({"models": len(metrics), "report": str(PHASE / "MUSE_FAMILY_REPORT.md")}))


if __name__ == "__main__":
    main()
