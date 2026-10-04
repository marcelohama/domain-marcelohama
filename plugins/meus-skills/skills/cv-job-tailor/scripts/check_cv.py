#!/usr/bin/env python3
"""Confere se o PDF do CV é lido corretamente por filtros automáticos e IAs.

Uso:
    python check_cv.py <cv.pdf> --spec <spec.json> [--dump-text]

Extrai o texto do PDF como um ATS faria e confere, contra o spec:
    - texto extraível, sem imagens e sem caracteres quebrados;
    - contato no começo do documento;
    - seções presentes e experiências na ordem certa, com cada marcador
      dentro da experiência a que pertence (colunas não se misturam);
    - períodos em formato que parsers de data reconhecem;
    - cobertura das palavras-chave da vaga (spec: vaga.palavras_chave);
    - número de páginas e de palavras.

Sai com código 1 se houver algum ERRO. AVISO pede uma decisão, não um conserto
obrigatório. Com --dump-text grava <cv>.txt com o texto extraído, que serve
para colar em formulários de candidatura.

Dependência: pip install pypdf reportlab   (pdftotext, do poppler, é opcional)
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_cv import ErroDeSpec, carregar, limpar, simples  # noqa: E402

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("ERRO: instale o pypdf (pip install pypdf).")

MESES = (
    "jan|january|janeiro|enero|ene|feb|february|fev|fevereiro|febrero|mar|march|março|marzo|"
    "apr|april|abr|abril|may|mai|maio|mayo|jun|june|junho|junio|jul|july|julho|julio|"
    "aug|august|ago|agosto|sep|sept|september|set|setembro|septiembre|oct|october|out|outubro|octubre|"
    "nov|november|novembro|noviembre|dec|december|dez|dezembro|dic|diciembre"
)
DATA = rf"(?:(?:{MESES})\.? \d{{4}}|\d{{2}}/\d{{4}}|\d{{4}})"
HOJE = r"(?:present|current|now|atual|atualmente|presente|actual|actualidad)"
PERIODO = re.compile(rf"^{DATA}(?: - (?:{DATA}|{HOJE}))?$", re.IGNORECASE)


def norm(texto):
    """Minúsculas, sem acentos, espaços colapsados: comparação tolerante."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.lower().split())


def extrair_pypdf(pdf):
    leitor = PdfReader(str(pdf))
    paginas = [(p.extract_text() or "") for p in leitor.pages]
    imagens = 0
    for p in leitor.pages:
        try:
            imagens += len(list(p.images))
        except Exception:
            pass
    return leitor, "\n".join(paginas), imagens


def extrair_pdftotext(pdf, *opcoes):
    if not shutil.which("pdftotext"):
        return None
    try:
        out = subprocess.run(["pdftotext", "-enc", "UTF-8", *opcoes, str(pdf), "-"],
                             capture_output=True, check=True)
        return out.stdout.decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, OSError):
        return None


def ordem_das_experiencias(texto, spec):
    """Devolve a lista de problemas de ordem de leitura encontrados em `texto`."""
    t = norm(texto)
    problemas = []
    posicoes = []
    cursor = 0
    for e in spec["experiencias"]:
        cabeca = norm(" | ".join(x for x in (simples(e["cargo"]), simples(e["empresa"]), e["periodo"]) if x))
        pos = t.find(cabeca, cursor)
        if pos < 0:
            # A linha pode ter quebrado no meio; tenta só cargo + empresa.
            curto = norm(" | ".join(x for x in (simples(e["cargo"]), simples(e["empresa"])) if x))
            pos = t.find(curto, cursor)
        if pos < 0:
            problemas.append(f"não achei, na ordem esperada, a experiência '{e['cargo']} | {e['empresa']}'")
            posicoes.append(None)
            continue
        posicoes.append(pos)
        cursor = pos + 1
    for i, e in enumerate(spec["experiencias"]):
        if posicoes[i] is None:
            continue
        fim = next((p for p in posicoes[i + 1:] if p is not None), len(t))
        for item in e["itens"]:
            trecho = norm(simples(item))[:45]
            pos = t.find(trecho)
            if pos < 0:
                problemas.append(f"marcador não encontrado inteiro: '{simples(item)[:50]}...'")
            elif not posicoes[i] < pos < fim:
                problemas.append(f"marcador fora da sua experiência: '{simples(item)[:50]}...'")
    return problemas


