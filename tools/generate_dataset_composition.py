"""Render the recorded labeled inventory without loading waveform datasets."""

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


ROOT = Path(__file__).resolve().parents[1]
COLORS = {'Maintenance': '#f39c12', 'Normal': '#27ae60', 'Compressor Down': '#e74c3c'}


def main():
    inventory = json.loads((ROOT / 'datasets/inventory.json').read_text(encoding='utf-8'))
    rows = sorted((row for row in inventory['files'] if row['label'] is not None),
                  key=lambda row: (row['status'], row['file']))
    fig, ax = plt.subplots(figsize=(10, 4.8), layout='constrained')
    ax.barh([row['file'] for row in rows], [row['n_windows'] for row in rows],
            color=[COLORS[row['status']] for row in rows])
    for index, row in enumerate(rows):
        ax.text(row['n_windows'] + 1600, index,
                f"{row['status']} ({row['n_windows']:,})", va='center', fontsize=9)
    ax.set_title('Labelled dataset composition')
    ax.set_xlabel('Recorded 128-sample windows per selected channel')
    ax.set_xlim(0, max(row['n_windows'] for row in rows) * 1.48)
    ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.set_axisbelow(True)
    ax.grid(axis='x', alpha=0.25)
    ax.spines[['top', 'right']].set_visible(False)
    output = ROOT / 'thesis_figures/03_dataset_composition.png'
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, dpi=240, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Saved {output.relative_to(ROOT)} (recorded inventory; unlabeled NASA file excluded)')


if __name__ == '__main__':
    main()
