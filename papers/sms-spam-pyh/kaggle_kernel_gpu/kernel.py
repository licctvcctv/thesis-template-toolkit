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
import tensorflow as tf
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


ROOT = Path("/kaggle/working")
DATA = Path("/kaggle/input/message/message80W1.csv")
if not DATA.exists():
    DATA = next(Path("/kaggle/input").glob("**/message80W1.csv"))
OUT_ROOT = ROOT / "training_runs"
IMG_DIR = ROOT / "outputs"
IMG_DIR.mkdir(parents=True, exist_ok=True)

font_candidates = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
font_file = next((f for f in font_candidates if Path(f).exists()), None)
FONT = FontProperties(fname=font_file) if font_file else FontProperties()


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
    arr = np.zeros((len(texts), max_len), dtype=np.int32)
    for i, text in enumerate(texts):
        ids = [vocab.get(ch, unk) for ch in text[:max_len]]
        arr[i, : len(ids)] = ids
    return arr


def build_model(vocab_size, max_len=80):
    inputs = tf.keras.Input(shape=(max_len,), dtype="int32")
    x = tf.keras.layers.Embedding(vocab_size, 64, mask_zero=True)(inputs)
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=1e-4),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(curve="PR", name="average_precision"),
            tf.keras.metrics.AUC(curve="ROC", name="roc_auc"),
        ],
    )
    return model


class LogCallback(tf.keras.callbacks.Callback):
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.epoch_start = None

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = time.time()
        self.log(f"epoch={epoch + 1} begin")

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        elapsed = time.time() - (self.epoch_start or time.time())
        self.log(
            "epoch={epoch} done loss={loss:.5f} acc={acc:.5f} "
            "val_loss={val_loss:.5f} val_acc={val_acc:.5f} "
            "val_recall={val_recall:.5f} val_f1=pending seconds={seconds:.1f}".format(
                epoch=epoch + 1,
                loss=float(logs.get("loss", 0.0)),
                acc=float(logs.get("accuracy", 0.0)),
                val_loss=float(logs.get("val_loss", 0.0)),
                val_acc=float(logs.get("val_accuracy", 0.0)),
                val_recall=float(logs.get("val_recall", 0.0)),
                seconds=elapsed,
            )
        )


