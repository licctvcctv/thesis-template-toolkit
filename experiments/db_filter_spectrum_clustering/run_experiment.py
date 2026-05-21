#!/usr/bin/env python3
"""Reproducible experiment for database-filtered mass spectrum clustering.

The script builds a small SQLite-backed synthetic top-down spectrum library,
compares several clustering strategies, and exports paper-ready metrics and
figures. It intentionally avoids external ML packages so the experiment can run
in a clean thesis workspace.
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import time
import tracemalloc
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = Path(__file__).resolve().parent
OUT_DIR = EXP_DIR / "outputs"
PAPER_DIR = ROOT / "papers" / "db_filter_spectrum_clustering"
PAPER_IMG_DIR = PAPER_DIR / "images" / "experiments"
PAPER_DATA_DIR = PAPER_DIR / "data"
DB_PATH = OUT_DIR / "spectrum_library.sqlite"


RNG = np.random.default_rng(20260519)
N_CLUSTERS = 10
SPECTRA_PER_CLUSTER = 44
N_SPECTRA = N_CLUSTERS * SPECTRA_PER_CLUSTER
TOP_PEAKS = 56
VECTOR_BINS = 260


@dataclass
class ExperimentData:
    spectra: list[dict]
    vectors: np.ndarray
    labels_true: np.ndarray


def ensure_dirs() -> None:
    for path in (OUT_DIR, PAPER_IMG_DIR, PAPER_DATA_DIR):
        path.mkdir(parents=True, exist_ok=True)


def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    return v / norm if norm else v


def mass_bin(mass: float) -> int:
    return int(mass // 20)


def vector_index(mass: float) -> int:
    return int(mass // 18) % VECTOR_BINS


def generate_spectra() -> ExperimentData:
    spectra: list[dict] = []
    vectors = np.zeros((N_SPECTRA, VECTOR_BINS), dtype=float)
    labels = np.zeros(N_SPECTRA, dtype=int)

    cluster_precursors = np.linspace(5200, 18200, N_CLUSTERS)
    cluster_charges = RNG.integers(4, 10, size=N_CLUSTERS)
    base_masses = []
    base_intensities = []
    for cluster_idx in range(N_CLUSTERS):
        masses = np.sort(RNG.uniform(220, 4800, size=TOP_PEAKS))
        intensities = RNG.gamma(3.0, 1.0, size=TOP_PEAKS)
        base_masses.append(masses)
        base_intensities.append(normalize(intensities))

    for cluster_idx in range(N_CLUSTERS):
        for local_idx in range(SPECTRA_PER_CLUSTER):
            spec_id = cluster_idx * SPECTRA_PER_CLUSTER + local_idx
            labels[spec_id] = cluster_idx
            precursor = float(cluster_precursors[cluster_idx] + RNG.normal(0, 8.0))
            charge = int(cluster_charges[cluster_idx] + RNG.choice([-1, 0, 0, 0, 1]))
            charge = max(2, charge)

            keep_mask = RNG.random(TOP_PEAKS) > 0.16
            masses = base_masses[cluster_idx][keep_mask] + RNG.normal(0, 1.8, keep_mask.sum())
            intensities = base_intensities[cluster_idx][keep_mask] * RNG.lognormal(0, 0.20, keep_mask.sum())
            noise_count = int(RNG.integers(5, 12))
            masses = np.concatenate([masses, RNG.uniform(180, 5000, size=noise_count)])
            intensities = np.concatenate([intensities, RNG.gamma(1.6, 0.35, size=noise_count)])
            order = np.argsort(intensities)[::-1][:TOP_PEAKS]
            masses = masses[order]
            intensities = normalize(intensities[order])

            vec = np.zeros(VECTOR_BINS, dtype=float)
            for mass, inten in zip(masses, intensities):
                vec[vector_index(float(mass))] += float(inten)
            vectors[spec_id] = normalize(vec)

            top_bins = [mass_bin(float(m)) for m in masses[:8]]
            spectra.append(
                {
                    "id": spec_id,
                    "cluster_id": cluster_idx,
                    "precursor_mass": precursor,
                    "charge": charge,
                    "peak_count": int(len(masses)),
                    "top_bins": top_bins,
                    "peaks": [(float(m), float(i)) for m, i in zip(masses, intensities)],
                }
            )
    return ExperimentData(spectra=spectra, vectors=vectors, labels_true=labels)


def build_sqlite(data: ExperimentData) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE spectrum (
            id INTEGER PRIMARY KEY,
            cluster_id INTEGER,
            precursor_mass REAL,
            charge INTEGER,
            peak_count INTEGER,
            top_bin_1 INTEGER,
            top_bin_2 INTEGER,
            top_bin_3 INTEGER,
            top_bin_4 INTEGER
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE peak (
            spectrum_id INTEGER,
            mass REAL,
            intensity REAL,
            FOREIGN KEY (spectrum_id) REFERENCES spectrum(id)
        )
        """
    )
    cur.execute("CREATE INDEX idx_spectrum_filter ON spectrum(charge, precursor_mass)")
    cur.execute("CREATE INDEX idx_peak_spectrum ON peak(spectrum_id)")

    for spec in data.spectra:
        bins = spec["top_bins"][:4]
        cur.execute(
            """
            INSERT INTO spectrum
            (id, cluster_id, precursor_mass, charge, peak_count, top_bin_1, top_bin_2, top_bin_3, top_bin_4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec["id"],
                spec["cluster_id"],
                spec["precursor_mass"],
                spec["charge"],
                spec["peak_count"],
                bins[0],
                bins[1],
                bins[2],
                bins[3],
            ),
        )
        cur.executemany(
            "INSERT INTO peak(spectrum_id, mass, intensity) VALUES (?, ?, ?)",
            [(spec["id"], mass, inten) for mass, inten in spec["peaks"]],
        )
    con.commit()
    con.close()


def cosine_matrix(vectors: np.ndarray) -> np.ndarray:
    sim = vectors @ vectors.T
    np.fill_diagonal(sim, 1.0)
    return np.clip(sim, 0.0, 1.0)


def kmeans(vectors: np.ndarray, k: int, iterations: int = 60) -> np.ndarray:
    rng = np.random.default_rng(42)
    centers = vectors[rng.choice(len(vectors), size=k, replace=False)].copy()
    labels = np.zeros(len(vectors), dtype=int)
    for _ in range(iterations):
        sims = vectors @ centers.T
        new_labels = sims.argmax(axis=1)
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        for idx in range(k):
            members = vectors[labels == idx]
            if len(members):
                centers[idx] = normalize(members.mean(axis=0))
    return labels


def spectral_clustering(sim: np.ndarray, k: int) -> np.ndarray:
    affinity = np.where(sim >= 0.22, sim, 0.0)
    degree = affinity.sum(axis=1)
    degree[degree == 0] = 1.0
    d_inv_sqrt = np.diag(1.0 / np.sqrt(degree))
    lap = np.eye(len(sim)) - d_inv_sqrt @ affinity @ d_inv_sqrt
    _, eigvecs = np.linalg.eigh(lap)
    embed = eigvecs[:, :k]
    row_norm = np.linalg.norm(embed, axis=1, keepdims=True)
    row_norm[row_norm == 0] = 1.0
    embed = embed / row_norm
    return kmeans(embed, k)


def agglomerative_average(sim: np.ndarray, k: int) -> np.ndarray:
    """Fast single-link agglomerative baseline.

    A full average-link implementation is unnecessarily slow for repeated thesis
    builds. This baseline still follows the hierarchical merge idea: pairs are
    processed from high to low similarity until the target cluster count is
    reached.
    """

    n = len(sim)
    parent = np.arange(n)
    components = n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        nonlocal components
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
            components -= 1

    tri_i, tri_j = np.triu_indices(n, k=1)
    order = np.argsort(sim[tri_i, tri_j])[::-1]
    for pos in order:
        union(int(tri_i[pos]), int(tri_j[pos]))
        if components <= k:
            break

    root_to_label: dict[int, int] = {}
    labels = np.zeros(n, dtype=int)
    for idx in range(n):
        root = find(idx)
        if root not in root_to_label:
            root_to_label[root] = len(root_to_label)
        labels[idx] = root_to_label[root]
    return labels


def dbscan_cosine(sim: np.ndarray, eps: float = 0.61, min_samples: int = 3) -> np.ndarray:
    n = len(sim)
    visited = np.zeros(n, dtype=bool)
    labels = np.full(n, -1, dtype=int)
    cluster_id = 0
    threshold = 1.0 - eps
    neighbors = [np.where(sim[i] >= threshold)[0].tolist() for i in range(n)]
    for point in range(n):
        if visited[point]:
            continue
        visited[point] = True
        if len(neighbors[point]) < min_samples:
            continue
        labels[point] = cluster_id
        seeds = list(neighbors[point])
        while seeds:
            candidate = seeds.pop()
            if not visited[candidate]:
                visited[candidate] = True
                if len(neighbors[candidate]) >= min_samples:
                    seeds.extend([x for x in neighbors[candidate] if x not in seeds])
            if labels[candidate] == -1:
                labels[candidate] = cluster_id
        cluster_id += 1
    # Metrics are easier to compare when unclustered spectra remain distinct.
    next_label = cluster_id
    for idx in np.where(labels == -1)[0]:
        labels[idx] = next_label
        next_label += 1
    return labels


def database_filtered_clustering(data: ExperimentData, threshold: float = 0.20, mass_window: float = 80.0) -> tuple[np.ndarray, dict]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    parent = np.arange(len(data.spectra))
    compared: set[tuple[int, int]] = set()

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for spec in data.spectra:
        bins = spec["top_bins"][:4]
        clauses = " OR ".join([f"top_bin_{i} IN ({','.join(['?'] * len(bins))})" for i in range(1, 5)])
        sql = f"""
            SELECT id FROM spectrum
            WHERE id > ?
              AND charge BETWEEN ? AND ?
              AND precursor_mass BETWEEN ? AND ?
              AND ({clauses})
        """
        params = [
            spec["id"],
            max(1, spec["charge"] - 1),
            spec["charge"] + 1,
            spec["precursor_mass"] - mass_window,
            spec["precursor_mass"] + mass_window,
        ]
        for _ in range(4):
            params.extend(bins)
        for (candidate_id,) in cur.execute(sql, params):
            a, b = spec["id"], int(candidate_id)
            if a > b:
                a, b = b, a
            compared.add((a, b))
            if float(data.vectors[a] @ data.vectors[b]) >= threshold:
                union(a, b)
    con.close()

    root_to_label: dict[int, int] = {}
    labels = np.zeros(len(data.spectra), dtype=int)
    for idx in range(len(data.spectra)):
        root = find(idx)
        if root not in root_to_label:
            root_to_label[root] = len(root_to_label)
        labels[idx] = root_to_label[root]
    stats = {
        "candidate_pairs": len(compared),
        "candidate_pairs_set": compared,
        "all_pairs": len(data.spectra) * (len(data.spectra) - 1) // 2,
        "reduction_rate": 1.0 - len(compared) / (len(data.spectra) * (len(data.spectra) - 1) / 2),
        "similarity_threshold": threshold,
        "mass_window": mass_window,
    }
    return labels, stats


def adjusted_rand_index(true: np.ndarray, pred: np.ndarray) -> float:
    contingency: dict[tuple[int, int], int] = Counter(zip(true.tolist(), pred.tolist()))
    true_counts = Counter(true.tolist())
    pred_counts = Counter(pred.tolist())

    def comb2(n: int) -> int:
        return n * (n - 1) // 2

    sum_comb = sum(comb2(v) for v in contingency.values())
    sum_true = sum(comb2(v) for v in true_counts.values())
    sum_pred = sum(comb2(v) for v in pred_counts.values())
    total = comb2(len(true))
    expected = sum_true * sum_pred / total if total else 0.0
    max_index = 0.5 * (sum_true + sum_pred)
    denom = max_index - expected
    return float((sum_comb - expected) / denom) if denom else 0.0


def normalized_mutual_info(true: np.ndarray, pred: np.ndarray) -> float:
    n = len(true)
    true_counts = Counter(true.tolist())
    pred_counts = Counter(pred.tolist())
    joint = Counter(zip(true.tolist(), pred.tolist()))

    mi = 0.0
    for (a, b), count in joint.items():
        mi += count / n * math.log((count * n) / (true_counts[a] * pred_counts[b]) + 1e-12)
    h_true = -sum((count / n) * math.log(count / n) for count in true_counts.values())
    h_pred = -sum((count / n) * math.log(count / n) for count in pred_counts.values())
    denom = math.sqrt(h_true * h_pred)
    return float(mi / denom) if denom else 0.0


def silhouette_cosine(sim: np.ndarray, labels: np.ndarray) -> float:
    unique = [label for label in sorted(set(labels.tolist())) if np.sum(labels == label) > 1]
    if len(unique) < 2:
        return 0.0
    dist = 1.0 - sim
    values = []
    for idx in range(len(labels)):
        same = np.where(labels == labels[idx])[0]
        same = same[same != idx]
        if len(same) == 0:
            continue
        a = float(dist[idx, same].mean())
        b = min(float(dist[idx, np.where(labels == other)[0]].mean()) for other in unique if other != labels[idx])
        denom = max(a, b)
        if denom:
            values.append((b - a) / denom)
    return float(np.mean(values)) if values else 0.0


def evaluate(name: str, labels: np.ndarray, true: np.ndarray, sim: np.ndarray, elapsed: float, peak_mb: float, extra: dict | None = None) -> dict:
    clusters = Counter(labels.tolist())
    valid = sum(1 for size in clusters.values() if size >= 2)
    result = {
        "algorithm": name,
        "clusters": len(clusters),
        "valid_clusters": valid,
        "ari": round(adjusted_rand_index(true, labels), 4),
        "nmi": round(normalized_mutual_info(true, labels), 4),
        "silhouette": round(silhouette_cosine(sim, labels), 4),
        "runtime_sec": round(elapsed, 4),
        "peak_memory_mb": round(peak_mb, 3),
    }
    if extra:
        result.update(extra)
    return result


def run_measured(func, *args):
    tracemalloc.start()
    start = time.perf_counter()
    output = func(*args)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return output, elapsed, peak / (1024 * 1024)


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_bar_chart(path: Path, title: str, labels: list[str], series: list[tuple[str, list[float], tuple[int, int, int]]], y_max: float) -> None:
    width, height = 1300, 760
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font_title = load_font(34, True)
    font = load_font(22)
    small = load_font(18)
    left, right, top, bottom = 110, 70, 90, 120
    chart_w = width - left - right
    chart_h = height - top - bottom
    draw.text((left, 28), title, fill=(20, 32, 44), font=font_title)
    draw.line((left, top, left, top + chart_h), fill=(40, 40, 40), width=2)
    draw.line((left, top + chart_h, left + chart_w, top + chart_h), fill=(40, 40, 40), width=2)
    for tick in range(6):
        y = top + chart_h - chart_h * tick / 5
        val = y_max * tick / 5
        draw.line((left - 6, y, left + chart_w, y), fill=(226, 232, 238), width=1)
        draw.text((25, y - 11), f"{val:.2f}", fill=(60, 70, 80), font=small)
    group_w = chart_w / len(labels)
    bar_w = min(46, group_w / (len(series) + 1))
    for i, label in enumerate(labels):
        x0 = left + i * group_w + group_w * 0.18
        for j, (series_name, values, color) in enumerate(series):
            value = values[i]
            bar_h = chart_h * value / y_max
            x = x0 + j * (bar_w + 7)
            y = top + chart_h - bar_h
            draw.rounded_rectangle((x, y, x + bar_w, top + chart_h), radius=4, fill=color)
            draw.text((x - 6, y - 25), f"{value:.2f}", fill=color, font=small)
        draw.text((left + i * group_w + 5, top + chart_h + 18), label, fill=(30, 40, 50), font=small)
    legend_x = left
    for name, _, color in series:
        draw.rectangle((legend_x, height - 58, legend_x + 26, height - 32), fill=color)
        draw.text((legend_x + 34, height - 60), name, fill=(30, 40, 50), font=font)
        legend_x += 150
    img.save(path)


def draw_runtime_chart(path: Path, results: list[dict]) -> None:
    labels = [r["algorithm"] for r in results]
    runtimes = [r["runtime_sec"] for r in results]
    pairs = [r.get("candidate_pairs", r.get("all_pairs", 0)) for r in results]
    max_runtime = max(runtimes) * 1.18
    draw_bar_chart(path, "聚类算法运行时间对比", labels, [("运行时间/s", runtimes, (68, 114, 196))], max_runtime)

    pair_path = path.with_name("candidate_reduction.png")
    max_pairs = max(pairs) * 1.18
    draw_bar_chart(pair_path, "数据库过滤前后的候选谱图对数量", labels, [("候选对数量", pairs, (66, 151, 115))], max_pairs)


def draw_scatter(path: Path, vectors: np.ndarray, true: np.ndarray, pred: np.ndarray) -> None:
    centered = vectors - vectors.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :2] * s[:2]
    x = coords[:, 0]
    y = coords[:, 1]
    x = (x - x.min()) / (x.max() - x.min() + 1e-12)
    y = (y - y.min()) / (y.max() - y.min() + 1e-12)
    width, height = 1200, 760
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font_title = load_font(34, True)
    font = load_font(20)
    palette = [
        (54, 96, 146),
        (202, 93, 61),
        (68, 151, 115),
        (134, 103, 179),
        (196, 150, 66),
        (83, 144, 176),
        (180, 82, 116),
        (112, 132, 58),
        (72, 72, 72),
        (48, 132, 132),
    ]
    draw.text((70, 30), "数据库过滤聚类结果二维投影", fill=(20, 32, 44), font=font_title)
    draw.rectangle((80, 100, width - 70, height - 95), outline=(44, 54, 66), width=2)
    for idx in range(len(vectors)):
        px = 90 + x[idx] * (width - 180)
        py = 110 + (1 - y[idx]) * (height - 220)
        color = palette[int(true[idx]) % len(palette)]
        radius = 5 if pred[idx] == true[idx] else 7
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=color, outline=(255, 255, 255))
    draw.text((80, height - 70), "颜色表示真实谱图组；点云分离度用于辅助观察聚类结构", fill=(65, 75, 88), font=font)
    img.save(path)


def draw_memory_chart(path: Path, results: list[dict]) -> None:
    draw_bar_chart(
        path,
        "聚类算法峰值内存占用对比",
        [r["algorithm"] for r in results],
        [("峰值内存/MB", [r["peak_memory_mb"] for r in results], (134, 103, 179))],
        max(r["peak_memory_mb"] for r in results) * 1.18,
    )


def draw_sensitivity_chart(path: Path, sensitivity: list[dict]) -> None:
    labels = [item["setting"] for item in sensitivity]
    draw_bar_chart(
        path,
        "候选过滤参数敏感性分析",
        labels,
        [
            ("ARI", [item["ari"] for item in sensitivity], (54, 96, 146)),
            ("NMI", [item["nmi"] for item in sensitivity], (68, 151, 115)),
        ],
        1.05,
    )


def draw_cluster_size_chart(path: Path, true: np.ndarray, pred: np.ndarray) -> None:
    true_sizes = sorted(Counter(true.tolist()).values(), reverse=True)
    pred_sizes = sorted(Counter(pred.tolist()).values(), reverse=True)[:18]
    labels = [f"C{i + 1}" for i in range(max(len(true_sizes), len(pred_sizes)))]
    true_values = true_sizes + [0] * (len(labels) - len(true_sizes))
    pred_values = pred_sizes + [0] * (len(labels) - len(pred_sizes))
    draw_bar_chart(
        path,
        "真实簇与数据库过滤聚类簇规模分布",
        labels,
        [
            ("真实簇规模", true_values, (54, 96, 146)),
            ("预测簇规模", pred_values, (202, 93, 61)),
        ],
        max(max(true_values), max(pred_values)) * 1.18,
    )


def draw_similarity_histogram(path: Path, sim: np.ndarray, candidate_pairs: set[tuple[int, int]]) -> None:
    rng = np.random.default_rng(20260520)
    all_i, all_j = np.triu_indices(len(sim), k=1)
    sample_idx = rng.choice(len(all_i), size=min(5000, len(all_i)), replace=False)
    background = sim[all_i[sample_idx], all_j[sample_idx]]
    candidate_values = np.array([sim[a, b] for a, b in candidate_pairs], dtype=float)
    bins = np.linspace(0, 1, 21)
    bg_hist, _ = np.histogram(background, bins=bins)
    cand_hist, _ = np.histogram(candidate_values, bins=bins)
    bg_hist = bg_hist / max(1, bg_hist.max())
    cand_hist = cand_hist / max(1, cand_hist.max())
    labels = [f"{bins[i]:.2f}" for i in range(len(bins) - 1)]
    draw_bar_chart(
        path,
        "候选谱图对与随机谱图对相似度分布",
        labels,
        [
            ("随机谱图对", bg_hist.tolist(), (150, 158, 170)),
            ("过滤候选对", cand_hist.tolist(), (66, 151, 115)),
        ],
        1.05,
    )


def run_filter_sensitivity(data: ExperimentData, sim: np.ndarray) -> list[dict]:
    settings = [
        ("质量窗口过窄", 10.0, 0.20),
        ("质量窗口适中", 20.0, 0.20),
        ("基准设置", 80.0, 0.20),
        ("相似度阈值降低", 80.0, 0.15),
        ("相似度阈值提高", 80.0, 0.25),
    ]
    rows = []
    for name, mass_window, threshold in settings:
        labels, stats = database_filtered_clustering(data, threshold=threshold, mass_window=mass_window)
        serializable_stats = {k: v for k, v in stats.items() if k != "candidate_pairs_set"}
        item = evaluate(name, labels, data.labels_true, sim, 0.0, 0.0, serializable_stats)
        item["setting"] = name
        rows.append(item)
    return rows


def export_tables(results: list[dict], data: ExperimentData, filter_stats: dict, sensitivity: list[dict]) -> None:
    metrics = {
        "dataset": {
            "spectrum_count": len(data.spectra),
            "true_cluster_count": N_CLUSTERS,
            "spectra_per_cluster": SPECTRA_PER_CLUSTER,
            "peaks_per_spectrum": TOP_PEAKS,
            "vector_bins": VECTOR_BINS,
            "sqlite_path": str(DB_PATH.relative_to(ROOT)),
        },
        "filter": filter_stats,
        "results": results,
    }
    for path in (OUT_DIR / "metrics.json", PAPER_DATA_DIR / "experiment_metrics.json"):
        path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["算法,聚类数,ARI,NMI,轮廓系数,运行时间(s),峰值内存(MB),候选对数量"]
    for r in results:
        lines.append(
            ",".join(
                [
                    r["algorithm"],
                    str(r["clusters"]),
                    str(r["ari"]),
                    str(r["nmi"]),
                    str(r["silhouette"]),
                    str(r["runtime_sec"]),
                    str(r["peak_memory_mb"]),
                    str(r.get("candidate_pairs", r.get("all_pairs", ""))),
                ]
            )
        )
    (OUT_DIR / "algorithm_comparison.csv").write_text("\n".join(lines), encoding="utf-8")

    for path in (OUT_DIR / "filter_sensitivity.json", PAPER_DATA_DIR / "filter_sensitivity.json"):
        path.write_text(json.dumps(sensitivity, ensure_ascii=False, indent=2), encoding="utf-8")
    sens_lines = ["设置,质量窗口/Da,阈值,候选对,过滤率,ARI,NMI,轮廓系数,聚类数"]
    for item in sensitivity:
        sens_lines.append(
            ",".join(
                [
                    item["setting"],
                    f"{item['mass_window']:.0f}",
                    f"{item['similarity_threshold']:.2f}",
                    str(item["candidate_pairs"]),
                    f"{item['reduction_rate']:.4f}",
                    f"{item['ari']:.4f}",
                    f"{item['nmi']:.4f}",
                    f"{item['silhouette']:.4f}",
                    str(item["clusters"]),
                ]
            )
        )
    for path in (OUT_DIR / "filter_sensitivity.csv", PAPER_DATA_DIR / "filter_sensitivity.csv"):
        path.write_text("\n".join(sens_lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    data = generate_spectra()
    build_sqlite(data)
    sim, sim_elapsed, sim_mem = run_measured(cosine_matrix, data.vectors)

    results = []
    all_pairs = len(data.spectra) * (len(data.spectra) - 1) // 2

    labels, elapsed, peak = run_measured(kmeans, data.vectors, N_CLUSTERS)
    results.append(evaluate("K-Means", labels, data.labels_true, sim, elapsed, peak, {"candidate_pairs": all_pairs, "all_pairs": all_pairs}))

    labels, elapsed, peak = run_measured(spectral_clustering, sim, N_CLUSTERS)
    results.append(evaluate("谱聚类", labels, data.labels_true, sim, elapsed + sim_elapsed, peak + sim_mem, {"candidate_pairs": all_pairs, "all_pairs": all_pairs}))

    labels, elapsed, peak = run_measured(agglomerative_average, sim, N_CLUSTERS)
    results.append(evaluate("层次聚类", labels, data.labels_true, sim, elapsed + sim_elapsed, peak + sim_mem, {"candidate_pairs": all_pairs, "all_pairs": all_pairs}))

    labels, elapsed, peak = run_measured(dbscan_cosine, sim)
    results.append(evaluate("DBSCAN", labels, data.labels_true, sim, elapsed + sim_elapsed, peak + sim_mem, {"candidate_pairs": all_pairs, "all_pairs": all_pairs}))

    output, elapsed, peak = run_measured(database_filtered_clustering, data)
    labels, filter_stats = output
    serializable_filter_stats = {k: v for k, v in filter_stats.items() if k != "candidate_pairs_set"}
    proposed = evaluate("数据库过滤聚类", labels, data.labels_true, sim, elapsed, peak, serializable_filter_stats)
    results.append(proposed)

    result_order = ["K-Means", "谱聚类", "层次聚类", "DBSCAN", "数据库过滤聚类"]
    results = sorted(results, key=lambda r: result_order.index(r["algorithm"]))

    draw_bar_chart(
        PAPER_IMG_DIR / "algorithm_metrics.png",
        "聚类质量指标对比",
        [r["algorithm"] for r in results],
        [
            ("ARI", [r["ari"] for r in results], (54, 96, 146)),
            ("NMI", [r["nmi"] for r in results], (68, 151, 115)),
            ("轮廓系数", [r["silhouette"] for r in results], (202, 93, 61)),
        ],
        1.05,
    )
    draw_runtime_chart(PAPER_IMG_DIR / "runtime_comparison.png", results)
    draw_scatter(PAPER_IMG_DIR / "cluster_projection.png", data.vectors, data.labels_true, labels)
    draw_memory_chart(PAPER_IMG_DIR / "memory_comparison.png", results)
    sensitivity = run_filter_sensitivity(data, sim)
    draw_sensitivity_chart(PAPER_IMG_DIR / "filter_sensitivity.png", sensitivity)
    draw_cluster_size_chart(PAPER_IMG_DIR / "cluster_size_distribution.png", data.labels_true, labels)
    draw_similarity_histogram(PAPER_IMG_DIR / "similarity_histogram.png", sim, filter_stats["candidate_pairs_set"])

    for image_name in [
        "algorithm_metrics.png",
        "runtime_comparison.png",
        "candidate_reduction.png",
        "cluster_projection.png",
        "memory_comparison.png",
        "filter_sensitivity.png",
        "cluster_size_distribution.png",
        "similarity_histogram.png",
    ]:
        src = PAPER_IMG_DIR / image_name
        dst = OUT_DIR / image_name
        if src.exists():
            dst.write_bytes(src.read_bytes())

    export_tables(results, data, serializable_filter_stats, sensitivity)
    print(json.dumps({"results": results, "filter": serializable_filter_stats, "sensitivity": sensitivity}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
