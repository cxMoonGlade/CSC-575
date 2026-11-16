"""Plot reference-group error rates and one saved post-evaluation example."""
import argparse
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import numpy as np


def intervals(path):
    with path.open() as stream:
        rows = [(float(row['start']), float(row['end']), row['label']) for row in csv.DictReader(stream)]
    merged = []
    for start, end, label in rows:
        if merged and merged[-1][2] == label and abs(merged[-1][1] - start) < 1e-7:
            merged[-1] = merged[-1][0], end, label
        else:
            merged.append((start, end, label))
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.project / 'docs/research/root_questions_2026-11-13/annotation_check.json'
    data = json.loads(source.read_text())
    grouped = data['by_reference_pitch_set']
    plt.rcParams.update({'font.size': 7, 'axes.titlesize': 8, 'axes.labelsize': 7,
                         'xtick.labelsize': 7, 'ytick.labelsize': 7, 'pdf.fonttype': 42,
                         'hatch.linewidth': .45})
    fig, axes = plt.subplots(3, 1, figsize=(3.4, 3.25), layout='constrained',
                             gridspec_kw={'height_ratios': [1.3, 1, 0.55]})
    ax = axes[0]
    centers = np.arange(2)
    for index, (method, label, color) in enumerate([
        ('long_viterbi', 'Long STFT', '#426b96'), ('projection_viterbi', 'Projection', '#cf783d')]):
        values = [100 * grouped[group][method + '/quality_wrong'] / grouped[group]['reference_seconds']
                  for group in ['triad_pitch_set', 'extended_pitch_set']]
        bars = ax.bar(centers + (index - 0.5) * 0.3, values, width=0.29, label=label, color=color)
        ax.bar_label(bars, fmt='%.2f', padding=2, fontsize=7)
    ax.set_xticks(centers, ['Triad pitch classes', 'Additional chord tones'])
    ax.set_ylabel('Quality-error time (%)')
    ax.set_ylim(0, 8.7)
    ax.set_yticks([0, 2, 4, 6, 8])
    ax.set_title('(a) Errors by reference type', loc='left')
    ax.legend(frameon=False, fontsize=7, loc='upper left')
    ax.spines[['top', 'right']].set_visible(False)
    ax = axes[1]
    folder = args.project / 'results/root_optimization/fast/predictions/rock_6'
    files = ['reference.csv', 'long_viterbi.csv', 'projection_viterbi.csv']
    tracks = [intervals(folder / name) for name in files]
    lower, upper = tracks[0][0][0], tracks[0][-1][1]
    colors = {'A': '#90b8d8', 'D': '#edc477', 'E': '#96c8a5'}
    for y, track in enumerate(tracks):
        for start, end, label in track:
            start, end = max(start, lower), min(end, upper)
            if end <= start:
                continue
            root = label.split(':')[0]
            minor = ':min' in label
            color = colors.get(root, '#dddddd')
            segment = Rectangle((start, y - .3), end - start, .6, facecolor=color,
                                edgecolor='#444444', linewidth=.3,
                                hatch='///' if minor else None)
            ax.add_patch(segment)
            segment.set_clip_path(Rectangle((start, y - .3), end - start, .6,
                                            transform=ax.transData))
            ax.add_patch(Rectangle((start, y - .3), end - start, .6, facecolor='none',
                                   edgecolor='#444444', linewidth=.3))
    ax.set_yticks(range(3), ['Reference (7th)', 'Long STFT', 'Projection'])
    ax.set_ylim(2.55, -.55)
    ax.set_xlim(lower, upper)
    ax.set_xticks([10, 20, 30, 40, 50])
    ax.set_xlabel('Time (s)')
    ax.set_title('(b) rock_6: original labels and predictions', loc='left')
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    legend_ax = axes[2]
    legend_ax.set_axis_off()
    root_handles = [Patch(facecolor=color, edgecolor='#444444', linewidth=.3, label=root)
                    for root, color in colors.items()]
    root_handles.append(Patch(facecolor='#dddddd', edgecolor='#444444', linewidth=.3,
                              label='Other'))
    root_legend = legend_ax.legend(handles=root_handles, title='Root', title_fontsize=7,
                                   loc='upper center', bbox_to_anchor=(.5, 1.15), ncol=4,
                                   frameon=False, fontsize=7, handlelength=1.3,
                                   columnspacing=1, handletextpad=.4, borderaxespad=0)
    legend_ax.add_artist(root_legend)
    quality_handles = [
        Patch(facecolor='white', edgecolor='#444444', linewidth=.3, label='Major prediction'),
        Patch(facecolor='white', edgecolor='#444444', linewidth=.3, hatch='///',
              label='Minor prediction')]
    legend_ax.legend(handles=quality_handles, loc='lower center', bbox_to_anchor=(.5, -.05),
                     ncol=2, frameon=False, fontsize=7, handlelength=1.3,
                     columnspacing=1, handletextpad=.4, borderaxespad=0)
    args.output.mkdir(parents=True, exist_ok=True)
    for ext in ['pdf', 'png']:
        fig.savefig(args.output / ('quality_diagnostic.' + ext), dpi=220)
    plt.close(fig)


if __name__ == '__main__':
    main()
