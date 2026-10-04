"""Paso 1: descarga de microdatos DEIS (defunciones) y proyecciones INE base 2017.

Estrategia:
1. Intenta descubrir los enlaces vigentes inspeccionando el HTML de las páginas
   fuente (no se hardcodean URLs de archivos, que cambian).
2. Si la descarga falla (p. ej. red bloqueada), registra el fallo y usa los
   archivos que el usuario haya dejado manualmente en data/raw/.
3. Registra en data/raw/SOURCES.md: archivo, URL u origen, fecha, tamaño y SHA-256.

Uso:  .venv/bin/python scripts/01_download.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SOURCES = RAW / "SOURCES.md"
TODAY = dt.date.today().isoformat()
TIMEOUT = 60

# Páginas donde se buscan los enlaces y patrones que identifican cada archivo.
TARGETS = {
    "deis_defunciones_1990_2021": {
        "page": "https://deis.minsal.cl/",
        "pattern": re.compile(r"defunciones.*(1990|causa).*2021", re.I),
    },
    "deis_defunciones_2022_actual": {
        "page": "https://deis.minsal.cl/",
        "pattern": re.compile(r"defunciones.*(2022|semanal|actual|presente)", re.I),
    },
    "ine_proyecciones_comunas_base2017": {
        "page": "https://www.ine.gob.cl/estadisticas/sociales/demografia-y-vitalidad/"
                "proyecciones-de-poblacion",
        "pattern": re.compile(r"(comuna|comunal).*(2002|2017|2035|proyecc)", re.I),
    },
}
DATA_EXT = (".zip", ".csv", ".xlsx", ".xls", ".rar", ".7z")
# Patrones para reconocer archivos dejados manualmente en data/raw/.
MANUAL_PATTERNS = {
    "deis_defunciones_1990_2021": re.compile(r"(DEFUNCIONES|DEF).*(1990|2021)", re.I),
    "deis_defunciones_2022_actual": re.compile(r"(DEFUNCIONES|DEF).*(2022|SEMANA|ACTUAL)", re.I),
    "ine_proyecciones_comunas_base2017": re.compile(r"(proyecc|estimac|ine|comuna)", re.I),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_links(page: str, pattern: re.Pattern) -> list[str]:
    r = requests.get(page, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page, a["href"])
        text = " ".join([a.get_text(" ", strip=True), a.get("title", ""), href])
        if href.lower().split("?")[0].endswith(DATA_EXT) and pattern.search(text):
            out.append(href)
    return list(dict.fromkeys(out))


def download(url: str) -> Path:
    name = url.split("?")[0].rstrip("/").split("/")[-1]
    dest = RAW / name
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    return dest


def manual_file(key: str) -> Path | None:
    cands = [p for p in RAW.iterdir()
             if p.is_file() and p.name != "SOURCES.md" and MANUAL_PATTERNS[key].search(p.name)]
    return max(cands, key=lambda p: p.stat().st_mtime) if cands else None


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    rows, failures = [], []
    for key, t in TARGETS.items():
        try:
            links = find_links(t["page"], t["pattern"])
            if not links:
                raise RuntimeError("no se encontró enlace que calce con el patrón")
            path = download(links[0])
            rows.append((key, path, links[0], "descarga automática"))
            continue
        except Exception as e:  # red bloqueada, cambio de sitio, etc.
            failures.append((key, t["page"], f"{type(e).__name__}: {e}"))
        path = manual_file(key)
        if path:
            rows.append((key, path, "carga manual por el usuario (origen declarado: "
                         f"{t['page']})", "manual"))

    with SOURCES.open("a", encoding="utf-8") as f:
        f.write(f"\n## Ejecución {dt.datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write("| Clave | Archivo | URL / origen | Modo | Fecha registro | Bytes | SHA-256 |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for key, path, url, mode in rows:
            f.write(f"| {key} | {path.name} | {url} | {mode} | {TODAY} | "
                    f"{path.stat().st_size} | {sha256(path)} |\n")
        if failures:
            f.write("\nIntentos de descarga fallidos:\n\n")
            for key, page, err in failures:
                f.write(f"- {key}: {page} → {err}\n")

    got = {r[0] for r in rows}
    missing = [k for k in TARGETS if k not in got]
    for key, page, err in failures:
        print(f"[FALLO] {key}: {page}\n        {err}")
    for key, path, url, mode in rows:
        print(f"[OK]    {key}: {path.name} ({mode})")
    if missing:
        print("\nFaltan archivos: " + ", ".join(missing)
              + f"\nDéjelos en {RAW} y vuelva a ejecutar.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
