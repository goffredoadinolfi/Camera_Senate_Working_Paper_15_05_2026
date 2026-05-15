#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========
# INPUT/OUTPUT
# ==========
FILE_EXCEL = "parole_chiave_camera_senato_per_anno.xlsx"   # se serve metti path completo
SHEET_NAME = "Sheet1"

OUTDIR = "output_grafici"
os.makedirs(OUTDIR, exist_ok=True)

OUT_WAR   = os.path.join(OUTDIR, "graph_3_war_guerra_senate_chamber.png")
OUT_MULTI = os.path.join(OUTDIR, "graph_4_key_terms_panels_senate_chamber.png")

YEAR_MIN, YEAR_MAX = 1848, 1938

# Header ESATTO (22 colonne)
COLS = [
    "year",
    "senato_democrazia","camera_democrazia","total_democrazia",
    "senato_socialismo","camera_socialismo","total_socialismo",
    "senato_fascismo","camera_fascismo","total_fascismo",
    "senato_guerra","camera_guerra","total_guerra",
    "senato_suffragio","camera_suffragio","total_suffragio",
    "senato_suffragio_universale","camera_suffragio_universale","total_suffragio_universale",
    "senato_assemblea_costituente","camera_assemblea_costituente","total_assemblea_costituente",
]

# ==========
# LETTURA DATI (file senza header: prima riga vuota)
# ==========
df = pd.read_excel(
    FILE_EXCEL,
    sheet_name=SHEET_NAME,
    header=None,
    skiprows=1,
    names=COLS,
    engine="openpyxl"
)

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"]).copy()
df["year"] = df["year"].astype(int)
df = df[(df["year"] >= YEAR_MIN) & (df["year"] <= YEAR_MAX)].sort_values("year")

for c in COLS:
    if c != "year":
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ==========
# PERIOD SHADING (visibile ma soft)
# ==========
# Usiamo confini a mezzo anno per evitare sovrapposizioni visive sugli anni-chiave.
# Slightly stronger (still soft) grey for the Fascism band:
FASCISM_COLOR = "#d9d9d9"   # a touch darker than #e7e7e7

# ...so your PERIODS becomes:
PERIODS = [
    (1848.0, 1861.5, "#f6f6f6", "1848–1861 Kingdom of Sardinia"),
    (1861.5, 1882.5, "#fff4cc", "1861–1882 restricted suffrage"),
    (1882.5, 1912.5, "#e6f6f2", "1882–1912 expanded suffrage"),
    (1912.5, 1922.5, "#f1e9ff", "1912–1922 universal male suffrage"),
    (1922.5, 1938.5, FASCISM_COLOR, "1922–1938 Fascism"),
]

BREAKS = [1861, 1882, 1912, 1922]

def add_period_shading(ax, alpha=0.22):
    # bande
    for start, end, color, _ in PERIODS:
        ax.axvspan(start, end, facecolor=color, alpha=alpha, edgecolor="none", zorder=0)

    # linee sottili sui break (aiutano anche se i colori sono leggeri)
    for b in BREAKS:
        ax.axvline(b, color="black", linewidth=0.6, alpha=0.12, zorder=1)

    ax.set_xlim(YEAR_MIN, YEAR_MAX)
    ax.set_axisbelow(True)

# ==========
# GRAPH 1: WAR (guerra)
# ==========
fig = plt.figure(figsize=(14, 5))
ax = plt.gca()

add_period_shading(ax, alpha=0.22)

ax.plot(df["year"], df["senato_guerra"], linestyle="--", color="black", linewidth=1.6, label="Senate",  zorder=3)
ax.plot(df["year"], df["camera_guerra"], linestyle="-",  color="black", linewidth=1.6, label="Chamber", zorder=3)

ax.set_title(r"Graph 3. War ($\bf{guerra}$) — Senate vs Chamber (1848–1938)")
ax.set_xlabel("Year")
ax.set_ylabel("Occurrences (raw counts)")
ax.set_xticks(df["year"])
ax.set_xticklabels(df["year"], rotation=90, fontsize=7)
ax.grid(True, linewidth=0.4, alpha=0.5, zorder=2)
ax.legend(frameon=False, ncol=2, loc="upper left")

plt.tight_layout()
plt.savefig(OUT_WAR, dpi=300)
plt.close()

# ==========
# GRAPH 2: ONE PANEL PER TERM (stacked)
# ==========
terms = [
    ("democrazia",  r"Democracy ($\bf{democrazia}$)"),
    ("socialismo",  r"Socialism ($\bf{socialismo}$)"),
    ("suffragio",   r"Suffrage ($\bf{suffragio}$)"),
    ("fascismo",    r"Fascism ($\bf{fascismo}$)"),
    ("assemblea_costituente", r"Constituent Assembly ($\bf{assemblea\ costituente}$)"),
]

n = len(terms)
fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(14, 12), sharex=True)

for ax, (term, title) in zip(axes, terms):
    add_period_shading(ax, alpha=0.22)

    ax.plot(df["year"], df[f"senato_{term}"], linestyle="--", color="black", linewidth=1.4, label="Senate",  zorder=3)
    ax.plot(df["year"], df[f"camera_{term}"], linestyle="-",  color="black", linewidth=1.4, label="Chamber", zorder=3)

    ax.set_title(title, loc="left", fontsize=11)
    ax.set_ylabel("Counts")
    ax.grid(True, linewidth=0.4, alpha=0.5, zorder=2)
    ax.legend(frameon=False, ncol=2, fontsize=9, loc="upper left")

axes[-1].set_xlabel("Year")
axes[-1].set_xticks(df["year"])
axes[-1].set_xticklabels(df["year"], rotation=90, fontsize=7)

fig.suptitle("Graph 4. Key terms — Senate (--) vs Chamber (—), 1848–1938", y=0.995, fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.985])

plt.savefig(OUT_MULTI, dpi=300)
plt.close()

print("OK. Saved:")
print(" -", OUT_WAR)
print(" -", OUT_MULTI)