#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import random
from pathlib import Path

import requests
import pandas as pd


# =========================
# CONFIGURAZIONE
# =========================

INPUT_XLSX = "senato_resoconti_sedute.xlsx"
OUTPUT_DIR = Path("senato_resoconti_pdf")

# pause diverse (secondi) scelte a caso
SLEEP_CHOICES = [0.7, 3.4, 1.1, 6.0, 1.6, 2.2, 1.0, 3.0, 1.0]

# user agent simile a Chrome
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


# =========================
# FUNZIONI DI SUPPORTO
# =========================

def int_to_roman(num: int) -> str:
    """Converte un intero positivo (es. 30) in numeri romani (es. 'XXX')."""
    try:
        num = int(num)
    except (TypeError, ValueError):
        return str(num)

    if num <= 0:
        return str(num)

    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = []
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num.append(syms[i])
            num -= val[i]
        i += 1
    return "".join(roman_num)


def extract_year_from_giorno(giorno: str) -> str:
    """
    Cerca un anno a 4 cifre nella stringa 'giorno' (es. '8 maggio 1848')
    e lo restituisce come stringa. Se non trova nulla, restituisce '0000'.
    """
    if pd.isna(giorno):
        return "0000"
    text = str(giorno)
    m = re.search(r"(\d{4})", text)
    if m:
        return m.group(1)
    return "0000"


def clean_int(value) -> int | None:
    """Prova a convertire a int. Se fallisce, restituisce None."""
    try:
        v = int(str(value).strip())
        return v
    except Exception:
        return None


def ensure_unique_path(path: Path) -> Path:
    """
    Se 'path' esiste già, aggiunge suffissi _dup1, _dup2, ... finché non
    trova un nome libero.
    """
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    i = 1
    while True:
        new_path = parent / f"{stem}_dup{i}{suffix}"
        if not new_path.exists():
            return new_path
        i += 1


def format_seconds(seconds: float) -> str:
    """Converte un numero di secondi in stringa hh:mm:ss o mm:ss."""
    if seconds < 0:
        seconds = 0
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


# =========================
# DOWNLOAD DI UN SINGOLO ANNO
# =========================

def download_for_year(df: pd.DataFrame, year: int, leg_col: str) -> None:
    """
    Scarica tutti i PDF relativi all'anno indicato.
    Salva un log separato per quell'anno.
    """
    year_str = str(year)
    df_year = df[df["anno_seduta"] == year_str].copy().reset_index(drop=True)

    if df_year.empty:
        print(f"\n[Anno {year_str}] Nessuna seduta trovata, salto.")
        return

    print(f"\n=== ANNO {year_str}: {len(df_year)} sedute da scaricare ===")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_log = OUTPUT_DIR / f"download_log_senato_resoconti_{year_str}.csv"

    log_rows = []
    total_rows = len(df_year)
    start_time = time.time()

    for idx, row in df_year.iterrows():
        pdf_url = row.get("pdf_url", "")
        done = idx + 1

        # ETA per l'anno
        elapsed = time.time() - start_time
        avg_per_file = elapsed / done if done > 0 else 0
        remaining = (total_rows - done) * avg_per_file
        eta_str = format_seconds(remaining)

        if pd.isna(pdf_url) or not str(pdf_url).strip():
            print(f"[{done}/{total_rows}] Anno {year_str} – nessun PDF (no_url). ETA ~ {eta_str}")
            log_rows.append(
                {
                    "row_index": idx,
                    "pdf_url": "",
                    "output_file": "",
                    "anno_seduta": year_str,
                    "status": "no_url",
                }
            )
            continue

        pdf_url = str(pdf_url).strip()

        # Legislatura in numeri romani
        roman_leg = ""
        if "legislatura_roman" in df.columns:
            roman_leg = str(row.get("legislatura_roman") or "").strip()
        if not roman_leg:
            legislatura_val = row.get(leg_col, "")
            roman_leg = int_to_roman(legislatura_val) if legislatura_val is not None else "NA"

        # Numero seduta
        num_seduta = row.get("numero_seduta", "")
        num_sed_int = clean_int(num_seduta)
        if num_sed_int is not None and num_sed_int >= 0:
            num_part = f"n{num_sed_int:02d}"
        else:
            num_part = "n00"

        # Nome file
        base_name = f"{year_str}_seduta_{roman_leg}_{num_part}.pdf"
        out_path = OUTPUT_DIR / base_name
        out_path = ensure_unique_path(out_path)

        print(
            f"[{done}/{total_rows}] Anno {year_str}, leg. {roman_leg}, seduta {num_part} "
            f"(ETA residua ~ {eta_str})"
        )
        print(f"    URL: {pdf_url}")

        # Download
        try:
            resp = requests.get(pdf_url, headers=HEADERS, timeout=60)
            resp.raise_for_status()
            out_path.write_bytes(resp.content)
            status = "ok"
            print(f"    -> Salvato come: {out_path.name}")
        except Exception as e:
            status = f"error: {e}"
            print(f"    !! ERRORE nello scaricare {pdf_url}: {e}")

        log_rows.append(
            {
                "row_index": idx,
                "pdf_url": pdf_url,
                "output_file": str(out_path),
                "anno_seduta": year_str,
                "status": status,
            }
        )

        # === PAUSE "DISSONANTI" ===
        if done % 50 == 0:
            # pausa lunga 3–6 minuti
            long_pause = random.uniform(180, 360)
            print(f"    >> Pausa lunga (ogni 50 PDF) ~ {format_seconds(long_pause)}")
            time.sleep(long_pause)
        elif done % 10 == 0:
            # pausa media 1–3 minuti
            mid_pause = random.uniform(60, 180)
            print(f"    >> Pausa media (ogni 10 PDF) ~ {format_seconds(mid_pause)}")
            time.sleep(mid_pause)
        else:
            # pausa breve, ma almeno 2 secondi
            delay = max(2.0, random.choice(SLEEP_CHOICES))
            # volendo puoi loggare anche questo:
            # print(f"    >> Pausa breve ~ {delay:.1f} s")
            time.sleep(delay)

    # Salva log per l'anno
    log_df = pd.DataFrame(log_rows)
    log_df.to_csv(output_log, index=False)
    print(f"\n[Anno {year_str}] Log salvato in: {output_log}")
    print(f"[Anno {year_str}] Download completato.")


