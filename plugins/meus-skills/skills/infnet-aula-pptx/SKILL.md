---
name: infnet-aula-pptx
description: Gera uma apresentação .pptx de aula no template do Instituto Infnet a partir de uma lista de temas e de uma lista de PDFs de bibliografia, com 10 slides por tema (conteúdo didático, diagramas, exemplo prático e exercícios de fixação). Use sempre que o pedido for criar slides, aula, material didático ou resumos contextualizados em .pptx a partir de bibliografia em PDF, mesmo que o usuário não cite a skill pelo nome nem diga "Infnet".
---

# Aula em .pptx a partir de temas e bibliografia

Produz material didático para aulas de pós-graduação em tecnologia: para cada tema recebido, 10 slides fundamentados nos PDFs recebidos, montados sobre `assets/exemplo.pptx`. O público é leigo no assunto e usará os slides depois como fonte de estudo, sem outro material de apoio.

## Entradas obrigatórias

Peça ao usuário, antes de qualquer outra coisa, o que faltar:

1. **Temas**: uma lista de textos. Cada tema gera exatamente 10 slides.
2. **Bibliografia**: uma lista de arquivos .pdf (caminhos ou anexos).

Não comece sem as duas listas e não invente temas nem fontes. Se o usuário já as informou no pedido, siga direto. Confirme que cada PDF existe e pode ser lido; se algum não abrir, avise e pergunte como proceder.

Se o usuário não disser qual PDF serve a qual tema, considere toda a bibliografia para todos os temas.

## Fluxo de trabalho

1. **Ler a bibliografia inteira.** `python scripts/extract_pdf.py arquivo.pdf` grava o texto por página em um .txt (use `--out-dir` para escolher a pasta). Se o PDF for digitalizado e não tiver texto, leia as páginas como imagem. Leia tudo antes de escrever: o conteúdo de um tema costuma estar espalhado pelo documento.
2. **Mapear cada tema na bibliografia.** Anote quais trechos sustentam cada tema. Se a bibliografia não cobrir parte de um tema, você pode complementar com definições básicas de conhecimento geral, mas guarde a lista do que foi complemento: ela entra no relato final.
3. **Planejar os 10 slides de cada tema** conforme `references/guia-de-conteudo.md` (estrutura, capacidade de texto por slide, tom, exemplos).
4. **Desenhar os diagramas** com `scripts/diagrams.py`, em um script de figuras no diretório de trabalho. `references/exemplo_figuras.py` mostra o padrão.
5. **Escrever a especificação** `spec.json` no diretório de trabalho. `references/exemplo_spec.json` é um tema completo que serve de modelo.
6. **Montar**: `python scripts/build_deck.py <dir de trabalho>/spec.json`. O .pptx é gravado na raiz desta skill. O script mede o texto e lista o que não cabe; corrija a especificação e rode de novo até sair sem erros.
7. **Conferir**: `python scripts/check_deck.py <arquivo.pptx>` verifica as regras de formatação. Depois faça a conferência visual (abaixo).
8. **Relatar** ao usuário (abaixo).

Use um diretório de trabalho temporário, fora da skill, para `spec.json`, figuras e textos extraídos. Na raiz da skill entra apenas o .pptx final.

Dependências: `pip install python-pptx pillow matplotlib lxml pypdf`.

## Regras do material

Estas regras vêm do professor e valem para todo slide. `build_deck.py` aplica as de formatação; as de conteúdo dependem de você.

**Formatação (automática pelo script)**

- Layout do `assets/exemplo.pptx` (layout `OBJECT`), sem alterar o template.
- Fonte Calibri preta em todo o texto: título em 30, subtítulo em 18 negrito, conteúdo em 18 normal.
- O subtítulo é a primeira linha do corpo e nunca é marcador.
- Marcadores e numeração mantêm a cor do template.

**Conteúdo (sua responsabilidade)**