def main():
    ap = argparse.ArgumentParser(description="Confere a leitura do CV por filtros automáticos.")
    ap.add_argument("pdf")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--dump-text", action="store_true", help="grava <cv>.txt com o texto extraído")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        sys.exit(f"ERRO: não encontrei {pdf}")
    try:
        spec = carregar(args.spec)
    except ErroDeSpec as e:
        sys.exit(f"ERRO: {e}")
    bruto = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    vaga = bruto.get("vaga") or {}

    erros, avisos, oks = [], [], []
    leitor, texto, imagens = extrair_pypdf(pdf)
    t = norm(texto)
    paginas = len(leitor.pages)
    palavras = len(texto.split())

    # 1. Texto extraível
    if palavras < 150:
        erros.append(f"só {palavras} palavras extraídas: o PDF não tem texto legível por máquina")
    else:
        oks.append(f"texto extraível ({palavras} palavras)")
    if "�" in texto or "(cid:" in texto:
        erros.append("há caracteres que não foram extraídos como texto (aparecem como lixo)")
    if "**" in texto:
        erros.append("sobrou marcação ** no texto: confira asteriscos sem par no spec")
    if imagens:
        avisos.append(f"{imagens} imagem(ns) no PDF: texto dentro de imagem não é lido por ATS")

    # 2. Páginas
    if paginas == 1:
        oks.append("1 página")
    elif paginas == 2:
        avisos.append("2 páginas: aceitável, mas o alvo é 1; veja se há o que cortar")
    else:
        erros.append(f"{paginas} páginas: reduza para 1, no máximo 2")
    if palavras > 950:
        avisos.append(f"{palavras} palavras: texto longo dilui as palavras-chave; corte o que não serve à vaga")

    # 3. Contato no começo
    inicio = norm(texto[:700])
    email = norm(spec["contato"]["email"])
    if email in inicio:
        oks.append("e-mail no começo do documento")
    elif email in t:
        avisos.append("o e-mail aparece, mas não no começo do texto extraído")
    else:
        erros.append("e-mail não encontrado no texto extraído")
    fone = re.sub(r"\D", "", spec["contato"]["telefone"])
    if fone and fone not in re.sub(r"\D", "", texto[:700]):
        avisos.append("telefone não aparece no começo do texto extraído")
    if norm(spec["nome"]) not in norm(texto[:200]):
        erros.append("o nome não é a primeira coisa lida no documento")

    # 4. Seções
    rot = spec["rotulos"]
    esperadas = [("resumo", True), ("competencias", bool(spec["competencias"])), ("experiencias", True),
                 ("formacao", bool(spec["formacao"])), ("certificacoes", bool(spec["certificacoes"])),
                 ("idiomas", bool(spec["idiomas"]))]
    faltam = [rot[k] for k, usada in esperadas if usada and norm(rot[k]) not in t]
    if faltam:
        erros.append("título(s) de seção ausente(s) no texto: " + ", ".join(faltam))
    else:
        oks.append("títulos de seção presentes")
    if not spec["formacao"]:
        avisos.append("sem seção de formação: a maioria dos filtros exige")

    # 5. Ordem de leitura
    problemas = ordem_das_experiencias(texto, spec)
    if problemas:
        erros.append("ordem de leitura (texto na ordem do arquivo): " + "; ".join(problemas[:4]))
    else:
        oks.append("experiências e marcadores na ordem certa (leitura na ordem do arquivo)")
    fluxo = extrair_pdftotext(pdf)
    if fluxo is not None:
        p = ordem_das_experiencias(fluxo, spec)
        if p:
            avisos.append("leitura com detecção de colunas (pdftotext): " + "; ".join(p[:3]))
        else:
            oks.append("experiências e marcadores na ordem certa (leitura com detecção de colunas)")
    linhas = extrair_pdftotext(pdf, "-layout")
    if linhas is not None:
        p = ordem_das_experiencias(linhas, spec)
        if not p:
            oks.append("experiências e marcadores na ordem certa (leitura linha a linha)")
        elif spec["layout"] == "classico":
            avisos.append("leitura linha a linha mistura as duas colunas (esperado no layout classico); "
                          "para envio por portal de vagas, gere com o layout ats")
        else:
            avisos.append("leitura linha a linha (pdftotext -layout): " + "; ".join(p[:3]))

    # 6. Períodos
    ruins = []
    for grupo in ("experiencias", "formacao"):
        for x in spec[grupo]:
            if x["periodo"] and not PERIODO.match(x["periodo"]):
                ruins.append(x["periodo"])
    if ruins:
        avisos.append("período(s) fora do padrão 'Mon YYYY - Mon YYYY': " + "; ".join(ruins)
                      + " (parsers de data podem não calcular o tempo de experiência)")
    else:
        oks.append("períodos em formato reconhecível")

    # 7. Palavras-chave da vaga
    chaves = [limpar(k, "vaga.palavras_chave", []) for k in (vaga.get("palavras_chave") or []) if isinstance(k, str)]
    if chaves:
        presentes = [k for k in chaves if norm(k) in t]
        ausentes = [k for k in chaves if norm(k) not in t]
        oks.append(f"palavras-chave da vaga no CV: {len(presentes)}/{len(chaves)}")
        if ausentes:
            avisos.append("palavras-chave ausentes: " + ", ".join(ausentes)
                          + ". Se há evidência nas fontes, use o termo exato da vaga; se não há, "
                            "é lacuna real: deixe fora e relate ao usuário")
    else:
        avisos.append("o spec não tem vaga.palavras_chave: sem isso não dá para medir a cobertura da vaga")

    for m in oks:
        print("OK:    " + m)
    for m in avisos:
        print("AVISO: " + m)
    for m in erros:
        print("ERRO:  " + m)
    print(f"\nResumo: {len(erros)} erro(s), {len(avisos)} aviso(s), {paginas} página(s), {palavras} palavras.")

    if args.dump_text:
        saida = pdf.with_suffix(".txt")
        saida.write_text(fluxo if fluxo is not None else texto, encoding="utf-8")
        print(f"Texto extraído: {saida}")

    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
