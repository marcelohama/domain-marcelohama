# Guia de conteúdo

## Estrutura dos 10 slides de um tema

| Slide | Papel | Forma usual |
|---|---|---|
| 1 | Visão geral: o que é o tema, por que importa, de qual obra vem. Subtítulo "Tema N: Visão Geral" | texto + diagrama |
| 2 a 4 | Conceitos: definições e o problema que o tema resolve | alternar texto corrido, texto + diagrama e lista |
| 5 a 8 | Aplicação: estratégias, etapas, critérios, sintomas, efeitos | alternar as três formas |
| 9 | Exemplo prático em sala. Subtítulo "Exemplo Prático: ..." | passos numerados com o prompt pronto |
| 10 | "Exercícios de Fixação" | 3 a 4 questões numeradas |

A divisão entre conceitos e aplicação é um ponto de partida. O que importa é a progressão: quem lê do slide 1 ao 8 chega ao exemplo prático sabendo o que vai observar.

Para decidir a ordem dos slides 2 a 8, escreva antes, em uma frase, o que o aluno deve saber ao fim do tema. Cada slide precisa aproximá-lo disso; se não aproxima, troque o slide.

## Capacidade de texto por slide

O corpo usa Calibri 18 em uma área de 8,5 por 3,75 polegadas. É pouco espaço, então escreva já dentro do limite:

| Forma | Texto que cabe |
|---|---|
| Só texto (largura total) | subtítulo + cerca de 10 linhas de até 68 caracteres |
| Imagem `abaixo` | subtítulo + 2 a 4 linhas; quanto menos texto, maior a figura |
| Imagem `lado` | subtítulo de até uns 28 caracteres + cerca de 10 linhas de até 33 caracteres |

Cada item de lista ocupa pelo menos uma linha, e cada parágrafo novo custa um pequeno espaço extra. `build_deck.py` mede de verdade e diz quantas linhas cortar.

Quando o texto não couber, corte a ideia menos importante em vez de comprimir todas. Um slide com uma ideia bem explicada ensina mais do que um com três ideias em frases truncadas.

## Como escrever

- Comece cada slide pela afirmação principal e depois explique. O aluno que relê o material precisa achar a ideia na primeira frase.
- Use frases completas. Uma lista de substantivos soltos não é autoexplicativa.
- Defina o termo na primeira ocorrência, em negrito: "**Contexto** é tudo o que o modelo recebe em uma conversa".
- Prefira o exemplo concreto à abstração. Um caso único que atravessa todos os temas (um sistema de biblioteca, uma loja) ajuda o aluno a ligar os conceitos e serve de base para os exemplos práticos.
- Ao atribuir uma ideia à bibliografia, diga isso no texto ("o capítulo propõe...", "segundo o autor...") e só atribua o que está lá. O que for complemento seu não leva atribuição.
- Evite números que envelhecem (limites de modelos, preços, versões), a menos que estejam na bibliografia.
- Itens de lista em minúscula, terminados em ponto e vírgula, e o último em ponto final, como no `exemplo.pptx`.

## Exemplo prático (slide 9)

O ambiente da aula é um chat de prompt livre: Claude, ChatGPT, Gemini ou Copilot. Não presuma IDE, terminal, repositório nem instalação.

Um bom exemplo prático:

- cabe em uma aula: três ou quatro passos;
- traz o prompt literal, em itálico e entre aspas, pronto para o aluno enviar;
- produz um contraste observável (com e sem a técnica do tema, por exemplo) e diz o que comparar;
- usa o mesmo caso dos slides anteriores.

## Exercícios de fixação (slide 10)

Três ou quatro questões numeradas, que cubram níveis diferentes: uma de definição com as próprias palavras, uma de explicação (por quê), uma de aplicação (monte, escreva, proponha) e, se couber, uma de análise que remeta a um slide do tema.

## Quando a bibliografia não cobre o tema

Acontece de o tema pedido ser mais específico do que o texto. Nesse caso:

1. Ancore o tema nas ideias da bibliografia que se relacionam com ele e atribua só essas.
2. Acrescente as definições básicas necessárias como complemento, sem atribuí-las à obra.
3. Informe ao usuário, no relato final, o que foi complemento.

Se a bibliografia não tiver relação alguma com o tema, pare e pergunte ao usuário antes de montar os slides.
