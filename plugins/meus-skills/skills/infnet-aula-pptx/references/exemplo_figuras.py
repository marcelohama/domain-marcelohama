"""Exemplo de script de figuras: gera os cinco diagramas usados em exemplo_spec.json.

    python exemplo_figuras.py <pasta de saída>     # grava f01.png ... f05.png

Copie este padrão para o diretório de trabalho: uma função por figura, coordenadas em
polegadas, texto com quebras manuais. Ajuste o caminho de scripts/ no sys.path.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from diagrams import *  # noqa: E402,F401,F403

OUT = sys.argv[1] if len(sys.argv) > 1 else "img"


def f01():
    """Barra de proporção 70/30 (posição 'abaixo')."""
    fig, ax = canvas(7.6, 1.7)
    x0, w, y, h = 0.1, 7.4, 0.9, 0.62
    rect(ax, x0, y, w * 0.7, h, fc=BLUE)
    rect(ax, x0 + w * 0.7, y, w * 0.3, h, fc=NAVY)
    txt(ax, x0 + w * 0.35, y + h / 2, "70%  ·  onde a IA acelera", 15, "white", bold=True)
    txt(ax, x0 + w * 0.85, y + h / 2, "30%  ·  parte humana", 15, "white", bold=True)
    txt(ax, x0 + w * 0.35, 0.45, "código repetitivo, estruturas iniciais\ne primeiros rascunhos", 12.5)
    txt(ax, x0 + w * 0.85, 0.45, "arquitetura, regras de negócio,\ncontexto e qualidade", 12.5)
    save(fig, os.path.join(OUT, "f01.png"))


def f02():
    """Parte destacada dentro de um todo (posição 'lado')."""
    fig, ax = canvas(3.9, 3.4)
    box(ax, 0.05, 0.05, 3.8, 3.3, fc=LIGHT2, ec=LGRAY, r=0.12)
    txt(ax, 1.95, 3.08, "O projeto completo", 13.5, bold=True)
    cw, ch, xs = 1.6, 0.56, [0.27, 2.03]
    labels = [["Histórico\ndo projeto", "Decisões de\narquitetura"], ["Regras\nde negócio", "Convenções\nda equipe"]]
    for r, yy in enumerate([2.25, 1.55]):
        for c in range(2):
            box(ax, xs[c], yy, cw, ch, fc="white", ec=GRAY, lw=1.1, ls=DASH)
            txt(ax, xs[c] + cw / 2, yy + ch / 2, labels[r][c], 11.5, GRAY)
    box(ax, 0.15, 0.2, 3.6, 1.2, fc="white", ec=BLUE, lw=2.2, r=0.1)
    for c, lab in enumerate(["Pedido\ndo usuário", "Trecho\nde código"]):
        box(ax, xs[c], 0.68, cw, ch, fc=BLUE, ec=BLUE)
        txt(ax, xs[c] + cw / 2, 0.68 + ch / 2, lab, 11.5, "white", bold=True)
    txt(ax, 1.95, 0.44, "O que a IA recebe na conversa", 12, BLUE, bold=True)
    save(fig, os.path.join(OUT, "f02.png"))


def f03():
    """Fluxo de três etapas com seta de retorno."""
    fig, ax = canvas(7.6, 1.9)
    w, h, y, xs = 2.1, 1.0, 0.82, [0.1, 2.75, 5.4]
    data = [("Pessoa", "seleciona o contexto\ne descreve a tarefa", NAVY),
            ("IA", "gera o rascunho\ndo código", BLUE),
            ("Pessoa", "revisa e integra\nao sistema", NAVY)]
    for x, (t, d, c) in zip(xs, data):
        box(ax, x, y, w, h, fc=c, ec=c)
        txt(ax, x + w / 2, y + h - 0.22, t, 13.5, "white", bold=True)
        txt(ax, x + w / 2, y + 0.36, d, 12, "white")
    arrow(ax, (xs[0] + w, y + h / 2), (xs[1], y + h / 2))
    arrow(ax, (xs[1] + w, y + h / 2), (xs[2], y + h / 2))
    yb = 0.3
    ax.plot([xs[2] + w / 2, xs[2] + w / 2, xs[0] + w / 2], [y, yb, yb], color=GRAY, lw=1.8)
    arrow(ax, (xs[0] + w / 2, yb), (xs[0] + w / 2, y))
    txt(ax, 3.8, yb, "ajusta o contexto e repete", 12, italic=True, bg="white")
    save(fig, os.path.join(OUT, "f03.png"))


def f04():
    """Três módulos ligados por interfaces; o do meio em foco."""
    fig, ax = canvas(7.6, 1.55)
    w, h, y, xs = 1.9, 1.25, 0.15, [0.1, 2.85, 5.6]
    lados = [("Módulo Cadastro", "buscar_aluno(aluno_id)"), None, ("Módulo Multas", "calcular_multa(emp_id)")]
    for x, lado in zip(xs, lados):
        if lado is None:
            box(ax, x, y, w, h, fc=BLUE, ec=BLUE)
            txt(ax, x + w / 2, y + h - 0.25, "Módulo Empréstimos", 13, "white", bold=True)
            txt(ax, x + w / 2, y + 0.63, "em foco nesta conversa:", 11.5, "white")
            txt(ax, x + w / 2, y + 0.3, "código completo", 12, "white", bold=True)
        else:
            box(ax, x, y, w, h, fc="white", ec=GRAY, lw=1.2, ls=DASH)
            txt(ax, x + w / 2, y + h - 0.25, lado[0], 13, bold=True)
            txt(ax, x + w / 2, y + 0.63, "enviada só a interface:", 11.5, GRAY)
            txt(ax, x + w / 2, y + 0.3, lado[1], 9.5, family=MONO)
    for a, b in [(xs[0] + w, xs[1]), (xs[1] + w, xs[2])]:
        arrow(ax, (a + 0.04, y + h / 2 - 0.08), (b - 0.04, y + h / 2 - 0.08), style="<|-|>", ms=13)
        txt(ax, (a + b) / 2, y + h / 2 + 0.16, "interface", 11.5, italic=True)
    save(fig, os.path.join(OUT, "f04.png"))


def f05():
    """Faixa superior que alimenta uma sequência de etapas."""
    fig, ax = canvas(7.6, 1.9)
    box(ax, 0.1, 1.4, 7.4, 0.42, fc=LIGHT, ec=BLUE, lw=1.5)
    txt(ax, 3.8, 1.61, "Documento de contexto do projeto  ·  enviado no início de cada conversa", 12.5, bold=True)
    w, h, y = 1.25, 0.7, 0.12
    step = (7.4 - w) / 4
    labs = ["Conversa 1", "Resumo\ndo estado", "Conversa 2", "Resumo\natualizado", "Conversa 3"]
    for i, lab in enumerate(labs):
        x = 0.1 + i * step
        if i % 2 == 0:
            box(ax, x, y, w, h, fc=NAVY, ec=NAVY)
            txt(ax, x + w / 2, y + h / 2, lab, 12.5, "white", bold=True)
            arrow(ax, (x + w / 2, 1.4), (x + w / 2, y + h + 0.02), color=BLUE)
        else:
            box(ax, x, y, w, h, fc="white", ec=TEAL, lw=1.8)
            txt(ax, x + w / 2, y + h / 2, lab, 12)
        if i < 4:
            arrow(ax, (x + w + 0.03, y + h / 2), (x + step - 0.03, y + h / 2))
    save(fig, os.path.join(OUT, "f05.png"))


if __name__ == "__main__":
    for f in (f01, f02, f03, f04, f05):
        f()
    print("figuras gravadas em", os.path.abspath(OUT))
