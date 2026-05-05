import json
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from matplotlib.font_manager import FontProperties
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "kaggle_data" / "message80W1.csv"
OUT_ROOT = ROOT / "training_runs"
IMG_DIR = ROOT / "images"
FONT = FontProperties(fname="/System/Library/Fonts/STHeiti Medium.ttc")


def normalize_text(text):
    text = str(text or "")
    text = re.sub(r"\s+", "", text)
    return "".join(ch for ch in text if ch.isalnum())[:80]


def build_vocab(texts, max_vocab=6000):
    counter = Counter()
    for text in texts:
        counter.update(text)
    vocab = {"[PAD]": 0, "[UNK]": 1}
    for token, _ in counter.most_common(max_vocab - 2):
        vocab[token] = len(vocab)
    return vocab


def encode_texts(texts, vocab, max_len=80):
    unk = vocab["[UNK]"]
    arr = np.zeros((len(texts), max_len), dtype=np.int64)
    for i, text in enumerate(texts):
        ids = [vocab.get(ch, unk) for ch in text[:max_len]]
        arr[i, : len(ids)] = ids
    return arr


class CharBiLSTM(nn.Module):
    def __init__(self, vocab_size, emb_dim=64, hidden_dim=64, dropout=0.2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=emb_dim,
            hidden_size=hidden_dim,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, 1)

    def forward(self, input_ids):
        emb = self.embedding(input_ids)
        _, (hidden, _) = self.lstm(emb)
        hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)
        hidden = self.dropout(hidden)
        return self.fc(hidden).squeeze(-1)


def evaluate(model, loader, device):
    model.eval()
    losses = []
    scores = []
    labels_all = []
    criterion = nn.BCEWithLogitsLoss()
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            probs = torch.sigmoid(logits).detach().cpu().numpy()
            scores.extend(probs.tolist())
            labels_all.extend(y.detach().cpu().numpy().tolist())
            losses.append(loss.item() * len(y))
    labels = np.asarray(labels_all, dtype=np.int64)
    scores_arr = np.asarray(scores)
    preds = (scores_arr > 0.5).astype(np.int64)
    return {
        "loss": float(np.sum(losses) / max(len(labels), 1)),
        "accuracy": float(accuracy_score(labels, preds)),
        "precision": float(precision_score(labels, preds, zero_division=0)),
        "recall": float(recall_score(labels, preds, zero_division=0)),
        "f1": float(f1_score(labels, preds, zero_division=0)),
        "average_precision": float(average_precision_score(labels, scores_arr)),
        "roc_auc": float(roc_auc_score(labels, scores_arr)),
        "labels": labels,
        "scores": scores_arr,
        "preds": preds,
    }


