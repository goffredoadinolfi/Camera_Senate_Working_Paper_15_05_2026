#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopo:
    - Leggere tutti i PDF nelle cartelle:
        * /Users/goffredo/Documents/Articoli Giornali Scientifici/
          Database_elezioni_italia_liberale/Senato_Atti/senato_atti
        * /Users/goffredo/Documents/Articoli Giornali Scientifici/
          Database_elezioni_italia_liberale/Camera_atti/camera_atti
    - Periodo di riferimento: 1848–1946
    - Estrarre l'anno dal nome file (prime 4 cifre trovate, es. 1848)
    - Considerare SOLO gli anni che:
        * sono nel range 1848–1946
        * compaiono almeno una volta sia nei PDF del Senato sia nei PDF della Camera
    - Per questi anni:
        * contare il numero di parole nei PDF per anno e per ramo (Senato / Camera)
        * contare il numero di PDF (sessioni) per anno e per ramo
    - Salvare un file Excel con la tabella dei conteggi
      (parole per anno + numero di sessioni per anno)
    - Salvare due grafici (PNG), in bianco e nero:
        * parole per anno (Senato vs Camera)
            - linea nera continua: Senato
            - linea nera tratteggiata: Camera
        * sessioni per anno (Senato vs Camera)
            - linea nera continua: Senato
            - linea nera tratteggiata: Camera
      con:
        - asse X inferiore: tutti gli anni (tick per ogni anno)
        - asse X superiore: etichette delle Legislature sull'anno di inizio
          (I–XXX, compresso 'II–IV' per il 1849)

NOTE IMPORTANTI:
    - Questo script RICALCOLA TUTTO DA ZERO.
      Non fa aggiornamento incrementale: ignora l'eventuale contenuto
      del file Excel esistente.
    - Se esiste già 'parole_camera_senato_per_anno.xlsx':
        * PRIMA di sovrascriverlo viene creata una copia di backup
          con nome:
              parole_camera_senato_per_anno_backup_XXX.xlsx

