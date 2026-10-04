#!/usr/bin/env python3
"""Extrai o texto dos três PDFs de origem (assets/) para arquivos .txt.

Uso:
    python extract_sources.py --out-dir <diretório de trabalho>

Grava, no diretório indicado:
    cv_base.txt    texto do "CV - MARCELO TOMIO HAMA.pdf" (modelo de formato e de tom)
    linkedin.txt   texto do "LinkedInProfile.pdf" (conteúdo profissional completo)
    lattes.txt     texto do "Lattes.pdf" (conteúdo acadêmico completo)

Usa o `pdftotext` (poppler) quando existe, porque ele separa melhor as colunas;
sem ele, usa pypdf (`pip install pypdf`). A extração é refeita a cada execução,
então basta trocar um PDF em assets/ por uma versão mais nova para a skill
passar a usar o conteúdo atualizado.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

FONTES = {
    "cv_base.txt": "CV - MARCELO TOMIO HAMA.pdf",
    "linkedin.txt": "LinkedInProfile.pdf",
    "lattes.txt": "Lattes.pdf",
}


def via_pdftotext(pdf: Path) -> str:
    out = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
        capture_output=True, check=True,
    )
    return out.stdout.decode("utf-8", errors="replace")


def via_pypdf(pdf: Path) -> str:
    from pypdf import PdfReader

    paginas = []
    for pagina in PdfReader(str(pdf)).pages:
        texto = pagina.extract_text() or ""
        # O CV base (Google Docs) sai com espaços duplos entre as palavras.
        paginas.append("\n".join(" ".join(l.split()) for l in texto.splitlines()))
    return "\n\n".join(paginas)


def extrair(pdf: Path) -> str:
    if shutil.which("pdftotext"):
        try:
            return via_pdftotext(pdf)
        except (subprocess.CalledProcessError, OSError):
            pass
    try:
        return via_pypdf(pdf)
    except ImportError:
        sys.exit("ERRO: instale o pypdf (pip install pypdf) ou o poppler (pdftotext).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-dir", default=".", help="onde gravar os .txt (padrão: diretório atual)")
    args = ap.parse_args()

    destino = Path(args.out_dir)
    destino.mkdir(parents=True, exist_ok=True)

    faltando = [nome for nome in FONTES.values() if not (ASSETS / nome).exists()]
    if faltando:
        sys.exit("ERRO: não encontrei em assets/: " + ", ".join(faltando))

    for txt, pdf in FONTES.items():
        texto = extrair(ASSETS / pdf)
        # Zero-width space que o Google Docs põe depois de cada marcador.
        texto = texto.replace("​", "")
        (destino / txt).write_text(texto, encoding="utf-8")
        palavras = len(texto.split())
        aviso = "  <- pouco texto: confira se o PDF é digitalizado" if palavras < 150 else ""
        print(f"{destino / txt}  ({palavras} palavras, de {pdf}){aviso}")


if __name__ == "__main__":
    main()