- Cada tema reflete a bibliografia: afirmações atribuídas à fonte precisam estar na fonte. Cite a obra no primeiro slide do tema.
- Texto em português, de fácil compreensão para alunos de tecnologia leigos no assunto. Defina cada termo técnico na primeira vez em que aparece.
- Cada slide é conciso e autoexplicativo: frases completas, que façam sentido para quem estuda sozinho. Tópicos telegráficos não servem.
- Marcadores só quando o conteúdo é de fato uma lista. Não use em todos os slides; cerca de metade dos slides deve ser texto corrido ou texto com imagem.
- Equilibre texto, listas e imagens: em cada tema, por volta de 5 slides com diagrama.
- Subtítulos com substantivos, verbos e adjetivos iniciando em maiúscula e o restante em minúsculas ("Seleção do Código Relevante"); artigos, preposições e conjunções ficam em minúsculas. Evite siglas no subtítulo.
- O slide 9 de cada tema é um exemplo prático para executar em sala em um ambiente de prompt livre (Claude, ChatGPT, Gemini ou Copilot): traga o prompt pronto para os alunos enviarem e diga o que comparar ou observar.
- O slide 10 de cada tema são os exercícios de fixação (3 a 4 questões numeradas).
- O total é sempre 10 slides por tema, sem capa, sem slide de dúvidas e sem slide de referências, a menos que o usuário peça.

## Especificação

```json
{
  "arquivo": "Nome_Do_Arquivo.pptx",
  "temas": [
    {
      "titulo": "Título Curto do Tema",
      "slides": [
        {
          "subtitulo": "Tema 1: Visão Geral",
          "corpo": [["p", "Parágrafo com **negrito** e *itálico*."],
                    ["b", "item com marcador;"],
                    ["n", "item numerado;"]],
          "imagem": {"arquivo": "img/f01.png", "posicao": "abaixo", "alt": "Descrição da figura."}
        }
      ]
    }
  ]
}
```

- `titulo` aparece em todos os slides do tema, em 30 pt e em uma linha só. O tema que o usuário informa costuma ser uma frase longa; derive dele um título curto (até uns 38 caracteres) e use o tema completo para orientar o conteúdo.
- `corpo`: `p` é parágrafo, `b` é marcador, `n` é item numerado. `**texto**` vira negrito e `*texto*` vira itálico. Use itálico para prompts e títulos de obras, negrito para o termo que está sendo definido.
- `imagem` é opcional. `posicao` é `abaixo` (figura sob o texto) ou `lado` (texto à esquerda, figura à direita). Caminhos são relativos ao `spec.json`. Escreva sempre o `alt`.
- `arquivo` é só o nome; o destino é a raiz da skill. `--out-dir` existe para testes.

## Diagramas

As imagens são diagramas que explicam o conteúdo do slide (fluxos, comparações, camadas, antes e depois), não decoração. `scripts/diagrams.py` traz a paleta do template e primitivas (`canvas`, `box`, `txt`, `arrow`, `flow_row`, `cards_row`, `layer_stack`, `code_panel`); a docstring do módulo explica o uso.

- Desenhe no tamanho em que a figura aparece no slide: 7,6 pol de largura por 1,3 a 2,3 de altura para `abaixo`; 3,9 por até 3,5 para `lado`.
- Texto do diagrama entre 11 e 13,5 pt, com quebras de linha manuais (`\n`).
- Código-fonte vai em diagrama (`code_panel`), porque o texto do slide é só Calibri.
- Olhe cada PNG gerado antes de montar: texto vazando da caixa e rótulos sobrepostos são os defeitos comuns.

## Conferência visual

Se houver LibreOffice, converta e olhe todos os slides:

```bash
soffice --headless --convert-to pdf Arquivo.pptx
pdftoppm -jpeg -r 80 Arquivo.pdf slide
```

Procure texto cortado, imagem encostada no texto ou saindo do cartão branco, e título encostando no logotipo. Sem LibreOffice, confie no relatório de encaixe do `build_deck.py` e diga ao usuário que a conferência visual não foi feita.

## Relato final

Entregue o caminho do .pptx e, em poucas linhas:

- o que cada tema cobre e de quais partes da bibliografia veio;
- o que foi complemento seu por não estar na bibliografia;
- o resultado da revisão das regras (saída do `check_deck.py` e conferência visual);
- decisões que o usuário pode querer rever (títulos encurtados, por exemplo).
