#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from pathlib import Path

import requests
import pandas as pd  # solo per salvare il log in csv (puoi togliere se non ti serve)


# =========================
# CONFIGURAZIONE
# =========================

YEAR = "1921"            # anno che vuoi nel nome file
LEG  = "25"              # legislatura: leg04
SED_START = 136         # da sed204...
SED_END   = 193          # ...a sed396

BASE_URL = f"https://storia.camera.it/regno/lavori/leg{LEG}"
OUTPUT_DIR = Path("camera_atti")
OUTPUT_LOG = OUTPUT_DIR / f"download_log_camera_leg{LEG}_{YEAR}.csv"

# pause brevi tra un PDF e l'altro (secondi) — VERSIONE PIÙ RAPIDA
SLEEP_CHOICES = [0.4, 0.7, 1.0, 1.5, 2.0, 0.6, 1.2, 1.8]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


# =========================
# UTILS
# =========================

def format_seconds(seconds: float) -> str:
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


def ensure_unique_path(path: Path) -> Path:
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


# =========================
# MAIN
# =========================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log_rows = []
    total = SED_END - SED_START + 1
    start_time = time.time()

    print("======================================")
    print(f"Scarico Camera – Regno di Sardegna")
    print(f"  Anno (nome file): {YEAR}")
    print(f"  Legislatura: leg{LEG}")
    print(f"  Sedute: {SED_START:03d} → {SED_END:03d}")
    print(f"  Base URL: {BASE_URL}/sedXXX.pdf")
    print("======================================\n")

    for i, sed in enumerate(range(SED_START, SED_END + 1), start=1):
        sed_label = f"{sed:03d}"   # es. 1 -> "001"
        url = f"{BASE_URL}/sed{sed_label}.pdf"

        elapsed = time.time() - start_time
        avg_per = elapsed / i if i > 0 else 0
        remaining = (total - i) * avg_per
        eta_str = format_seconds(remaining)

        print(f"[{i}/{total}] sed{sed_label} – ETA residua ~ {eta_str}")
        print(f"    URL: {url}")

        base_name = f"{YEAR}_let{LEG}_sed{sed_label}.pdf"
        out_path = OUTPUT_DIR / base_name
        out_path = ensure_unique_path(out_path)

        status = ""
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            if resp.status_code == 200 and resp.content:
                out_path.write_bytes(resp.content)
                status = "ok"
                print(f"    -> Salvato come: {out_path.name}")
            else:
                status = f"http_{resp.status_code}"
                print(f"    !! Nessun file valido (status {resp.status_code})")
        except Exception as e:
            status = f"error: {e}"
            print(f"    !! ERRORE nello scaricare {url}: {e}")

        log_rows.append(
            {
                "anno": YEAR,
                "legislatura": LEG,
                "seduta": sed_label,
                "url": url,
                "output_file": str(out_path) if status == "ok" else "",
                "status": status,
            }
        )

        # Pausa dopo ogni download (VERSIONE PIÙ RAPIDA)
        if i % 50 == 0:
            # pausa lunga ~2,5 minuti (anziché 5)
            long_pause = 150 + random.uniform(-15, 15)   # 2,5 min ± 15 s
            print(f"    >> Pausa lunga di circa {format_seconds(long_pause)} (ogni 50 PDF)")
            time.sleep(max(long_pause, 0))
        elif i % 20 == 0:
            # pausa media tra 30 e 90 secondi (anziché 60–180)
            mid_pause = random.uniform(30, 90)
            print(f"    >> Pausa media di circa {format_seconds(mid_pause)} (ogni 20 PDF)")
            time.sleep(mid_pause)
        else:
            # pausa breve random
            delay = random.choice(SLEEP_CHOICES)
            time.sleep(delay)

    # log
    log_df = pd.DataFrame(log_rows)
    log_df.to_csv(OUTPUT_LOG, index=False)

    total_time = time.time() - start_time
    print(f"\nLog salvato in: {OUTPUT_LOG}")
    print(f"Download completato in {format_seconds(total_time)}.")


if __name__ == "__main__":
    main()