# =========================
# MAIN
# =========================

def main():
    # Controllo input
    if not Path(INPUT_XLSX).is_file():
        raise FileNotFoundError(
            f"File di input '{INPUT_XLSX}' non trovato nella cartella corrente."
        )

    print(f"Carico il file di input: {INPUT_XLSX}")
    df = pd.read_excel(INPUT_XLSX)

    # Colonne minime
    required_base = ["pdf_url", "giorno"]
    missing = [c for c in required_base if c not in df.columns]
    if missing:
        raise ValueError(
            "Mancano le seguenti colonne nel file Excel:\n"
            + ", ".join(missing)
        )

    # Colonna legislatura
    leg_col = None
    if "legislatura_num_arabic" in df.columns:
        leg_col = "legislatura_num_arabic"
    elif "legislatura" in df.columns:
        leg_col = "legislatura"
    else:
        raise ValueError(
            "Non trovo né 'legislatura_num_arabic' né 'legislatura' nel file Excel."
        )

    # Aggiungo colonna anno_seduta
    df["anno_seduta"] = df["giorno"].apply(extract_year_from_giorno)

    # Chiedo a te anno di inizio e fine
    default_start = 1848
    default_end = 1861

    try:
        start_input = input(f"Anno di inizio (default {default_start}): ").strip()
        end_input = input(f"Anno di fine, incluso (default {default_end}): ").strip()
    except EOFError:
        # in caso di run non interattivo
        start_input = ""
        end_input = ""

    if start_input:
        try:
            start_year = int(start_input)
        except ValueError:
            print(f"Valore non valido per anno di inizio, uso default {default_start}.")
            start_year = default_start
    else:
        start_year = default_start

    if end_input:
        try:
            end_year = int(end_input)
        except ValueError:
            print(f"Valore non valido per anno di fine, uso default {default_end}.")
            end_year = default_end
    else:
        end_year = default_end

    if start_year > end_year:
        print(f"Attenzione: anno di inizio {start_year} > anno di fine {end_year}, inverto.")
        start_year, end_year = end_year, start_year

    print(f"\nScaricherò gli anni da {start_year} a {end_year} (inclusi).")

    # Loop sugli anni
    first = True
    for year in range(start_year, end_year + 1):
        if first:
            print(f"\n*** Inizio download per l'anno {year} ***")
            download_for_year(df, year, leg_col)
            first = False
        else:
            ans = input(
                f"\nVuoi procedere con il download per l'anno {year}? [s/N]: "
            ).strip().lower()

            if ans not in ("s", "si", "y", "yes", "1"):
                print(f"\nInterrotto su richiesta prima dell'anno {year}.")
                break

            print(f"\n*** Inizio download per l'anno {year} ***")
            download_for_year(df, year, leg_col)

    print("\nTutto il ciclo anni completato (o interrotto da te).")


if __name__ == "__main__":
    main()