def evaluate_scores(y_true, y_score):
    y_pred = (y_score > 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "average_precision": float(average_precision_score(y_true, y_score)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "preds": y_pred,
    }


def plot_outputs(run_dir, history_rows, y_true, y_score, y_pred, counts):
    plt.rcParams["axes.unicode_minus"] = False

    epochs = [h["epoch"] for h in history_rows]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=180)
    axes[0].plot(epochs, [h["loss"] for h in history_rows], marker="o", label="训练Loss", color="#1f77b4")
    axes[0].plot(epochs, [h["val_loss"] for h in history_rows], marker="s", label="验证Loss", color="#ff7f0e")
    axes[0].set_title("Kaggle GPU全量训练损失", fontproperties=FONT, fontsize=14)
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].grid(True, ls="--", alpha=0.3)
    axes[0].legend(prop=FONT, frameon=False)
    axes[1].plot(epochs, [h["accuracy"] for h in history_rows], marker="o", label="训练Accuracy", color="#1f77b4")
    axes[1].plot(epochs, [h["val_accuracy"] for h in history_rows], marker="s", label="验证Accuracy", color="#ff7f0e")
    axes[1].set_title("Kaggle GPU全量训练准确率", fontproperties=FONT, fontsize=14)
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].grid(True, ls="--", alpha=0.3)
    axes[1].legend(prop=FONT, frameon=False)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("真实运行：80万条短信BiLSTM完整训练曲线", fontproperties=FONT, fontsize=16)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-9-kaggle-gpu-full-training-curves.png", bbox_inches="tight")
    plt.close(fig)

    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6.4, 5.8), dpi=180)
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["正常短信", "垃圾短信"], fontproperties=FONT)
    ax.set_yticks([0, 1], ["正常短信", "垃圾短信"], fontproperties=FONT)
    ax.set_xlabel("预测类别", fontproperties=FONT)
    ax.set_ylabel("真实类别", fontproperties=FONT)
    ax.set_title("Kaggle GPU全量训练测试集混淆矩阵", fontproperties=FONT, fontsize=14)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-10-kaggle-gpu-full-confusion-matrix.png", bbox_inches="tight")
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
    fig.suptitle("真实运行：Kaggle GPU全量训练模型概率输出曲线", fontproperties=FONT, fontsize=15)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fig4-11-kaggle-gpu-full-pr-roc.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.8, 4.8), dpi=180)
    names = ["总样本", "训练集", "测试集", "正常短信", "垃圾短信"]
    values = [counts["total"], counts["train"], counts["test"], counts["ham"], counts["spam"]]
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
    fig.savefig(IMG_DIR / "fig4-12-kaggle-gpu-full-data-scale.png", bbox_inches="tight")
    plt.close(fig)

    log_lines = (run_dir / "train.log").read_text(encoding="utf-8").splitlines()[-18:]
    fig, ax = plt.subplots(figsize=(11.8, 6.2), dpi=180)
    ax.set_facecolor("#101418")
    fig.patch.set_facecolor("#101418")
    ax.axis("off")
    y = 0.94
    ax.text(0.03, y, "Kaggle GPU 80W Full Training Log", color="#7dd3fc", fontsize=15, family="monospace")
    y -= 0.08
    for line in log_lines:
        ax.text(0.04, y, line, color="#e5e7eb", fontsize=9.8, family="monospace")
        y -= 0.050
    fig.savefig(IMG_DIR / "fig4-13-kaggle-gpu-full-training-log.png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    start = time.time()
    run_dir = OUT_ROOT / f"kaggle_gpu_full_bilstm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "train.log"

    def log(message):
        print(message, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(message + "\n")

    gpus = tf.config.list_physical_devices("GPU")
    log(f"dataset={DATA}")
    log(f"tensorflow={tf.__version__} gpu_count={len(gpus)} gpu_devices={[str(g) for g in gpus]}")
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

    model = build_model(vocab_size=len(vocab), max_len=80)
    model.summary(print_fn=log)
    class_weight = {0: 1.0, 1: float((y_train == 0).sum() / max((y_train == 1).sum(), 1))}
    log(f"class_weight={class_weight}")
    epochs = 5
    batch_size = 2048
    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=[LogCallback(log)],
        verbose=2,
    )

    y_score = model.predict(x_test, batch_size=batch_size).reshape(-1)
    final = evaluate_scores(y_test.astype(int), y_score)
    history_rows = []
    for idx in range(epochs):
        row = {
            "epoch": idx + 1,
            "loss": float(history.history["loss"][idx]),
            "accuracy": float(history.history["accuracy"][idx]),
            "precision": float(history.history["precision"][idx]),
            "recall": float(history.history["recall"][idx]),
            "average_precision": float(history.history["average_precision"][idx]),
            "roc_auc": float(history.history["roc_auc"][idx]),
            "val_loss": float(history.history["val_loss"][idx]),
            "val_accuracy": float(history.history["val_accuracy"][idx]),
            "val_precision": float(history.history["val_precision"][idx]),
            "val_recall": float(history.history["val_recall"][idx]),
            "val_average_precision": float(history.history["val_average_precision"][idx]),
            "val_roc_auc": float(history.history["val_roc_auc"][idx]),
        }
        row["val_f1"] = float(2 * row["val_precision"] * row["val_recall"] / max(row["val_precision"] + row["val_recall"], 1e-8))
        history_rows.append(row)

    metrics = {
        "dataset": str(DATA),
        "tensorflow": tf.__version__,
        "gpu_count": len(gpus),
        "gpu_devices": [str(g) for g in gpus],
        "total_samples": int(len(df)),
        "ham_samples": int((df.label == 0).sum()),
        "spam_samples": int((df.label == 1).sum()),
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "vocab_size": int(len(vocab)),
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": 1e-3,
        "training_seconds": time.time() - start,
        "history": history_rows,
        "final": {k: v for k, v in final.items() if k != "preds"},
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    model.save(run_dir / "model.keras")
    plot_outputs(
        run_dir,
        history_rows,
        y_test.astype(int),
        y_score,
        final["preds"],
        {
            "total": int(len(df)),
            "train": int(len(train_df)),
            "test": int(len(test_df)),
            "ham": int((df.label == 0).sum()),
            "spam": int((df.label == 1).sum()),
        },
    )
    log(
        f"final accuracy={final['accuracy']:.5f} precision={final['precision']:.5f} "
        f"recall={final['recall']:.5f} f1={final['f1']:.5f} "
        f"ap={final['average_precision']:.5f} roc_auc={final['roc_auc']:.5f}"
    )
    log(f"training_seconds={metrics['training_seconds']:.1f}")
    log(f"run_dir={run_dir}")


if __name__ == "__main__":
    main()