Librerie utilizzate:
    - pathlib (gestione percorsi)
    - re (regex per estrarre l'anno)
    - shutil (per creare i backup)
    - pandas (costruzione e salvataggio tabella)
    - matplotlib (grafici in bianco e nero)
    - PyPDF2 (lettura testo dai PDF)

Prerequisiti:
    pip install pandas matplotlib PyPDF2
"""

import re
import shutil
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader

# =========================
# CONFIGURAZIONE
# =========================

# Cartelle di input (percorsi ASSOLUTI)
SENATO_DIR = Path(
    "/Users/goffredo/Documents/Articoli Giornali Scientifici/"
    "Database_elezioni_italia_liberale/Senato_Atti/senato_atti"
)

CAMERA_DIR = Path(
    "/Users/goffredo/Documents/Articoli Giornali Scientifici/"
    "Database_elezioni_italia_liberale/Camera_atti/camera_atti"
)

# File di output (nella cartella da cui lanci lo script)
OUTPUT_EXCEL = Path("parole_camera_senato_per_anno.xlsx")
OUTPUT_PLOT_WORDS = Path("parole_camera_senato_parole_per_anno.png")
OUTPUT_PLOT_SESS  = Path("parole_camera_senato_sessioni_per_anno.png")

# Periodo di interesse fisso
MIN_YEAR = 1848
MAX_YEAR = 1946

# Mappa anni di inizio legislatura → etichetta (compressa per 1849: II–IV)
LEGISLATURE_LABELS_BY_YEAR = {
    1848: "I",
    1849: "II–IV",  # II, III, IV tutte nel 1849
    1853: "V",
    1857: "VI",
    1860: "VII",
    1861: "VIII",
    1865: "IX",
    1867: "X",
    1870: "XI",
    1874: "XII",
    1876: "XIII",
    1880: "XIV",
    1882: "XV",
    1886: "XVI",
    1890: "XVII",
    1892: "XVIII",
    1895: "XIX",
    1897: "XX",
    1900: "XXI",
    1904: "XXII",
    1909: "XXIII",
    1913: "XXIV",
    1919: "XXV",
    1921: "XXVI",
    1924: "XXVII",
    1929: "XXVIII",
    1934: "XXIX",
    1939: "XXX",
}


# =========================
# FUNZIONI DI SUPPORTO
# =========================

def extract_year_from_name(filename: str) -> int | None:
    """
    Estrae le prime 4 cifre consecutive dal nome del file e le interpreta come anno.
    Restituisce None se non trova nulla o se l'anno è fuori dal range MIN_YEAR–MAX_YEAR.
    """
    m = re.search(r"(\d{4})", filename)
    if not m:
        return None
    year = int(m.group(1))
    if year < MIN_YEAR or year > MAX_YEAR:
        return None
    return year


def detect_years_in_folder(folder: Path) -> set[int]:
    """
    Scorre tutti i PDF in 'folder' e restituisce l'insieme degli anni
    (nel range MIN_YEAR–MAX_YEAR) trovati nei nomi file.
    NON apre i PDF, guarda solo i nomi.
    """
    if not folder.is_dir():
        raise FileNotFoundError(f"Cartella non trovata: {folder}")

    years_found: set[int] = set()
    pdf_files = folder.glob("*.pdf")
    for pdf_path in pdf_files:
        year = extract_year_from_name(pdf_path.name)
        if year is not None:
            years_found.add(year)

    return years_found


def count_words_in_pdf(pdf_path: Path) -> int:
    """
    Apre il PDF e conta le parole nel testo.
    Se ci sono problemi di lettura, restituisce 0 ma stampa un warning.
    """
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as e:
        print(f"[ATTENZIONE] Impossibile aprire {pdf_path}: {e}")
        return 0

    text_chunks = []
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text()
        except Exception as e:
            print(f"[ATTENZIONE] Problema nell'estrarre testo da {pdf_path}, pagina {i}: {e}")
            continue
        if txt:
            text_chunks.append(txt)

    full_text = " ".join(text_chunks)
    words = full_text.split()
    return len(words)


def process_folder(
    folder: Path,
    chamber_label: str,
    years_to_process: set[int]
) -> tuple[dict[int, int], dict[int, int]]:
    """
    Scorre tutti i PDF in 'folder', estrae l'anno dal nome file,
    conta le parole e il numero di file (sessioni) per anno.

    Elabora solo gli anni in 'years_to_process'.

    Restituisce due dizionari:
        - words_per_year:   {year: total_words_for_that_year}
        - sessions_per_year:{year: number_of_pdfs_for_that_year}

    chamber_label è solo per i messaggi di log (es. "Senato", "Camera").
    """
    if not folder.is_dir():
        raise FileNotFoundError(f"Cartella non trovata: {folder}")

    print(f"\n=== Elaboro cartella {chamber_label}: {folder} ===")

    words_per_year: dict[int, int] = {}
    sessions_per_year: dict[int, int] = {}

    pdf_files = sorted(folder.glob("*.pdf"))
    if not pdf_files:
        print(f"[ATTENZIONE] Nessun PDF trovato in {folder}")

    for pdf_path in pdf_files:
        year = extract_year_from_name(pdf_path.name)
        # Se anno non valido o anno non richiesto → salto
        if year is None or year not in years_to_process:
            continue

        print(f"  - {chamber_label}: {pdf_path.name} (anno {year}) → conto parole...")
        n_words = count_words_in_pdf(pdf_path)
        print(f"    → {n_words} parole")

        words_per_year[year] = words_per_year.get(year, 0) + n_words
        sessions_per_year[year] = sessions_per_year.get(year, 0) + 1

    return words_per_year, sessions_per_year


def make_backup_if_exists(path: Path) -> None:
    """
    Se 'path' esiste, crea una copia di backup con suffisso incrementale:
        nomefile_backup_001.xlsx
        nomefile_backup_002.xlsx
        ...
    """
    if not path.is_file():
        return

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    i = 1
    while True:
        backup_name = parent / f"{stem}_backup_{i:03d}{suffix}"
        if not backup_name.exists():
            shutil.copy2(path, backup_name)
            print(f"[BACKUP] Creato backup: {backup_name}")
            break
        i += 1


def add_legislature_axis(ax, years_series: pd.Series) -> None:
    """
    Aggiunge un asse X superiore con le etichette delle Legislature.
    - Tick in alto solo sugli anni presenti in LEGISLATURE_LABELS_BY_YEAR
      e compresi nel range dei dati.
    - Etichette: numeri romani (compressi tipo 'II–IV').
    """
    years = years_series.astype(int)
    x_min = int(years.min())
    x_max = int(years.max())

    leg_years = [
        y for y in sorted(LEGISLATURE_LABELS_BY_YEAR.keys())
        if x_min <= y <= x_max
    ]
    if not leg_years:
        return

    leg_labels = [LEGISLATURE_LABELS_BY_YEAR[y] for y in leg_years]

    ax_top = ax.secondary_xaxis('top')
    ax_top.set_xticks(leg_years)
    ax_top.set_xticklabels(leg_labels, rotation=90, fontsize=6)
    ax_top.set_xlabel("Legislature")


# =========================
# MAIN
# =========================

def main():
    # 1) Rilevo gli anni presenti nelle cartelle (solo da nomi file)
    years_senato = detect_years_in_folder(SENATO_DIR)
    years_camera = detect_years_in_folder(CAMERA_DIR)

    print(f"Anni trovati nel Senato (da nomi file, {MIN_YEAR}-{MAX_YEAR}):")
    print(sorted(years_senato))
    print(f"\nAnni trovati nella Camera (da nomi file, {MIN_YEAR}-{MAX_YEAR}):")
    print(sorted(years_camera))

    # Anni in comune tra Senato e Camera
    common_years = sorted(years_senato & years_camera)
    print(f"\nAnni presenti in ENTRAMBE le camere:")
    print(common_years)

    if not common_years:
        print("\n[STOP] Non ci sono anni in comune tra le due cartelle nel range "
              f"{MIN_YEAR}-{MAX_YEAR}. Controlla i PDF.")
        return

    common_years_set = set(common_years)

    # 2) Elaboro TUTTI gli anni in comune (nessun aggiornamento incrementale)
    print("\nElaboro TUTTI gli anni in comune (ricalcolo completo):")
    print(common_years)

    counts_senato_words, sessions_senato = process_folder(
        SENATO_DIR, "Senato", years_to_process=common_years_set
    )
    counts_camera_words, sessions_camera = process_folder(
        CAMERA_DIR, "Camera", years_to_process=common_years_set
    )

    # 3) Costruisco il DataFrame finale da zero
    rows = []
    for y in sorted(common_years_set):
        sen_words = counts_senato_words.get(y, 0)
        cam_words = counts_camera_words.get(y, 0)
        sen_sess  = sessions_senato.get(y, 0)
        cam_sess  = sessions_camera.get(y, 0)

        rows.append({
            "year": y,
            "senato_words": sen_words,
            "camera_words": cam_words,
            "senato_sessions": sen_sess,
            "camera_sessions": cam_sess,
        })

    if not rows:
        print("\n[STOP] Nessun dato da salvare. Controlla MIN_YEAR, MAX_YEAR e i PDF.")
        return

    df_all = pd.DataFrame(rows)
    df_all = df_all.sort_values("year")
    df_all["total_words"] = df_all["senato_words"] + df_all["camera_words"]
    df_all["total_sessions"] = df_all["senato_sessions"] + df_all["camera_sessions"]

    # 4) Backup dell'Excel esistente (se c'è), poi salvataggio NUOVO
    make_backup_if_exists(OUTPUT_EXCEL)
    df_all.to_excel(OUTPUT_EXCEL, index=False)
    print(f"\n[OK] Tabella COMPLETAMENTE RICALCOLATA salvata in: {OUTPUT_EXCEL.resolve()}")
    print("\n=== Prime righe della tabella ===")
    print(df_all.head())

    # Lista ordinata di tutti gli anni (per i tick dell'asse X)
    years = df_all["year"].astype(int).sort_values().unique()

    # 5) Grafico parole per anno (bianco e nero, legislature sopra)
    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    ax.plot(
        df_all["year"],
        df_all["senato_words"],
        marker="o",
        linestyle="-",
        color="black",
        label="Senate"
    )
    ax.plot(
        df_all["year"],
        df_all["camera_words"],
        marker="o",
        linestyle="--",
        color="black",
        label="Chamber"
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of words in PDFs")
    ax.set_title("Total words per year in parliamentary acts (Senate vs Chamber)")
    ax.legend()
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)

    # Tick per ogni anno sull'asse X
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=90, fontsize=6)

    # Asse superiore con Legislature
    add_legislature_axis(ax, df_all["year"])

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_WORDS, dpi=300)
    plt.close()
    print(f"[OK] Grafico parole per anno salvato in: {OUTPUT_PLOT_WORDS.resolve()}")

    # 6) Grafico sessioni per anno (stessa estetica)
    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    ax.plot(
        df_all["year"],
        df_all["senato_sessions"],
        marker="o",
        linestyle="-",
        color="black",
        label="Senate sessions"
    )
    ax.plot(
        df_all["year"],
        df_all["camera_sessions"],
        marker="o",
        linestyle="--",
        color="black",
        label="Chamber sessions"
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of sessions (PDFs)")
    ax.set_title("Number of sessions per year (Senate vs Chamber)")
    ax.legend()
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)

    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=90, fontsize=6)

    add_legislature_axis(ax, df_all["year"])

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_SESS, dpi=300)
    plt.close()
    print(f"[OK] Grafico sessioni per anno salvato in: {OUTPUT_PLOT_SESS.resolve()}")

    print("\nFatto.")


if __name__ == "__main__":
    main()