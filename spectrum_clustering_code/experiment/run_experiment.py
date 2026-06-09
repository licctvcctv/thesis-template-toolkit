#!/usr/bin/env python3
"""Run a real-data experiment for database-filtered spectrum clustering.

The input is the PRIDE data set PXD019368, one of the public data sets listed
in the TopLib paper data-availability statement.  The downloaded files already
contain msalign spectra and TopPIC search output tables, so this script can run
on macOS without reprocessing RAW files through TopFD.
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import sqlite3
import sys
import time
import tracemalloc
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:
    bundled_python = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "bin" / "python3"
    if bundled_python.exists() and Path(sys.executable) != bundled_python:
        os.execv(str(bundled_python), [str(bundled_python), *sys.argv])
    raise


ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "_source_materials" / "pride" / "PXD019368"
PXD029703_DIR = ROOT / "_source_materials" / "pride" / "PXD029703"
OUT_DIR = EXP_DIR / "outputs"
PAPER_DIR = ROOT / "papers" / "db_filter_spectrum_clustering"
PAPER_IMG_DIR = PAPER_DIR / "images" / "experiments"
PAPER_DATA_DIR = PAPER_DIR / "data"
DB_PATH = OUT_DIR / "toplib_real_spectra.sqlite"


TOP_PEAKS = 50
PRECURSOR_WINDOW_DA = 2.2
FRAGMENT_TOLERANCE_PPM = 10.0
BASELINE_THRESHOLD = 0.30


@dataclass
class Spectrum:
    row_id: int
    source_file: str
    spectrum_id: int
    scan: str
    precursor_mass: float
    precursor_charge: int
    label: str
    protein: str
    peaks: list[tuple[float, float, int]]


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra

    def labels(self) -> list[int]:
        root_to_label: dict[int, int] = {}
        out = []
        for idx in range(len(self.parent)):
            root = self.find(idx)
            if root not in root_to_label:
                root_to_label[root] = len(root_to_label)
            out.append(root_to_label[root])
        return out


def ensure_dirs() -> None:
    for path in (OUT_DIR, PAPER_IMG_DIR, PAPER_DATA_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_text(draw: ImageDraw.ImageDraw, pos, text: str, size=22, fill=(30, 40, 50), bold=False):
    draw.text(pos, text, font=load_font(size, bold=bold), fill=fill)


def text_size(draw: ImageDraw.ImageDraw, text: str, size=22):
    box = draw.textbbox((0, 0), text, font=load_font(size))
    return box[2] - box[0], box[3] - box[1]


def save_chart(title: str, painter, path: Path, width=1400, height=850) -> None:
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width - 1, height - 1], outline=(220, 226, 232), width=2)
    draw_text(draw, (56, 38), title, size=34, fill=(23, 43, 77), bold=True)
    painter(draw, width, height)
    img.save(path)


def parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value in {"", "-"}:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def parse_int(value: str | None, default: int = 0) -> int:
    try:
        return int(float(value or default))
    except ValueError:
        return default


def label_from_row(row: dict[str, str]) -> tuple[str, str]:
    protein = (row.get("Protein name") or "UNKNOWN").split()[0]
    first = row.get("First residue") or "0"
    last = row.get("Last residue") or "0"
    charge = row.get("Charge") or "0"
    adjusted_mass = parse_float(row.get("Adjusted precursor mass"), parse_float(row.get("Precursor mass")))
    mass_bin = round(adjusted_mass / PRECURSOR_WINDOW_DA)
    label = f"{protein}|{first}|{last}|{mass_bin}|z{charge}"
    return protein, label


def read_identifications() -> dict[tuple[str, int], tuple[str, str]]:
    labels: dict[tuple[str, int], tuple[str, str]] = {}
    for table_path in sorted(SOURCE_DIR.glob("*.OUTPUT_TABLE")):
        lines = table_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        header_idx = next((i for i, line in enumerate(lines) if line.startswith("Data file name\tPrsm ID")), None)
        if header_idx is None:
            continue
        reader = csv.DictReader(lines[header_idx:], delimiter="\t")
        for row in reader:
            spectrum_id = parse_int(row.get("Spectrum ID"), -1)
            if spectrum_id < 0:
                continue
            protein, label = label_from_row(row)
            labels[(table_path.stem, spectrum_id)] = (protein, label)
    return labels


def normalize_top_peaks(peaks: list[tuple[float, float, int]]) -> list[tuple[float, float, int]]:
    selected = sorted(peaks, key=lambda x: x[1], reverse=True)[:TOP_PEAKS]
    converted = [(mass, math.log2(max(intensity, 1e-6)), charge) for mass, intensity, charge in selected]
    norm = math.sqrt(sum(intensity * intensity for _, intensity, _ in converted)) or 1.0
    return sorted([(mass, intensity / norm, charge) for mass, intensity, charge in converted], key=lambda x: x[0])


def read_spectra(labels: dict[tuple[str, int], tuple[str, str]]) -> list[Spectrum]:
    spectra: list[Spectrum] = []
    for msalign_path in sorted(SOURCE_DIR.glob("*.msalign")):
        current: dict | None = None
        with msalign_path.open(encoding="utf-8", errors="ignore") as fh:
            for raw in fh:
                line = raw.strip()
                if line == "BEGIN IONS":
                    current = {"source_file": msalign_path.stem, "peaks": []}
                    continue
                if line == "END IONS":
                    if not current:
                        continue
                    key = (current["source_file"], current.get("spectrum_id"))
                    if key in labels and current.get("precursor_mass") and current.get("precursor_charge"):
                        peaks = normalize_top_peaks(current["peaks"])
                        if len(peaks) > 1:
                            protein, label = labels[key]
                            spectra.append(
                                Spectrum(
                                    row_id=len(spectra),
                                    source_file=current["source_file"],
                                    spectrum_id=int(current["spectrum_id"]),
                                    scan=str(current.get("scan", "")),
                                    precursor_mass=float(current["precursor_mass"]),
                                    precursor_charge=int(current["precursor_charge"]),
                                    label=label,
                                    protein=protein,
                                    peaks=peaks,
                                )
                            )
                    current = None
                    continue
                if current is None:
                    continue
                if line.startswith("ID="):
                    current["spectrum_id"] = parse_int(line.split("=", 1)[1])
                elif line.startswith("SCANS="):
                    current["scan"] = line.split("=", 1)[1]
                elif line.startswith("PRECURSOR_MASS="):
                    current["precursor_mass"] = parse_float(line.split("=", 1)[1])
                elif line.startswith("PRECURSOR_CHARGE="):
                    current["precursor_charge"] = parse_int(line.split("=", 1)[1])
                elif line and "=" not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            current["peaks"].append((float(parts[0]), float(parts[1]), int(float(parts[2]))))
                        except ValueError:
                            pass
    return spectra


def build_database(spectra: list[Spectrum]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE spectrum (
            row_id INTEGER PRIMARY KEY,
            source_file TEXT,
            spectrum_id INTEGER,
            scan TEXT,
            precursor_mass REAL,
            precursor_charge INTEGER,
            protein TEXT,
            ground_truth_label TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE peak (
            row_id INTEGER,
            rank INTEGER,
            mass REAL,
            norm_intensity REAL,
            charge INTEGER,
            FOREIGN KEY(row_id) REFERENCES spectrum(row_id)
        )
        """
    )
    cur.execute("CREATE INDEX idx_spectrum_precursor ON spectrum(precursor_charge, precursor_mass)")
    cur.execute("CREATE INDEX idx_peak_row ON peak(row_id)")
    for spec in spectra:
        cur.execute(
            """
            INSERT INTO spectrum
            (row_id, source_file, spectrum_id, scan, precursor_mass, precursor_charge, protein, ground_truth_label)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                spec.row_id,
                spec.source_file,
                spec.spectrum_id,
                spec.scan,
                spec.precursor_mass,
                spec.precursor_charge,
                spec.protein,
                spec.label,
            ),
        )
        cur.executemany(
            "INSERT INTO peak(row_id, rank, mass, norm_intensity, charge) VALUES (?, ?, ?, ?, ?)",
            [(spec.row_id, rank, mass, inten, charge) for rank, (mass, inten, charge) in enumerate(spec.peaks, start=1)],
        )
    con.commit()
    con.close()


def precursor_candidates(spectra: list[Spectrum], mass_window_da: float = PRECURSOR_WINDOW_DA) -> list[tuple[int, int]]:
    by_charge: dict[int, list[int]] = defaultdict(list)
    for idx, spec in enumerate(spectra):
        by_charge[spec.precursor_charge].append(idx)
    for values in by_charge.values():
        values.sort(key=lambda idx: spectra[idx].precursor_mass)

    pairs: list[tuple[int, int]] = []
    for values in by_charge.values():
        for pos, left in enumerate(values):
            mass = spectra[left].precursor_mass
            scan = pos + 1
            while scan < len(values) and spectra[values[scan]].precursor_mass - mass <= mass_window_da:
                pairs.append((left, values[scan]))
                scan += 1
    return pairs


def fragment_cosine(left: Spectrum, right: Spectrum, ppm: float = FRAGMENT_TOLERANCE_PPM) -> float:
    a, b = left.peaks, right.peaks
    i = j = 0
    score = 0.0
    while i < len(a) and j < len(b):
        mass_a, intensity_a, charge_a = a[i]
        mass_b, intensity_b, charge_b = b[j]
        tolerance = max(mass_a, mass_b) * ppm * 1e-6
        delta = mass_a - mass_b
        if abs(delta) <= tolerance:
            if charge_a == charge_b:
                score += intensity_a * intensity_b
            i += 1
            j += 1
        elif delta < 0:
            i += 1
        else:
            j += 1
    return score


def cluster_by_edges(n: int, edges: list[tuple[int, int]]) -> list[int]:
    uf = UnionFind(n)
    for left, right in edges:
        uf.union(left, right)
    return uf.labels()


def comb2(value: int) -> int:
    return value * (value - 1) // 2


def adjusted_rand_index(true_labels: list[str], predicted: list[int]) -> float:
    n = len(true_labels)
    contingency = Counter(zip(true_labels, predicted))
    true_count = Counter(true_labels)
    pred_count = Counter(predicted)
    sum_contingency = sum(comb2(v) for v in contingency.values())
    sum_true = sum(comb2(v) for v in true_count.values())
    sum_pred = sum(comb2(v) for v in pred_count.values())
    total = comb2(n)
    if total == 0:
        return 0.0
    expected = sum_true * sum_pred / total
    maximum = (sum_true + sum_pred) / 2
    return (sum_contingency - expected) / (maximum - expected) if maximum != expected else 0.0


def normalized_mutual_information(true_labels: list[str], predicted: list[int]) -> float:
    n = len(true_labels)
    true_count = Counter(true_labels)
    pred_count = Counter(predicted)
    joint = Counter(zip(true_labels, predicted))
    mutual_info = 0.0
    for (true_label, pred_label), count in joint.items():
        mutual_info += (count / n) * math.log((count * n) / (true_count[true_label] * pred_count[pred_label]) + 1e-15)
    true_entropy = -sum((count / n) * math.log(count / n) for count in true_count.values())
    pred_entropy = -sum((count / n) * math.log(count / n) for count in pred_count.values())
    return mutual_info / math.sqrt(true_entropy * pred_entropy) if true_entropy and pred_entropy else 0.0


def cluster_error_rate(true_labels: list[str], predicted: list[int]) -> float:
    clusters: dict[int, list[str]] = defaultdict(list)
    for label, cluster in zip(true_labels, predicted):
        clusters[cluster].append(label)
    wrong = 0
    clustered = 0
    for labels in clusters.values():
        if len(labels) <= 1:
            continue
        clustered += len(labels)
        majority = Counter(labels).most_common(1)[0][1]
        wrong += len(labels) - majority
    return wrong / clustered if clustered else 0.0


def clustered_ratio(predicted: list[int]) -> float:
    counts = Counter(predicted)
    clustered = sum(count for count in counts.values() if count > 1)
    return clustered / len(predicted) if predicted else 0.0


def evaluate(name: str, true_labels: list[str], predicted: list[int], elapsed: float, peak_mb: float, candidate_pairs: int, edges: int):
    return {
        "algorithm": name,
        "clusters": len(set(predicted)),
        "ari": adjusted_rand_index(true_labels, predicted),
        "nmi": normalized_mutual_information(true_labels, predicted),
        "incorrect_rate": cluster_error_rate(true_labels, predicted),
        "clustered_ratio": clustered_ratio(predicted),
        "runtime_sec": elapsed,
        "peak_memory_mb": peak_mb,
        "candidate_pairs": candidate_pairs,
        "retained_edges": edges,
    }


def measure(func):
    tracemalloc.start()
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / 1024 / 1024


def run_methods(spectra: list[Spectrum], candidates: list[tuple[int, int]], pair_scores: list[tuple[int, int, float]]):
    true_labels = [spec.label for spec in spectra]
    n = len(spectra)
    all_pairs = comb2(n)
    results = []

    labels, elapsed, peak = measure(lambda: list(range(n)))
    results.append(evaluate("全部单谱图基线", true_labels, labels, elapsed, peak, 0, 0))

    labels, elapsed, peak = measure(lambda: cluster_by_edges(n, candidates))
    results.append(evaluate("前体质量-荷电过滤", true_labels, labels, elapsed, peak, len(candidates), len(candidates)))

    for threshold in [0.30, 0.50, 0.70]:
        def make_labels(th=threshold):
            edges = [(i, j) for i, j, score in pair_scores if score >= th]
            return cluster_by_edges(n, edges), len(edges)

        (labels, edge_count), elapsed, peak = measure(make_labels)
        results.append(
            evaluate(
                f"数据库过滤+碎片峰相似度≥{threshold:.2f}",
                true_labels,
                labels,
                elapsed,
                peak,
                len(candidates),
                edge_count,
            )
        )
    return results, all_pairs


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def draw_grouped_bars(path: Path, results: list[dict]) -> None:
    names = [item["algorithm"] for item in results]
    ari = [item["ari"] for item in results]
    nmi = [item["nmi"] for item in results]

    def painter(draw, width, height):
        left, bottom, top = 120, height - 170, 150
        axis_h = bottom - top
        draw.line([left, top, left, bottom, width - 80, bottom], fill=(80, 95, 115), width=2)
        for tick in range(0, 6):
            y = bottom - axis_h * tick / 5
            draw.line([left - 8, y, width - 80, y], fill=(235, 239, 244), width=1)
            draw_text(draw, (48, int(y - 13)), f"{tick / 5:.1f}", size=20, fill=(90, 100, 115))
        group_w = (width - left - 120) / len(names)
        colors = [(53, 120, 198), (231, 145, 55)]
        for idx, name in enumerate(names):
            gx = left + idx * group_w + 18
            for offset, value in enumerate([ari[idx], nmi[idx]]):
                bar_w = group_w * 0.28
                x0 = gx + offset * (bar_w + 8)
                y0 = bottom - value * axis_h
                draw.rounded_rectangle([x0, y0, x0 + bar_w, bottom], radius=8, fill=colors[offset])
                draw_text(draw, (int(x0), int(y0 - 28)), f"{value:.3f}", size=17, fill=colors[offset])
            label = name.replace("数据库过滤+", "过滤+\n").replace("前体质量-", "前体\n")
            draw_text(draw, (int(gx - 6), bottom + 18), label, size=17, fill=(40, 50, 65))
        draw.rectangle([width - 300, 90, width - 270, 116], fill=colors[0])
        draw_text(draw, (width - 260, 86), "ARI", size=20)
        draw.rectangle([width - 190, 90, width - 160, 116], fill=colors[1])
        draw_text(draw, (width - 150, 86), "NMI", size=20)

    save_chart("谱图聚类质量对比", painter, path)


def draw_candidate_reduction(path: Path, all_pairs: int, candidates: int, edges: int) -> None:
    labels = ["全部谱图对", "前体候选对", "相似度保留边"]
    values = [all_pairs, candidates, edges]
    max_log = math.log10(max(values) + 1)

    def painter(draw, width, height):
        left, top, bottom = 180, 170, height - 145
        draw.line([left, top, left, bottom, width - 110, bottom], fill=(80, 95, 115), width=2)
        bar_h = 94
        colors = [(151, 166, 183), (58, 127, 204), (39, 159, 125)]
        for idx, (label, value) in enumerate(zip(labels, values)):
            y = top + idx * 155
            bar_w = (width - left - 210) * math.log10(value + 1) / max_log
            draw_text(draw, (42, y + 26), label, size=24)
            draw.rounded_rectangle([left, y, left + bar_w, y + bar_h], radius=12, fill=colors[idx])
            draw_text(draw, (int(left + bar_w + 20), y + 29), f"{value:,}", size=26, fill=(30, 40, 50), bold=True)
        reduction = 1 - candidates / all_pairs
        draw_text(draw, (left, height - 88), f"候选过滤率：{reduction * 100:.2f}%", size=28, fill=(28, 112, 84), bold=True)

    save_chart("数据库过滤前后的候选空间压缩", painter, path)


def draw_runtime(path: Path, results: list[dict]) -> None:
    labels = [item["algorithm"] for item in results[1:]]
    times = [item["runtime_sec"] for item in results[1:]]
    pairs = [max(item["retained_edges"], 1) for item in results[1:]]
    max_time = max(times) if times else 1
    max_pair = max(pairs) if pairs else 1

    def painter(draw, width, height):
        left, bottom, top = 110, height - 160, 145
        group_w = (width - left - 100) / len(labels)
        draw.line([left, top, left, bottom, width - 80, bottom], fill=(80, 95, 115), width=2)
        for idx, label in enumerate(labels):
            gx = left + idx * group_w + 40
            time_h = (bottom - top) * times[idx] / max_time if max_time else 0
            pair_h = (bottom - top) * math.log10(pairs[idx] + 1) / math.log10(max_pair + 1)
            draw.rounded_rectangle([gx, bottom - time_h, gx + 56, bottom], radius=8, fill=(62, 130, 204))
            draw.rounded_rectangle([gx + 76, bottom - pair_h, gx + 132, bottom], radius=8, fill=(231, 145, 55))
            draw_text(draw, (int(gx - 8), int(bottom - time_h - 30)), f"{times[idx]:.4f}s", size=17, fill=(62, 130, 204))
            draw_text(draw, (int(gx + 62), int(bottom - pair_h - 30)), f"{pairs[idx]:,}", size=17, fill=(180, 95, 32))
            draw_text(draw, (int(gx - 25), bottom + 18), label.replace("数据库过滤+", "过滤+\n").replace("前体质量-", "前体\n"), size=17)
        draw.rectangle([width - 360, 92, width - 332, 118], fill=(62, 130, 204))
        draw_text(draw, (width - 322, 88), "运行时间", size=20)
        draw.rectangle([width - 210, 92, width - 182, 118], fill=(231, 145, 55))
        draw_text(draw, (width - 172, 88), "保留边数", size=20)

    save_chart("运行时间与保留边数量", painter, path)


def draw_sensitivity(path: Path, rows: list[dict]) -> None:
    thresholds = [row["threshold"] for row in rows]
    ari = [row["ari"] for row in rows]
    edges = [row["retained_edges"] for row in rows]
    max_edges = max(edges) if edges else 1

    def painter(draw, width, height):
        left, bottom, top = 115, height - 155, 145
        draw.line([left, top, left, bottom, width - 95, bottom], fill=(80, 95, 115), width=2)
        plot_w = width - left - 170
        prev_ari = None
        prev_edge = None
        for idx, th in enumerate(thresholds):
            x = left + plot_w * idx / (len(thresholds) - 1)
            y_ari = bottom - (bottom - top) * ari[idx]
            y_edge = bottom - (bottom - top) * (edges[idx] / max_edges)
            if prev_ari:
                draw.line([prev_ari[0], prev_ari[1], x, y_ari], fill=(53, 120, 198), width=4)
                draw.line([prev_edge[0], prev_edge[1], x, y_edge], fill=(231, 145, 55), width=4)
            draw.ellipse([x - 7, y_ari - 7, x + 7, y_ari + 7], fill=(53, 120, 198))
            draw.ellipse([x - 7, y_edge - 7, x + 7, y_edge + 7], fill=(231, 145, 55))
            draw_text(draw, (int(x - 24), bottom + 18), f"{th:.2f}", size=20)
            prev_ari = (x, y_ari)
            prev_edge = (x, y_edge)
        draw_text(draw, (left, height - 82), "横轴：碎片峰相似度阈值", size=22)
        draw.rectangle([width - 360, 92, width - 332, 118], fill=(53, 120, 198))
        draw_text(draw, (width - 322, 88), "ARI", size=20)
        draw.rectangle([width - 250, 92, width - 222, 118], fill=(231, 145, 55))
        draw_text(draw, (width - 212, 88), "保留边归一化", size=20)

    save_chart("碎片峰相似度阈值敏感性分析", painter, path)


def draw_histogram(path: Path, pair_scores: list[tuple[int, int, float]], spectra: list[Spectrum]) -> None:
    bins = [i / 10 for i in range(11)]
    same = [0] * 10
    diff = [0] * 10
    for left, right, score in pair_scores:
        idx = min(9, max(0, int(score * 10)))
        if spectra[left].label == spectra[right].label:
            same[idx] += 1
        else:
            diff[idx] += 1
    max_v = max(same + diff) or 1

    def painter(draw, width, height):
        left, bottom, top = 110, height - 155, 145
        draw.line([left, top, left, bottom, width - 90, bottom], fill=(80, 95, 115), width=2)
        group_w = (width - left - 145) / 10
        for idx in range(10):
            gx = left + idx * group_w + 10
            h1 = (bottom - top) * same[idx] / max_v
            h2 = (bottom - top) * diff[idx] / max_v
            draw.rectangle([gx, bottom - h1, gx + group_w * 0.35, bottom], fill=(39, 159, 125))
            draw.rectangle([gx + group_w * 0.42, bottom - h2, gx + group_w * 0.77, bottom], fill=(202, 83, 76))
            draw_text(draw, (int(gx - 2), bottom + 18), f"{bins[idx]:.1f}", size=17)
        draw.rectangle([width - 360, 92, width - 332, 118], fill=(39, 159, 125))
        draw_text(draw, (width - 322, 88), "同标注谱图对", size=20)
        draw.rectangle([width - 190, 92, width - 162, 118], fill=(202, 83, 76))
        draw_text(draw, (width - 152, 88), "异标注谱图对", size=20)

    save_chart("候选谱图对碎片峰相似度分布", painter, path)


def draw_cluster_distribution(path: Path, true_labels: list[str], predicted: list[int]) -> None:
    true_sizes = sorted(Counter(true_labels).values(), reverse=True)[:20]
    pred_sizes = sorted(Counter(predicted).values(), reverse=True)[:20]
    max_v = max(true_sizes + pred_sizes) if true_sizes or pred_sizes else 1

    def painter(draw, width, height):
        left, bottom, top = 110, height - 155, 145
        draw.line([left, top, left, bottom, width - 90, bottom], fill=(80, 95, 115), width=2)
        group_w = (width - left - 145) / 20
        for idx in range(20):
            gx = left + idx * group_w + 4
            h1 = (bottom - top) * (true_sizes[idx] if idx < len(true_sizes) else 0) / max_v
            h2 = (bottom - top) * (pred_sizes[idx] if idx < len(pred_sizes) else 0) / max_v
            draw.rectangle([gx, bottom - h1, gx + group_w * 0.34, bottom], fill=(53, 120, 198))
            draw.rectangle([gx + group_w * 0.42, bottom - h2, gx + group_w * 0.76, bottom], fill=(39, 159, 125))
        draw_text(draw, (left, height - 88), "显示规模最大的前 20 个簇", size=22)
        draw.rectangle([width - 360, 92, width - 332, 118], fill=(53, 120, 198))
        draw_text(draw, (width - 322, 88), "TopPIC 标注组", size=20)
        draw.rectangle([width - 190, 92, width - 162, 118], fill=(39, 159, 125))
        draw_text(draw, (width - 152, 88), "聚类结果", size=20)

    save_chart("参考标注组与聚类簇规模分布", painter, path)


def draw_precursor_map(path: Path, spectra: list[Spectrum], predicted: list[int]) -> None:
    masses = [s.precursor_mass for s in spectra]
    charges = [s.precursor_charge for s in spectra]
    min_m, max_m = min(masses), max(masses)
    min_z, max_z = min(charges), max(charges)
    colors = [(53, 120, 198), (39, 159, 125), (231, 145, 55), (202, 83, 76), (126, 87, 194)]

    def painter(draw, width, height):
        left, right, top, bottom = 120, width - 95, 145, height - 145
        draw.rectangle([left, top, right, bottom], outline=(80, 95, 115), width=2)
        for spec, cluster in zip(spectra, predicted):
            x = left + (spec.precursor_mass - min_m) / (max_m - min_m) * (right - left)
            y = bottom - (spec.precursor_charge - min_z) / max(1, (max_z - min_z)) * (bottom - top)
            c = colors[cluster % len(colors)]
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=c)
        draw_text(draw, (left, height - 90), "横轴：前体质量；纵轴：前体荷电状态；颜色：预测簇编号取模", size=22)

    save_chart("谱图前体质量与荷电状态分布", painter, path)


def draw_memory(path: Path, results: list[dict]) -> None:
    labels = [item["algorithm"] for item in results]
    values = [max(item["peak_memory_mb"], 0.001) for item in results]
    max_v = max(values) if values else 1

    def painter(draw, width, height):
        left, bottom, top = 130, height - 165, 145
        draw.line([left, top, left, bottom, width - 90, bottom], fill=(80, 95, 115), width=2)
        group_w = (width - left - 125) / len(labels)
        for idx, label in enumerate(labels):
            gx = left + idx * group_w + 28
            h = (bottom - top) * values[idx] / max_v
            draw.rounded_rectangle([gx, bottom - h, gx + group_w * 0.45, bottom], radius=8, fill=(115, 135, 156))
            draw_text(draw, (int(gx - 6), int(bottom - h - 30)), f"{values[idx]:.3f}", size=17)
            draw_text(draw, (int(gx - 18), bottom + 18), label.replace("数据库过滤+", "过滤+\n").replace("前体质量-", "前体\n"), size=16)
        draw_text(draw, (left, height - 88), "单位：MB；使用 tracemalloc 记录算法阶段峰值", size=22)

    save_chart("算法阶段峰值内存对比", painter, path)


def create_outputs(spectra: list[Spectrum], candidates: list[tuple[int, int]], pair_scores: list[tuple[int, int, float]], results: list[dict], all_pairs: int) -> None:
    baseline_result = next(item for item in results if item["algorithm"].startswith("数据库过滤+碎片峰相似度≥0.30"))
    sensitivity = []
    for threshold in [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        edges = [(i, j) for i, j, score in pair_scores if score >= threshold]
        labels = cluster_by_edges(len(spectra), edges)
        sensitivity.append(
            {
                "threshold": threshold,
                "retained_edges": len(edges),
                "clusters": len(set(labels)),
                "ari": adjusted_rand_index([s.label for s in spectra], labels),
                "nmi": normalized_mutual_information([s.label for s in spectra], labels),
                "incorrect_rate": cluster_error_rate([s.label for s in spectra], labels),
            }
        )

    raw_count = 0
    for path in SOURCE_DIR.glob("*.msalign"):
        with path.open(encoding="utf-8", errors="ignore") as fh:
            raw_count += sum(1 for line in fh if line.startswith("BEGIN IONS"))

    metrics = {
        "dataset": {
            "source": "PRIDE PXD019368",
            "msalign_files": len(list(SOURCE_DIR.glob("*.msalign"))),
            "search_output_tables": len(list(SOURCE_DIR.glob("*.OUTPUT_TABLE"))),
            "raw_spectra_in_msalign": raw_count,
            "identified_spectra_used": len(spectra),
            "ground_truth_groups": len(set(s.label for s in spectra)),
            "top_peaks": TOP_PEAKS,
            "precursor_window_da": PRECURSOR_WINDOW_DA,
            "fragment_tolerance_ppm": FRAGMENT_TOLERANCE_PPM,
            "all_pairs": all_pairs,
            "precursor_candidate_pairs": len(candidates),
            "baseline_retained_edges": baseline_result["retained_edges"],
            "candidate_reduction_rate": 1 - len(candidates) / all_pairs,
            "sqlite_path": str(DB_PATH.relative_to(ROOT)),
            "pxd029703_raw_sample": str((PXD029703_DIR / "CRC_SW480_SEC4_RPLC1.raw").relative_to(ROOT))
            if (PXD029703_DIR / "CRC_SW480_SEC4_RPLC1.raw").exists()
            else "",
        },
        "results": results,
        "filter_sensitivity": sensitivity,
    }

    (OUT_DIR / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (PAPER_DATA_DIR / "experiment_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (PAPER_DATA_DIR / "toplib_dataset_summary.json").write_text(json.dumps(metrics["dataset"], ensure_ascii=False, indent=2), encoding="utf-8")

    write_csv(
        OUT_DIR / "algorithm_comparison.csv",
        results,
        ["algorithm", "clusters", "ari", "nmi", "incorrect_rate", "clustered_ratio", "runtime_sec", "peak_memory_mb", "candidate_pairs", "retained_edges"],
    )
    shutil.copy2(OUT_DIR / "algorithm_comparison.csv", PAPER_DATA_DIR / "algorithm_comparison.csv")
    write_csv(
        OUT_DIR / "filter_sensitivity.csv",
        sensitivity,
        ["threshold", "retained_edges", "clusters", "ari", "nmi", "incorrect_rate"],
    )
    (OUT_DIR / "filter_sensitivity.json").write_text(json.dumps(sensitivity, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(OUT_DIR / "filter_sensitivity.csv", PAPER_DATA_DIR / "filter_sensitivity.csv")

    draw_grouped_bars(OUT_DIR / "algorithm_metrics.png", results)
    draw_runtime(OUT_DIR / "runtime_comparison.png", results)
    draw_candidate_reduction(OUT_DIR / "candidate_reduction.png", all_pairs, len(candidates), baseline_result["retained_edges"])
    draw_memory(OUT_DIR / "memory_comparison.png", results)
    draw_sensitivity(OUT_DIR / "filter_sensitivity.png", sensitivity)
    draw_histogram(OUT_DIR / "similarity_histogram.png", pair_scores, spectra)
    baseline_labels = cluster_by_edges(len(spectra), [(i, j) for i, j, score in pair_scores if score >= BASELINE_THRESHOLD])
    draw_cluster_distribution(OUT_DIR / "cluster_size_distribution.png", [s.label for s in spectra], baseline_labels)
    draw_precursor_map(OUT_DIR / "cluster_projection.png", spectra, baseline_labels)

    for image in OUT_DIR.glob("*.png"):
        shutil.copy2(image, PAPER_IMG_DIR / image.name)


def main() -> None:
    ensure_dirs()
    labels = read_identifications()
    spectra = read_spectra(labels)
    if not spectra:
        raise RuntimeError(f"No usable spectra found in {SOURCE_DIR}")
    build_database(spectra)
    candidates = precursor_candidates(spectra)
    pair_scores = [(left, right, fragment_cosine(spectra[left], spectra[right])) for left, right in candidates]
    results, all_pairs = run_methods(spectra, candidates, pair_scores)
    create_outputs(spectra, candidates, pair_scores, results, all_pairs)
    print(json.dumps({"spectra": len(spectra), "candidate_pairs": len(candidates), "all_pairs": all_pairs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
