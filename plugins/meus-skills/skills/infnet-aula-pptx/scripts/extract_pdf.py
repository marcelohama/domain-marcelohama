#!/usr/bin/env python3
"""Extrai o texto de um ou mais PDFs, página por página, para arquivos .txt.

    python extract_pdf.py livro.pdf capitulo.pdf [--out-dir DIR]

Cada PDF gera <nome>.txt em DIR (padrão: diretório atual), com marcas "=== página N ===".
Páginas sem texto (PDF digitalizado) são listadas ao final: leia-as como imagem.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def pages_pypdf(path):
    from pypdf import PdfReader
    return [(p.extract_text() or "") for p in PdfReader(str(path)).pages]


def pages_pdftotext(path):
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, check=True)
    pages = out.stdout.decode("utf-8", errors="replace").split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages


def extract(path):
    try:
        return pages_pypdf(path)
    except ImportError:
        if shutil.which("pdftotext"):
            return pages_pdftotext(path)
        raise SystemExit("Instale o pypdf (pip install pypdf) ou o pdftotext (Poppler).")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    status = 0
    for name in a.pdfs:
        path = Path(name)
        if not path.is_file():
            print(f"NÃO ENCONTRADO: {path}")
            status = 1
            continue
        pages = extract(path)
        empty = [i for i, t in enumerate(pages, 1) if len(t.strip()) < 20]
        dest = out_dir / (path.stem + ".txt")
        dest.write_text("".join(f"\n=== página {i} ===\n{t}\n" for i, t in enumerate(pages, 1)), encoding="utf-8")
        chars = sum(len(t) for t in pages)
        print(f"{path.name}: {len(pages)} páginas, {chars} caracteres -> {dest}")
        if empty:
            print(f"  páginas sem texto (leia como imagem): {empty}")
    return status


if __name__ == "__main__":
    sys.exit(main())
