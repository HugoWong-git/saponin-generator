#!/usr/bin/env python
"""Generate a PDF summary table of all TL and RL results."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.table as tbl
import numpy as np

ROOT = "."

# ── Data ───────────────────────────────────────────────────────────────
# TL epoch results
tl_data = [
    ["TL Epoch 1", "0.8595", "0.9990", "23.80", "1.463", "43.83", "88.6%", "96.1%"],
    ["TL Epoch 2", "0.8633", "0.9980", "23.84", "1.433", "42.68", "89.4%", "98.0%"],
    ["TL Epoch 3", "0.8697", "0.9971", "23.90", "1.423", "41.58", "89.4%", "100%"],
    ["TL Epoch 4", "0.8618", "0.9978", "23.87", "1.409", "40.94", "85.7%", "96.0%"],
]
tl_cols = ["Model", "Validity", "Novelty", "FCD", "FDD", "Mean NLL", "Triterp.", "Terpenoid"]

# RL results (10k sample)
rl_data = [
    ["E4 Prior (no RL)", "0.8618", "0.9978", "13.62", "12.97", "3.58", "24%", "1.3%", "86%", "96%"],
    ["V1 RL (lenient)",   "0.8633", "0.9980", "8.28",  "8.03",  "2.36", "84%", "4.5%", "89%", "98%"],
    ["V3 RL (tight)",     "0.3722", "1.0000", "1.65",  "1.55",  "0.90", "83.6%","0.2%", "100%","100%"],
    ["V3 RL (100k)",      "0.2072", "1.0000", "1.73",  "1.61",  "0.89", "78.6%","0.2%", "100%","100%"],
]
rl_cols = ["Model", "Validity", "Novelty", "Mean\nIC50", "Median\nIC50", "Min\nIC50",
           "%<2µM", "%<1µM", "Triterp.", "Terpenoid"]

# ── Create PDF ─────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle("Saponin REINVENT4 — TL & IC50‑RL Results Summary", fontsize=16, fontweight='bold', y=0.98)

# --- TL Table ---
ax1.axis('off')
t1 = ax1.table(cellText=tl_data, colLabels=tl_cols, loc='center', cellLoc='center')
t1.auto_set_font_size(False)
t1.set_fontsize(10)
t1.scale(1.0, 1.8)
for (row, col), cell in t1.get_celld().items():
    if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white', fontweight='bold')
    elif row % 2 == 0: cell.set_facecolor('#ecf0f1')
    else: cell.set_facecolor('white')
    cell.set_edgecolor('#bdc3c7')
ax1.set_title("A. Transfer Learning — 4 Epoch × 4 Block Regularized", fontsize=12, fontweight='bold', pad=10)

# --- RL Table ---
ax2.axis('off')
t2 = ax2.table(cellText=rl_data, colLabels=rl_cols, loc='center', cellLoc='center')
t2.auto_set_font_size(False)
t2.set_fontsize(10)
t2.scale(1.0, 1.8)
for (row, col), cell in t2.get_celld().items():
    if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white', fontweight='bold')
    elif row % 2 == 0: cell.set_facecolor('#ecf0f1')
    else: cell.set_facecolor('white')
    cell.set_edgecolor('#bdc3c7')
ax2.set_title("B. IC50‑Guided RL (DAP, 500 steps, starting from E4 prior)", fontsize=12, fontweight='bold', pad=10)

plt.tight_layout(rect=[0, 0, 1, 0.94])
pdf_path = f"{ROOT}/reports/saponin_TL_RL_results_summary.pdf"
plt.savefig(pdf_path, dpi=200, bbox_inches='tight', pad_inches=0.3)
print(f"Saved: {pdf_path}")