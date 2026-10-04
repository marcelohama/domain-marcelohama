"""Primitivas para desenhar diagramas didáticos no estilo do template (matplotlib).

Uso típico, em um script de figuras no diretório de trabalho:

    import sys
    sys.path.insert(0, "<skill>/scripts")
    from diagrams import *

    fig, ax = canvas(7.6, 1.5)                       # polegadas = tamanho no slide
    flow_row(ax, ["Entrada", "Processo", "Saída"])
    save(fig, "img/f01.png")

As coordenadas do eixo são polegadas, então um texto de 12 pt no diagrama sai
com 12 pt no slide quando a imagem não é redimensionada.

Tamanhos de figura:
    posição "abaixo": 7.6 de largura por 1.3 a 2.3 de altura
    posição "lado":   3.9 de largura por até 3.5 de altura
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
from matplotlib.transforms import Affine2D

__all__ = [
    "NAVY", "BLUE", "TEAL", "LIGHT", "LIGHT2", "GRAY", "LGRAY", "INK", "ACCENT", "MONO", "DASH",
    "canvas", "save", "box", "txt", "arrow", "circle", "rect",
    "flow_row", "cards_row", "layer_stack", "code_panel",
]

# Paleta derivada do template (ondas azuis do Instituto Infnet) + um acento para "problema".
NAVY, BLUE, TEAL = "#073763", "#0079AD", "#00ABB4"
LIGHT, LIGHT2 = "#E3F3F8", "#F4F7F9"
GRAY, LGRAY, INK = "#5F6B76", "#C9D1D8", "#000000"
ACCENT = "#C8561B"
MONO = "DejaVu Sans Mono"
DASH = (0, (4, 3))
DPI = 220


def _setup_font():
    """Usa Calibri (Windows/macOS) ou Carlito (Linux, mesmas métricas); senão, a fonte padrão."""
    extra = ["/usr/share/fonts/truetype/crosextra", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")]
    for d in extra:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower().startswith(("carlito", "calibri")) and f.lower().endswith(".ttf"):
                    try:
                        fm.fontManager.addfont(os.path.join(d, f))
                    except Exception:
                        pass
    names = {f.name for f in fm.fontManager.ttflist}
    for name in ("Calibri", "Carlito"):
        if name in names:
            plt.rcParams["font.family"] = name
            return name
    return plt.rcParams["font.family"]


FONT = _setup_font()


def canvas(w, h):
    """Figura sem eixos, com coordenadas em polegadas: x em [0, w], y em [0, h]."""
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, path):
    """Grava o PNG (fundo branco, 220 dpi) e fecha a figura."""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)
    return path


def box(ax, x, y, w, h, fc="white", ec=LGRAY, lw=1.4, ls="-", r=0.08, rot=0):
    """Retângulo de cantos arredondados. (x, y) é o canto inferior esquerdo."""
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls)
    if rot:
        p.set_transform(Affine2D().rotate_deg_around(x + w / 2, y + h / 2, rot) + ax.transData)
    ax.add_patch(p)
    return p


def rect(ax, x, y, w, h, fc=LGRAY, ec="none", lw=1.0, **kw):
    p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw)
    ax.add_patch(p)
    return p


def circle(ax, x, y, r, fc=NAVY, ec="none"):
    p = Circle((x, y), r, fc=fc, ec=ec)
    ax.add_patch(p)
    return p


def txt(ax, x, y, s, size=12, color=INK, bold=False, italic=False, ha="center", va="center",
        family=None, rot=0, ls=1.15, bg=None):
    """Texto. Quebre linhas com \\n: o matplotlib não quebra sozinho."""
    kw = dict(fontsize=size, color=color, ha=ha, va=va, rotation=rot, linespacing=ls,
              fontweight="bold" if bold else "normal", fontstyle="italic" if italic else "normal")
    if family:
        kw["family"] = family
    if bg:
        kw["bbox"] = dict(fc=bg, ec="none", pad=3)
    return ax.text(x, y, s, **kw)


def arrow(ax, p1, p2, color=GRAY, lw=1.8, style="-|>", ms=15):
    """Seta de p1 para p2. Use style='<|-|>' para seta dupla."""
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle=style, lw=lw, color=color, shrinkA=0, shrinkB=0, mutation_scale=ms))


# ------------------------------------------------------------------ compostos
def flow_row(ax, labels, x0=0.1, x1=7.5, y=0.2, h=0.9, w=None, fills=None, size=12.5):
    """Sequência horizontal de caixas ligadas por setas.

    fills: lista de cores de preenchimento (None = caixa branca tracejada, texto preto).
    Padrão: azul, azul-marinho alternados e o acento na última caixa quando ela é o "problema"
    deve ser pedido explicitamente via fills.
    """
    n = len(labels)
    w = w or min(2.1, (x1 - x0) / (n + (n - 1) * 0.2))
    step = (x1 - x0 - w) / (n - 1) if n > 1 else 0
    fills = fills or [BLUE if i % 2 == 0 else NAVY for i in range(n)]
    for i, lab in enumerate(labels):
        x = x0 + i * step
        fc = fills[i]
        if fc is None:
            box(ax, x, y, w, h, fc="white", ec=GRAY, ls=DASH)
            txt(ax, x + w / 2, y + h / 2, lab, size, INK, bold=True)
        else:
            box(ax, x, y, w, h, fc=fc, ec=fc)
            txt(ax, x + w / 2, y + h / 2, lab, size, "white", bold=True)
        if i < n - 1:
            arrow(ax, (x + w + 0.04, y + h / 2), (x + step - 0.04, y + h / 2))


def cards_row(ax, cards, x0=0.1, x1=7.5, y=0.08, h=1.84, gap=0.175, highlight=None,
              title_size=13.5, body_size=12):
    """Cartões lado a lado: cards = [(título, texto com \\n), ...]. highlight = índice em destaque."""
    n = len(cards)
    w = (x1 - x0 - gap * (n - 1)) / n
    for i, (t, d) in enumerate(cards):
        x = x0 + i * (w + gap)
        hi = i == highlight
        box(ax, x, y, w, h, fc=LIGHT if hi else LIGHT2, ec=BLUE if hi else LGRAY, lw=2.2 if hi else 1.3, r=0.1)
        txt(ax, x + w / 2, y + h - 0.34, t, title_size, NAVY if hi else INK, bold=True)
        txt(ax, x + w / 2, y + (h - 0.5) / 2, d, body_size, INK, ls=1.25)


def layer_stack(ax, layers, x=0.08, w=3.74, top=3.38, h=0.58, gap=0.09):
    """Pilha vertical numerada: layers = [(título, descrição), ...], de cima para baixo."""
    for i, (t, d) in enumerate(layers):
        y = top - h - i * (h + gap)
        box(ax, x, y, w, h, fc=LIGHT, ec=BLUE, lw=1.4)
        circle(ax, x + 0.34, y + h / 2, 0.19, fc=NAVY)
        txt(ax, x + 0.34, y + h / 2 - 0.005, str(i + 1), 13, "white", bold=True)
        txt(ax, x + 0.7, y + h - 0.2, t, 12.5, INK, bold=True, ha="left")
        txt(ax, x + 0.7, y + 0.17, d, 11.5, INK, ha="left")


def code_panel(ax, x, y, w, h, title, lines, title_color=BLUE, size=9.2, line_gap=0.28, note=None,
               note_color=INK):
    """Painel de código monoespaçado. Código vai em imagem porque o texto do slide é só Calibri.

    Em 9.2 pt cabem cerca de 12 caracteres por polegada de largura útil.
    note: legenda em negrito abaixo do painel.
    """
    box(ax, x, y, w, h, fc=LIGHT2, ec=LGRAY, lw=1.3)
    txt(ax, x + 0.14, y + h - 0.22, title, 12.5, title_color, bold=True, ha="left")
    for i, s in enumerate(lines):
        txt(ax, x + 0.14, y + h - 0.57 - i * line_gap, s, size, INK, ha="left", family=MONO)
    if note:
        txt(ax, x + w / 2, y - 0.26, note, 11.5, note_color, bold=True)
