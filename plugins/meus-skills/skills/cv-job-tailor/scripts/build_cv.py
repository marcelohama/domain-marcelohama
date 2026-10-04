#!/usr/bin/env python3
"""Monta o CV em PDF a partir de uma especificação JSON.

Uso:
    python build_cv.py <spec.json> [--out-dir DIR] [--layout ats|classico]

O visual segue o "CV - MARCELO TOMIO HAMA.pdf": nome em azul sobre um fio preto,
títulos de seção em caixa alta, linha de cargo em azul e marcadores com hífen.

Dois layouts:
    ats       (padrão) uma coluna. Qualquer extrator de texto lê o arquivo na
              ordem certa, que é o que filtros automáticos e IAs precisam.
    classico  duas colunas, como o CV base. Para quando o PDF vai direto para
              uma pessoa; extratores que leem "por linha" misturam as colunas.

O PDF sai com texto real (sem imagens nem tabelas), fontes padrão, metadados
preenchidos e o texto gravado na ordem de leitura. O formato do spec está em
references/exemplo_spec.json e é explicado no SKILL.md.

Dependência: pip install reportlab
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from reportlab.lib.colors import HexColor, black
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Frame, HRFlowable, Paragraph
except ImportError:
    sys.exit("ERRO: instale o reportlab (pip install reportlab).")

AZUL_HEX = "#1155CC"
AZUL = HexColor(AZUL_HEX)
LARGURA, ALTURA = A4

ROTULOS = {
    "en": {
        "resumo": "SUMMARY", "competencias": "SKILLS",
        "experiencias": "PROFESSIONAL EXPERIENCE", "formacao": "EDUCATION",
        "certificacoes": "CERTIFICATIONS", "idiomas": "LANGUAGES",
        "telefone": "Phone", "assunto": "Resume", "lang": "en-US",
    },
    "pt": {
        "resumo": "RESUMO", "competencias": "COMPETÊNCIAS",
        "experiencias": "EXPERIÊNCIA PROFISSIONAL", "formacao": "FORMAÇÃO ACADÊMICA",
        "certificacoes": "CERTIFICAÇÕES", "idiomas": "IDIOMAS",
        "telefone": "Telefone", "assunto": "Currículo", "lang": "pt-BR",
    },
    "es": {
        "resumo": "RESUMEN", "competencias": "COMPETENCIAS",
        "experiencias": "EXPERIENCIA PROFESIONAL", "formacao": "FORMACIÓN ACADÉMICA",
        "certificacoes": "CERTIFICACIONES", "idiomas": "IDIOMAS",
        "telefone": "Teléfono", "assunto": "Currículum", "lang": "es",
    },
}

# Caracteres tipográficos que alguns extratores devolvem como lixo, trocados
# por equivalentes simples. Um parser que quebra um travessão quebra a data.
TROCAS = {
    "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-",
    "•": "-", "▪": "-", "●": "-", "‣": "-",
    "→": "->", "⇒": "->", "←": "<-",
    "≥": ">=", "≤": "<=", "≈": "~",
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "…": "...",
    " ": " ", " ": " ", " ": " ", " ": " ",
    "​": "", "‌": "", "‍": "", "﻿": "", "⁠": "",
}


class ErroDeSpec(Exception):
    pass


# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------

def limpar(texto, onde, erros):
    """Normaliza o texto e confere se cabe nas fontes padrão (cp1252)."""
    if not isinstance(texto, str):
        erros.append(f"{onde}: esperava texto, veio {type(texto).__name__}")
        return ""
    for de, para in TROCAS.items():
        texto = texto.replace(de, para)
    texto = " ".join(texto.split())
    try:
        texto.encode("cp1252")
    except UnicodeEncodeError:
        ruins = sorted({c for c in texto if not _cp1252(c)})
        erros.append(
            f"{onde}: caractere(s) fora do conjunto suportado: "
            + " ".join(f"{c!r}" for c in ruins)
            + " (troque por texto simples)"
        )
    return texto


def _cp1252(c):
    try:
        c.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def rico(texto):
    """Escapa o texto e converte **negrito** em <b>."""
    texto = escape(texto)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


def simples(texto):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", texto)


def azul(marcacao):
    return f'<font color="{AZUL_HEX}">{marcacao}</font>'


def link(texto_marcado, url):
    return f'<a href="{escape(url, {chr(34): "&quot;"})}" color="{AZUL_HEX}"><u>{texto_marcado}</u></a>'


def juntar(partes, sep=" | "):
    return sep.join(p for p in partes if p)


# --------------------------------------------------------------------------
# Leitura e validação do spec
# --------------------------------------------------------------------------

def carregar(caminho):
    try:
        bruto = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ErroDeSpec(f"não consegui ler {caminho}: {e}")
    if not isinstance(bruto, dict):
        raise ErroDeSpec("o spec precisa ser um objeto JSON")

    erros = []

    def t(valor, onde, obrigatorio=False):
        if valor is None or valor == "":
            if obrigatorio:
                erros.append(f"{onde}: campo obrigatório")
            return ""
        return limpar(valor, onde, erros)

    def lista(valor, onde):
        if valor is None:
            return []
        if not isinstance(valor, list):
            erros.append(f"{onde}: esperava uma lista")
            return []
        return valor

    idioma = bruto.get("idioma", "en")
    if idioma not in ROTULOS:
        erros.append(f"idioma: use um de {sorted(ROTULOS)}")
        idioma = "en"
    layout = bruto.get("layout", "ats")
    densidade = bruto.get("densidade", "normal")
    if densidade not in ("normal", "compacta"):
        erros.append("densidade: use 'normal' ou 'compacta'")

    contato = bruto.get("contato") or {}
    spec = {
        "idioma": idioma,
        "layout": layout,
        "densidade": densidade,
        "arquivo": bruto.get("arquivo") or "CV - MARCELO TOMIO HAMA.pdf",
        "nome": t(bruto.get("nome"), "nome", True),
        "titulo": t(bruto.get("titulo"), "titulo", True),
        "contato": {
            "telefone": t(contato.get("telefone"), "contato.telefone"),
            "email": t(contato.get("email"), "contato.email", True),
            "linkedin": t(contato.get("linkedin"), "contato.linkedin"),
            "local": t(contato.get("local"), "contato.local"),
        },
        "resumo": t(bruto.get("resumo"), "resumo", True),
        "competencias": [],
        "experiencias": [],
        "formacao": [],
        "certificacoes": [],
        "idiomas": [],
        "secoes_extras": [],
        "rotulos": dict(ROTULOS[idioma]),
    }

    for chave, valor in (bruto.get("rotulos") or {}).items():
        if chave in ("resumo", "competencias", "experiencias", "formacao", "certificacoes", "idiomas"):
            spec["rotulos"][chave] = t(valor, f"rotulos.{chave}")

    for i, c in enumerate(lista(bruto.get("competencias"), "competencias")):
        onde = f"competencias[{i}]"
        if isinstance(c, dict):
            itens = [t(x, f"{onde}.itens") for x in lista(c.get("itens"), f"{onde}.itens")]
            spec["competencias"].append({"grupo": t(c.get("grupo"), f"{onde}.grupo"), "itens": [x for x in itens if x]})
        else:
            spec["competencias"].append({"grupo": "", "itens": [t(c, onde)]})

    exps = lista(bruto.get("experiencias"), "experiencias")
    if not exps:
        erros.append("experiencias: inclua ao menos uma")
    for i, e in enumerate(exps):
        onde = f"experiencias[{i}]"
        if not isinstance(e, dict):
            erros.append(f"{onde}: esperava um objeto")
            continue
        itens = [t(x, f"{onde}.itens") for x in lista(e.get("itens"), f"{onde}.itens")]
        spec["experiencias"].append({
            "cargo": t(e.get("cargo"), f"{onde}.cargo", True),
            "empresa": t(e.get("empresa"), f"{onde}.empresa"),
            "periodo": t(e.get("periodo"), f"{onde}.periodo", True),
            "local": t(e.get("local"), f"{onde}.local"),
            "itens": [x for x in itens if x],
        })

    for i, f in enumerate(lista(bruto.get("formacao"), "formacao")):
        onde = f"formacao[{i}]"
        if not isinstance(f, dict):
            erros.append(f"{onde}: esperava um objeto")
            continue
        spec["formacao"].append({
            "curso": t(f.get("curso"), f"{onde}.curso", True),
            "instituicao": t(f.get("instituicao"), f"{onde}.instituicao", True),
            "periodo": t(f.get("periodo"), f"{onde}.periodo"),
            "local": t(f.get("local"), f"{onde}.local"),
        })

    for i, c in enumerate(lista(bruto.get("certificacoes"), "certificacoes")):
        onde = f"certificacoes[{i}]"
        if not isinstance(c, dict):
            erros.append(f"{onde}: esperava um objeto")
            continue
        spec["certificacoes"].append({
            "nome": t(c.get("nome"), f"{onde}.nome", True),
            "emissor": t(c.get("emissor"), f"{onde}.emissor"),
            "ano": t(str(c["ano"]) if c.get("ano") else "", f"{onde}.ano"),
            "url": (c.get("url") or "").strip(),
        })

    for i, l in enumerate(lista(bruto.get("idiomas"), "idiomas")):
        onde = f"idiomas[{i}]"
        if not isinstance(l, dict):
            erros.append(f"{onde}: esperava um objeto")
            continue
        spec["idiomas"].append({
            "idioma": t(l.get("idioma"), f"{onde}.idioma", True),
            "nivel": t(l.get("nivel"), f"{onde}.nivel", True),
        })

    for i, s in enumerate(lista(bruto.get("secoes_extras"), "secoes_extras")):
        onde = f"secoes_extras[{i}]"
        if not isinstance(s, dict):
            erros.append(f"{onde}: esperava um objeto")
            continue
        itens = [t(x, f"{onde}.itens") for x in lista(s.get("itens"), f"{onde}.itens")]
        coluna = s.get("coluna", "direita")
        if coluna not in ("direita", "esquerda"):
            erros.append(f"{onde}.coluna: use 'direita' ou 'esquerda'")
        spec["secoes_extras"].append({
            "titulo": t(s.get("titulo"), f"{onde}.titulo", True).upper(),
            "itens": [x for x in itens if x],
            "coluna": coluna,
        })

    if erros:
        raise ErroDeSpec("spec inválido:\n  - " + "\n  - ".join(erros))
    return spec


# --------------------------------------------------------------------------
# Estilos e blocos
# --------------------------------------------------------------------------

def estilos(densidade, layout):
    corpo, entrelinha = (9.2, 11.5) if densidade == "normal" else (8.7, 10.8)
    if layout == "classico":
        corpo, entrelinha = corpo - 0.2, entrelinha - 0.1
    base = ParagraphStyle("base", fontName="Helvetica", fontSize=corpo, leading=entrelinha, textColor=black)
    antes_secao = 8 if densidade == "normal" else 6
    return {
        "corpo": base,
        "entrelinha": entrelinha,
        "nome": ParagraphStyle("nome", parent=base, fontName="Helvetica-Bold", fontSize=23,
                               leading=27, textColor=AZUL),
        "titulo": ParagraphStyle("titulo", parent=base, fontName="Helvetica-Bold",
                                 fontSize=corpo + 2, leading=entrelinha + 3),
        "contato": ParagraphStyle("contato", parent=base, spaceAfter=1),
        "contato_forte": ParagraphStyle("contato_forte", parent=base, fontName="Helvetica-Bold",
                                        fontSize=corpo + 1.4, leading=entrelinha + 3),
        "secao": ParagraphStyle("secao", parent=base, fontName="Helvetica-Bold", fontSize=corpo + 1.2,
                                leading=entrelinha + 1.5, spaceBefore=antes_secao, spaceAfter=1),
        "resumo": ParagraphStyle("resumo", parent=base, alignment=TA_JUSTIFY),
        "cargo": ParagraphStyle("cargo", parent=base, textColor=AZUL, spaceBefore=3),
        "item": ParagraphStyle("item", parent=base, leftIndent=20, bulletIndent=9,
                               bulletFontName="Helvetica", bulletFontSize=corpo),
        "item_curto": ParagraphStyle("item_curto", parent=base, leftIndent=9, bulletIndent=0,
                                     bulletFontName="Helvetica", bulletFontSize=corpo),
        "linha": ParagraphStyle("linha", parent=base, spaceBefore=1.5),
    }


def P(marcacao, estilo, manter=False, marcador=None):
    p = Paragraph(marcacao, estilo, bulletText=marcador)
    p.manter_com_proximo = manter
    return p


def fio(espessura, antes, depois, largura="100%"):
    return HRFlowable(width=largura, thickness=espessura, color=black, spaceBefore=antes,
                      spaceAfter=depois, hAlign="LEFT")


def url_linkedin(valor):
    return valor if valor.startswith("http") else "https://" + valor.removeprefix("www.")


def bloco_resumo(spec, st):
    return [P(spec["rotulos"]["resumo"], st["secao"], manter=True), P(rico(spec["resumo"]), st["resumo"])]


def bloco_competencias(spec, st):
    if not spec["competencias"]:
        return []
    out = [P(rico(spec["rotulos"]["competencias"]), st["secao"], manter=True)]
    soltas = [i for c in spec["competencias"] if not c["grupo"] for i in c["itens"]]
    if soltas:
        out.append(P(rico(", ".join(soltas)), st["corpo"]))
    for c in spec["competencias"]:
        if c["grupo"] and c["itens"]:
            out.append(P(f"<b>{rico(c['grupo'])}:</b> {rico(', '.join(c['itens']))}", st["corpo"]))
    return out


def bloco_experiencias(spec, st):
    out = [P(rico(spec["rotulos"]["experiencias"]), st["secao"], manter=True)]
    for e in spec["experiencias"]:
        cabeca = juntar([
            f"<b>{rico(e['cargo'])}</b>",
            f"<b>{rico(e['empresa'])}</b>" if e["empresa"] else "",
            rico(e["periodo"]),
            rico(e["local"]),
        ])
        out.append(P(cabeca, st["cargo"], manter=bool(e["itens"])))
        for item in e["itens"]:
            out.append(P(rico(item), st["item"], marcador="-"))
    return out


def bloco_formacao(spec, st, estreito):
    if not spec["formacao"]:
        return []
    out = [P(rico(spec["rotulos"]["formacao"]), st["secao"], manter=True)]
    for f in spec["formacao"]:
        curso = azul(f"<b>{rico(f['curso'])}</b>")
        if estreito:
            resto = juntar([rico(f["instituicao"]), rico(f["periodo"]), rico(f["local"])], ", ")
            out.append(P(f"{curso}<br/>{resto}", st["linha"]))
        else:
            out.append(P(juntar([curso, rico(f["instituicao"]), rico(f["periodo"]), rico(f["local"])]), st["linha"]))
    return out


def bloco_certificacoes(spec, st, estreito):
    if not spec["certificacoes"]:
        return []
    out = [P(rico(spec["rotulos"]["certificacoes"]), st["secao"], manter=True)]
    for c in spec["certificacoes"]:
        nome = f"<b>{rico(c['nome'])}</b>"
        nome = link(nome, c["url"]) if c["url"] else azul(nome) if estreito else nome
        texto = juntar([nome, rico(c["emissor"]), rico(c["ano"])], ", " if estreito else " | ")
        out.append(P(texto, st["item_curto"] if estreito else st["item"], marcador="-"))
    return out


def bloco_idiomas(spec, st, estreito):
    if not spec["idiomas"]:
        return []
    out = [P(rico(spec["rotulos"]["idiomas"]), st["secao"], manter=True)]
    for l in spec["idiomas"]:
        nome = azul(f"<b>{rico(l['idioma'])}</b>")
        sep = "<br/>" if estreito else ": "
        out.append(P(f"{nome}{sep}{rico(l['nivel'])}", st["linha"]))
    return out


def bloco_extra(secao, st, estreito):
    out = [P(rico(secao["titulo"]), st["secao"], manter=True)]
    for item in secao["itens"]:
        out.append(P(rico(item), st["item_curto"] if estreito else st["item"], marcador="-"))
    return out


# --------------------------------------------------------------------------
# Diagramação
# --------------------------------------------------------------------------

def altura(f, largura):
    return f.wrap(largura, 10 ** 6)[1]


def cabe_grupo(story, moldura, entrelinha):
    """Um título só fica na página se couber com o começo do que ele anuncia."""
    precisa, i = 0.0, 0
    while i < len(story) and getattr(story[i], "manter_com_proximo", False):
        precisa += altura(story[i], moldura._aW) + story[i].getSpaceBefore() + story[i].getSpaceAfter()
        i += 1
    if i < len(story):
        precisa += min(altura(story[i], moldura._aW), 2 * entrelinha) + story[i].getSpaceBefore()
    return precisa <= moldura._y - moldura._y1p


def diagramar(canv, novas_molduras, segmentos, entrelinha, limite=12):
    pagina = 1
    while True:
        molduras = novas_molduras(pagina)
        for chave, story in segmentos:
            m = molduras[chave]
            while story:
                f = story[0]
                if getattr(f, "manter_com_proximo", False) and not m._atTop and not cabe_grupo(story, m, entrelinha):
                    break
                if m.add(f, canv):
                    story.pop(0)
                    continue
                partes = m.split(f, canv)
                if len(partes) > 1 and m.add(partes[0], canv):
                    story[0:1] = partes[1:]
                elif m._atTop:
                    raise ErroDeSpec("há um bloco que não cabe nem em uma coluna vazia; encurte o texto")
                break
        if not any(story for _, story in segmentos):
            return pagina, molduras
        canv.showPage()
        pagina += 1
        if pagina > limite:
            raise ErroDeSpec(f"o conteúdo passou de {limite} páginas; algo está errado no spec")


def montar(spec, destino):
    layout = spec["layout"]
    st = estilos(spec["densidade"], layout)
    rot = spec["rotulos"]
    ct = spec["contato"]
    estreito = layout == "classico"

    competencias_planas = [i for c in spec["competencias"] for i in c["itens"]]
    canv = Canvas(str(destino), pagesize=A4, lang=rot["lang"], pageCompression=1)
    canv.setTitle(f"{spec['nome']} - {spec['titulo']} - CV")
    canv.setAuthor(spec["nome"].title())
    canv.setSubject(rot["assunto"])
    canv.setKeywords(", ".join(simples(i) for i in competencias_planas[:40]))
    canv.setCreator(spec["nome"].title())

    email = link(rico(ct["email"]), "mailto:" + ct["email"])
    linkedin = link(rico(ct["linkedin"]), url_linkedin(ct["linkedin"])) if ct["linkedin"] else ""
    telefone = f"{rot['telefone']}: {rico(ct['telefone'])}" if ct["telefone"] else ""

    extras_dir = [s for s in spec["secoes_extras"] if s["coluna"] == "direita"]
    extras_esq = [s for s in spec["secoes_extras"] if s["coluna"] == "esquerda"]

    if layout == "ats":
        me, md, mt, mb = 42, 42, 36, 34
        story = [
            P(rico(spec["nome"]), st["nome"]),
            fio(1.4, 2, 7),
            P(rico(spec["titulo"]), st["titulo"]),
            P(juntar([telefone, email, linkedin, rico(ct["local"])]), st["contato"]),
        ]
        story += bloco_resumo(spec, st)
        story += bloco_competencias(spec, st)
        story += bloco_experiencias(spec, st)
        for s in extras_esq:
            story += bloco_extra(s, st, False)
        story += bloco_formacao(spec, st, False)
        story += bloco_certificacoes(spec, st, False)
        story += bloco_idiomas(spec, st, False)
        for s in extras_dir:
            story += bloco_extra(s, st, False)
        segmentos = [("c", story)]

        def novas_molduras(pagina):
            return {"c": Frame(me, mb, LARGURA - me - md, ALTURA - mt - mb, 0, 0, 0, 0)}

    elif layout == "classico":
        me, md, mt, mb, vao = 50, 46, 44, 40, 18
        util = LARGURA - me - md
        larg_e = round(util * 0.655)
        larg_d = util - larg_e - vao
        cabecalho = [P(rico(spec["nome"]), st["nome"]), fio(1.4, 2, 6)]
        alt_cab = sum(altura(f, util) + f.getSpaceBefore() + f.getSpaceAfter() for f in cabecalho) + 4

        # Contato primeiro no arquivo: quem lê o PDF na ordem em que foi gravado
        # encontra nome, título e contato antes do resto, como no layout ats.
        seg_contato = [P(rico(spec["titulo"]), st["contato_forte"])]
        if telefone:
            seg_contato.append(P(f"<b>{telefone}</b>", st["contato"]))
        seg_contato.append(P(email, st["contato"]))
        if linkedin:
            seg_contato.append(P(linkedin, st["contato"]))
        if ct["local"]:
            seg_contato.append(P(rico(ct["local"]), st["contato"]))

        esquerda = bloco_resumo(spec, st) + bloco_experiencias(spec, st)
        for s in extras_esq:
            esquerda += bloco_extra(s, st, False)
        esquerda += bloco_competencias(spec, st)

        direita = []
        for bloco in (
            bloco_formacao(spec, st, True),
            bloco_idiomas(spec, st, True),
            bloco_certificacoes(spec, st, True),
            *[bloco_extra(s, st, True) for s in extras_dir],
        ):
            if bloco:
                direita += [fio(0.8, 9, 0, "75%")] + bloco
        segmentos = [("d", seg_contato), ("e", esquerda), ("d", direita)]

        def novas_molduras(pagina):
            topo = ALTURA - mt
            if pagina == 1:
                cab = Frame(me, topo - alt_cab, util, alt_cab, 0, 0, 0, 0)
                for f in cabecalho:
                    cab.add(f, canv)
                topo -= alt_cab
            return {
                "e": Frame(me, mb, larg_e, topo - mb, 0, 0, 0, 0),
                "d": Frame(me + larg_e + vao, mb, larg_d, topo - mb, 0, 0, 0, 0),
            }
    else:
        raise ErroDeSpec("layout: use 'ats' ou 'classico'")

    paginas, molduras = diagramar(canv, novas_molduras, segmentos, st["entrelinha"])
    canv.save()

    # Ocupação da última página: vale a coluna mais cheia.
    usos = [(m._aH - (m._y - m._y1p), m._aH) for m in molduras.values()]
    alt_usada, alt_total = max(usos, key=lambda u: u[0] / u[1])
    return paginas, alt_usada, alt_total, st["entrelinha"]


def nome_seguro(nome):
    nome = re.sub(r'[\\/:*?"<>|]+', " ", nome).strip()
    nome = " ".join(nome.split())
    return nome if nome.lower().endswith(".pdf") else nome + ".pdf"


def main():
    ap = argparse.ArgumentParser(description="Monta o CV em PDF a partir de um spec JSON.")
    ap.add_argument("spec")
    ap.add_argument("--out-dir", default=".", help="pasta de saída (padrão: diretório atual)")
    ap.add_argument("--layout", choices=["ats", "classico"], help="sobrepõe o layout do spec")
    args = ap.parse_args()

    try:
        spec = carregar(args.spec)
        if args.layout:
            spec["layout"] = args.layout
        destino = Path(args.out_dir)
        destino.mkdir(parents=True, exist_ok=True)
        arquivo = destino / nome_seguro(spec["arquivo"])
        paginas, usada, total, entrelinha = montar(spec, arquivo)
    except ErroDeSpec as e:
        sys.exit(f"ERRO: {e}")

    print(f"PDF: {arquivo.resolve()}")
    print(f"Layout: {spec['layout']} | densidade: {spec['densidade']} | páginas: {paginas}")
    ocupacao = round(100 * usada / total)
    if paginas == 1:
        sobra = math.floor((total - usada) / entrelinha)
        print(f"Ocupação da página: {ocupacao}% (cabem mais ~{sobra} linhas)")
    else:
        linhas = math.ceil(usada / entrelinha)
        print(f"A página {paginas} tem ~{linhas} linhas ({ocupacao}% ocupada).")
        if paginas == 2 and ocupacao < 35:
            print(f"DICA: corte ~{linhas} linhas para fechar em 1 página (\"densidade\": \"compacta\" resolve "
                  "umas 4); uma segunda página quase vazia passa impressão de descuido.")
        if paginas > 2:
            print("AVISO: mais de 2 páginas. Um CV desta senioridade deve fechar em 1, no máximo 2.")


if __name__ == "__main__":
    main()
