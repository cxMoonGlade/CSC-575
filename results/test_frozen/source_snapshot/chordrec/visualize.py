"""Create an inspectable example from actual saved predictions."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .audio import extract_features
from .data import load_reference, reduce_label
from .model import LABELS, combine_features


def make_example(output, record, config, root):
    from .run import read_intervals, save_csv
    output = Path(output)
    destination = output / "examples" / record["id"]
    destination.mkdir(parents=True, exist_ok=True)
    features = extract_features(root / record["audio"], config)
    _, weights = combine_features(features, "adaptive", config)
    times, duration = features["times"], features["duration"]
    save_csv(destination / "adaptive_weights.csv", [dict(time=float(t), short_weight=float(w))
                                                   for t, w in zip(times, weights)])
    reference = load_reference(root / record["annotation"], config["annotation"])
    tracks = [("Reference", [(a, b, reduce_label(c) or "X") for a, b, c in reference])]
    for method in ("short", "long", "cqt", "equal", "fixed", "adaptive"):
        path = output / "predictions" / record["id"] / f"{method}_viterbi.csv"
        if path.exists():
            tracks.append((method, read_intervals(path)))
    fig, axes = plt.subplots(4, 1, figsize=(13, 9), sharex=True,
                             gridspec_kw={"height_ratios": [1.1, 1.1, .7, 2.2]}, layout="constrained")
    names = [label.split(":")[0] for label in LABELS[:12]]
    for ax, name in zip(axes[:2], ("short", "long")):
        ax.pcolormesh(times, np.arange(12), features[name], shading="nearest", cmap="magma", vmin=0, vmax=1)
        ax.set_yticks(np.arange(12), names, fontsize=7)
        ax.set_ylabel(f"{name} chroma")
    axes[2].plot(times, weights, color="#225ea8", linewidth=1)
    axes[2].set(ylabel="Short weight", ylim=(-.05, 1.05))
    colors = plt.get_cmap("tab20")
    for row, (name, intervals) in enumerate(tracks):
        for start, end, label in intervals:
            if label in ("N", "X"):
                color, hatch = ("#cccccc" if label == "N" else "white"), (None if label == "N" else "xx")
            else:
                index = LABELS.index(label)
                color, hatch = colors((index % 12) / 12), ("//" if index >= 12 else None)
            axes[3].broken_barh([(start, end - start)], (row - .35, .7),
                                 facecolors=color, edgecolors="#555555", linewidth=.3, hatch=hatch)
            if end - start > .85:
                axes[3].text((start + end) / 2, row, label.replace(":maj", "").replace(":min", "m"),
                             ha="center", va="center", fontsize=6)
    axes[3].set_yticks(range(len(tracks)), [name for name, _ in tracks])
    axes[3].invert_yaxis()
    axes[3].set(xlim=(0, duration), xlabel="Time (s)")
    fig.suptitle(f"{record['id']} — {record['split']} example ({config['annotation']} labels; X = excluded)", fontsize=12)
    for ext in ("png", "pdf"):
        fig.savefig(destination / f"timeline.{ext}", dpi=160)
    plt.close(fig)
    from .demo import write_player
    write_player(destination / "playback.html", root / record["audio"], record["id"], tracks, duration,
                 split=record["split"], annotation=config["annotation"])