def plot_outputs(run_dir, history, y_true, y_score, y_pred, counts):
    plt.rcParams["axes.unicode_minus"] = False

    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    val_loss = [h["val_loss"] for h in history]
    train_acc = [h["train_accuracy"] for h in history]
    val_acc = [h["val_accuracy"] for h in history]

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=180)
    axes[0].plot(epochs, train_loss, marker="o", label="训练Loss", color="#1f77b4")
    axes[0].plot(epochs, val_loss, marker="s", label="验证Loss", color="#ff7f0e")
    axes[0].set_title("Kaggle全量数据训练损失", fontproperties=FONT, fontsize=14)
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].grid(True, ls="--", alpha=0.3)
    axes[0].legend(prop=FONT, frameon=False)
    axes[1].plot(epochs, train_acc, marker="o", label="训练Accuracy", color="#1f77b4")
    axes[1].plot(epochs, val_acc, marker="s", label="验证Accuracy", color="#ff7f0e")
    axes[1].set_title("Kaggle全量数据训练准确率", fontproperties=FONT, fontsize=14)
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].grid(True, ls="--", alpha=0.3)
    axes[1].legend(prop=FONT, frameon=False)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("真实运行：80万条短信BiLSTM完整训练曲线", fontproperties=FONT, fontsize=16)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-9-kaggle-full-training-curves.png", bbox_inches="tight")
    plt.close(fig)

    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6.4, 5.8), dpi=180)
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["正常短信", "垃圾短信"], fontproperties=FONT)
    ax.set_yticks([0, 1], ["正常短信", "垃圾短信"], fontproperties=FONT)
    ax.set_xlabel("预测类别", fontproperties=FONT)
    ax.set_ylabel("真实类别", fontproperties=FONT)
    ax.set_title("Kaggle全量训练模型测试集混淆矩阵", fontproperties=FONT, fontsize=14)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-10-kaggle-full-confusion-matrix.png", bbox_inches="tight")
    plt.close(fig)

    precision, recall, _ = precision_recall_curve(y_true, y_score)
    fpr, tpr, _ = roc_curve(y_true, y_score)
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2), dpi=180)
    axes[0].plot(recall, precision, color="#1f77b4", lw=2.4)
    axes[0].set_title("Precision-Recall曲线", fontproperties=FONT, fontsize=13)
    axes[0].set_xlabel("Recall")
    axes[0].set_ylabel("Precision")
    axes[0].grid(True, ls="--", alpha=0.3)
    axes[1].plot(fpr, tpr, color="#ff7f0e", lw=2.4)
    axes[1].plot([0, 1], [0, 1], color="#999", ls="--")
    axes[1].set_title("ROC曲线", fontproperties=FONT, fontsize=13)
    axes[1].set_xlabel("False Positive Rate")
    axes[1].set_ylabel("True Positive Rate")
    axes[1].grid(True, ls="--", alpha=0.3)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("真实运行：Kaggle全量训练模型概率输出曲线", fontproperties=FONT, fontsize=15)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-11-kaggle-full-pr-roc.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.8, 4.8), dpi=180)
    names = ["总样本", "训练集", "测试集", "正常短信", "垃圾短信"]
    values = [
        counts["total"],
        counts["train"],
        counts["test"],
        counts["ham"],
        counts["spam"],
    ]
    colors = ["#3b82c4", "#4daf4a", "#f59e0b", "#2b8cbe", "#e85d3f"]
    bars = ax.bar(names, values, color=colors, width=0.58)
    ax.set_title("Kaggle完整数据训练样本规模", fontproperties=FONT, fontsize=14)
    ax.set_ylabel("样本数量", fontproperties=FONT)
    ax.grid(axis="y", ls="--", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(FONT)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.015, f"{value:,}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-12-kaggle-full-data-scale.png", bbox_inches="tight")
    plt.close(fig)

    log_lines = (run_dir / "train.log").read_text(encoding="utf-8").splitlines()[-16:]
    fig, ax = plt.subplots(figsize=(11.8, 6.2), dpi=180)
    ax.set_facecolor("#101418")
    fig.patch.set_facecolor("#101418")
    ax.axis("off")
    y = 0.94
    ax.text(0.03, y, "Kaggle 80W Full Training Log", color="#7dd3fc", fontsize=15, family="monospace")
    y -= 0.08
    for line in log_lines:
        ax.text(0.04, y, line, color="#e5e7eb", fontsize=10.5, family="monospace")
        y -= 0.055
    fig.savefig(IMG_DIR / "fig4-13-kaggle-full-training-log.png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    start = time.time()
    run_dir = OUT_ROOT / f"kaggle_full_bilstm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "train.log"

    def log(message):
        print(message, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(message + "\n")

    log(f"dataset={DATA}")
    df = pd.read_csv(DATA, header=None, names=["id", "label", "content"], encoding="utf-8-sig")
    df["label"] = df["label"].astype(int)
    df["text"] = df["content"].map(normalize_text)
    df = df[df["text"].str.len() > 0].reset_index(drop=True)
    log(f"loaded rows={len(df):,}, ham={(df.label == 0).sum():,}, spam={(df.label == 1).sum():,}")

    train_df, test_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df["label"])
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    vocab = build_vocab(train_df["text"], max_vocab=6000)
    log(f"split train={len(train_df):,}, test={len(test_df):,}, vocab={len(vocab):,}")

    x_train = encode_texts(train_df["text"], vocab)
    x_test = encode_texts(test_df["text"], vocab)
    y_train = train_df["label"].to_numpy(dtype=np.float32)
    y_test = test_df["label"].to_numpy(dtype=np.float32)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    log(f"device={device}")
    batch_size = 1024
    train_loader = DataLoader(
        TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train)),
        batch_size=batch_size,
        shuffle=True,
    )
    test_loader = DataLoader(
        TensorDataset(torch.from_numpy(x_test), torch.from_numpy(y_test)),
        batch_size=batch_size,
        shuffle=False,
    )

    model = CharBiLSTM(vocab_size=len(vocab)).to(device)
    pos_weight = torch.tensor([(y_train == 0).sum() / max((y_train == 1).sum(), 1)], dtype=torch.float32).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    history = []
    epochs = 3
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        total_loss = 0.0
        total_correct = 0
        total_seen = 0
        for batch_idx, (x, y) in enumerate(train_loader, start=1):
            x = x.to(device)
            y = y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            with torch.no_grad():
                preds = (torch.sigmoid(logits) > 0.5).float()
                total_loss += loss.item() * len(y)
                total_correct += (preds == y).sum().item()
                total_seen += len(y)
            if batch_idx % 100 == 0 or batch_idx == len(train_loader):
                log(
                    f"epoch={epoch}/{epochs} batch={batch_idx}/{len(train_loader)} "
                    f"loss={total_loss/total_seen:.5f} acc={total_correct/total_seen:.5f}"
                )

        val = evaluate(model, test_loader, device)
        row = {
            "epoch": epoch,
            "train_loss": float(total_loss / total_seen),
            "train_accuracy": float(total_correct / total_seen),
            "val_loss": val["loss"],
            "val_accuracy": val["accuracy"],
            "val_precision": val["precision"],
            "val_recall": val["recall"],
            "val_f1": val["f1"],
            "val_average_precision": val["average_precision"],
            "val_roc_auc": val["roc_auc"],
            "epoch_seconds": time.time() - epoch_start,
        }
        history.append(row)
        log(
            f"epoch={epoch} done train_loss={row['train_loss']:.5f} "
            f"train_acc={row['train_accuracy']:.5f} val_acc={row['val_accuracy']:.5f} "
            f"val_recall={row['val_recall']:.5f} val_f1={row['val_f1']:.5f} "
            f"seconds={row['epoch_seconds']:.1f}"
        )

    final = evaluate(model, test_loader, device)
    metrics = {
        "dataset": str(DATA),
        "total_samples": int(len(df)),
        "ham_samples": int((df.label == 0).sum()),
        "spam_samples": int((df.label == 1).sum()),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "vocab_size": int(len(vocab)),
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": 1e-3,
        "device": str(device),
        "training_seconds": time.time() - start,
        "history": history,
        "final": {
            key: value
            for key, value in final.items()
            if key not in {"labels", "scores", "preds"}
        },
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    torch.save({"model_state_dict": model.cpu().state_dict(), "vocab": vocab, "metrics": metrics}, run_dir / "model.pt")
    plot_outputs(
        run_dir,
        history,
        final["labels"],
        final["scores"],
        final["preds"],
        {
            "total": int(len(df)),
            "train": int(len(train_df)),
            "test": int(len(test_df)),
            "ham": int((df.label == 0).sum()),
            "spam": int((df.label == 1).sum()),
        },
    )
    log(f"final accuracy={metrics['final']['accuracy']:.5f} precision={metrics['final']['precision']:.5f} recall={metrics['final']['recall']:.5f} f1={metrics['final']['f1']:.5f} ap={metrics['final']['average_precision']:.5f}")
    log(f"run_dir={run_dir}")


if __name__ == "__main__":
    main()
