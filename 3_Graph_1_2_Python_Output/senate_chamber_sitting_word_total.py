#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# ============================================================
# PURPOSE:
#   - Graph 1: Total WORDS per year in MILLIONS — Senate vs Chamber (1848–1938)
#   - Graph 2: Total SESSIONS per year — Senate vs Chamber (1848–1938)
#
# INPUT:
#   - Excel: parole_camera_senato_per_anno.xlsx
#   - Columns (header): year, senato_words, camera_words, senato_sessions, camera_sessions
#
# OUTPUT:
#   - output_grafici/graph_1_words_senate_chamber.png
#   - output_grafici/graph_2_sessions_senate_chamber.png
#
# STYLE:
#   - Black lines: Senate dashed, Chamber solid
#   - Period shading (very light pastel bands)
# ============================================================

# ==========
# INPUT/OUTPUT
# ==========
FILE_EXCEL = "parole_camera_senato_per_anno.xlsx"  # put full path if needed
SHEET_NAME = "Sheet1"

OUTDIR = "output_grafici"
os.makedirs(OUTDIR, exist_ok=True)

OUT_WORDS = os.path.join(OUTDIR, "graph_1_words_senate_chamber.png")
OUT_SESS  = os.path.join(OUTDIR, "graph_2_sessions_senate_chamber.png")

YEAR_MIN, YEAR_MAX = 1848, 1938

# ==========
# PERIOD SHADING
# ==========
PERIODS = [
    (1848.0, 1861.5, "#f6f6f6", "1848–1861 Kingdom of Sardinia"),
    (1861.5, 1882.5, "#fff4cc", "1861–1882 restricted suffrage"),
    (1882.5, 1912.5, "#e6f6f2", "1882–1912 expanded suffrage"),
    (1912.5, 1922.5, "#f1e9ff", "1912–1922 universal male suffrage"),
    (1922.5, 1938.5, "#d9d9d9", "1922–1938 Fascism"),
]
BREAKS = [1861, 1882, 1912, 1922]

def add_period_shading(ax, alpha=0.22):
    for start, end, color, _ in PERIODS:
        ax.axvspan(start, end, facecolor=color, alpha=alpha, edgecolor="none", zorder=0)
    for b in BREAKS:
        ax.axvline(b, color="black", linewidth=0.6, alpha=0.12, zorder=1)
    ax.set_xlim(YEAR_MIN, YEAR_MAX)
    ax.set_axisbelow(True)

# ==========
# READ DATA
# ==========
raw = pd.read_excel(FILE_EXCEL, sheet_name=SHEET_NAME, engine="openpyxl")
raw.columns = [str(c).strip().lower() for c in raw.columns]

required = ["year", "senato_words", "camera_words", "senato_sessions", "camera_sessions"]
missing = [c for c in required if c not in raw.columns]
if missing:
    raise ValueError(
        f"Missing columns: {missing}\n"
        f"Available columns: {list(raw.columns)}\n"
        "Tip: header must be: year senato_words camera_words senato_sessions camera_sessions"
    )

df = raw[required].copy()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"]).copy()
df["year"] = df["year"].astype(int)
df = df[(df["year"] >= YEAR_MIN) & (df["year"] <= YEAR_MAX)].sort_values("year")

for c in ["senato_words", "camera_words", "senato_sessions", "camera_sessions"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ==========
# GRAPH 1: WORDS (IN MILLIONS)
# ==========
df["senato_words_m"] = df["senato_words"] / 1_000_000
df["camera_words_m"] = df["camera_words"] / 1_000_000

fig = plt.figure(figsize=(14, 5))
ax = plt.gca()
add_period_shading(ax, alpha=0.22)

ax.plot(df["year"], df["senato_words_m"], linestyle="--", color="black", linewidth=1.6, label="Senate",  zorder=3)
ax.plot(df["year"], df["camera_words_m"], linestyle="-",  color="black", linewidth=1.6, label="Chamber", zorder=3)

ax.set_title("Graph 2. Total words — Senate vs Chamber (1848–1938)")
ax.set_xlabel("Year")
ax.set_ylabel("Count (millions of words)")

# y ticks as 1,2,3,... (integer ticks)
ymax = max(df["senato_words_m"].max(), df["camera_words_m"].max())
ymax_int = max(1, int(math.ceil(ymax)))
ax.set_ylim(0, ymax_int * 1.02)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))

ax.set_xticks(df["year"])
ax.set_xticklabels(df["year"], rotation=90, fontsize=7)
ax.grid(True, linewidth=0.4, alpha=0.5, zorder=2)
ax.legend(frameon=False, ncol=2, loc="upper left")

plt.tight_layout()
plt.savefig(OUT_WORDS, dpi=300)
plt.close()

# ==========
# GRAPH 2: SESSIONS
# ==========
fig = plt.figure(figsize=(14, 5))
ax = plt.gca()
add_period_shading(ax, alpha=0.22)

ax.plot(df["year"], df["senato_sessions"], linestyle="--", color="black", linewidth=1.6, label="Senate",  zorder=3)
ax.plot(df["year"], df["camera_sessions"], linestyle="-",  color="black", linewidth=1.6, label="Chamber", zorder=3)

ax.set_title("Graph 1. Total sittings — Senate vs Chamber (1848–1938)")
ax.set_xlabel("Year")
ax.set_ylabel("Sittings")  # <- no "Counts (sittings)"

ax.set_xticks(df["year"])
ax.set_xticklabels(df["year"], rotation=90, fontsize=7)
ax.grid(True, linewidth=0.4, alpha=0.5, zorder=2)
ax.legend(frameon=False, ncol=2, loc="upper left")

plt.tight_layout()
plt.savefig(OUT_SESS, dpi=300)
plt.close()

print("OK. Saved:")
print(" -", OUT_WORDS)
print(" -", OUT_SESS)