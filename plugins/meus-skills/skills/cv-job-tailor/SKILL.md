---
name: cv-job-tailor
description: "Gera um CV do Marcelo Tomio Hama em PDF, personalizado para uma vaga, a partir do texto da job description: escolhe e reescreve o conteúdo do LinkedIn e do Lattes, omite o que não serve à vaga, destaca o que ela pede e monta no template do CV base, legível por ATS e por triagem com IA. Use sempre que o usuário colar ou enviar uma descrição de vaga (JD) e pedir CV, currículo ou resume adaptado, personalizado, sob medida ou para uma vaga específica, mesmo sem citar a skill. Para só avaliar aderência, sem gerar CV, use cv-job-fit."
---

# CV personalizado para uma vaga

Recebe o texto de uma job description (JD) e entrega um CV em PDF feito para ela: mesmo profissional, mesma história, mas com a seleção e a ordem que fazem um filtro automático e um recrutador com 30 segundos encontrarem o que a vaga pede.

## Entrada

Uma JD, colada no chat, anexada ou em link. Se não veio, peça só isso. Não pergunte mais nada antes de gerar: idioma, senioridade e palavras-chave saem da própria JD, e as lacunas vão no relato final.

## Recursos

| Caminho | Papel |
|---|---|
| `assets/LinkedInProfile.pdf` | Conteúdo profissional completo. Fonte principal dos fatos de carreira. |
| `assets/Lattes.pdf` | Conteúdo acadêmico completo: formação, dissertações, publicações, docência, palestras. |
| `assets/CV - MARCELO TOMIO HAMA.pdf` | CV base: modelo de template, tom e tamanho, e desempate quando as fontes divergem. |
| `references/fontes.md` | O que só existe em cada fonte, divergências conhecidas e ordem de precedência. |
| `references/exemplo_spec.json` | O CV base transcrito para o formato de entrada do gerador. |
| `scripts/extract_sources.py` | Extrai o texto dos três PDFs. |
| `scripts/build_cv.py` | Monta o PDF a partir de um spec JSON. |
| `scripts/check_cv.py` | Lê o PDF como um ATS e confere ordem de leitura, datas e palavras-chave. |

Dependências: `pip install reportlab pypdf`.

## Fluxo de trabalho

Use um diretório de trabalho temporário, fora da skill, para os textos extraídos e o spec.

1. **Extrair as fontes**: `python scripts/extract_sources.py --out-dir <trabalho>`. Leia os três .txt inteiros e depois `references/fontes.md`. A extração é refeita a cada uso para que um PDF atualizado em `assets/` valha na hora.
2. **Ler a vaga** e separar: cargo e senioridade; requisitos obrigatórios; desejáveis; termos exatos que ela usa (tecnologias, métodos, domínio de negócio); idioma; local e modelo de trabalho; instruções de candidatura.
3. **Mapear evidência**: para cada requisito, o fato das fontes que o comprova. O que ficar sem evidência é lacuna e vai para o relato, não para o CV.
4. **Selecionar e redigir** conforme as seções abaixo.
5. **Escrever o spec** em `<trabalho>/spec.json`, no formato de `references/exemplo_spec.json`.
6. **Montar**: `python scripts/build_cv.py <trabalho>/spec.json --out-dir <pasta do usuário>`. O script informa páginas e quantas linhas sobram ou faltam. Corte e reescreva até fechar em 1 página, como o CV base; use 2 só quando o conteúdo relevante para a vaga não couber, e nesse caso ocupe ao menos metade da segunda. No layout `ats`, um marcador de até uns 105 caracteres ocupa uma linha.
7. **Conferir**: `python scripts/check_cv.py <cv.pdf> --spec <trabalho>/spec.json`, e olhe o PDF renderizado (`pdftoppm -png -r 80 <cv.pdf> pagina`, se houver poppler; senão, abra o PDF). Corrija todo ERRO; decida cada AVISO.
8. **Entregar** o PDF e o relato final.

Grave o PDF na pasta de trabalho do usuário, ou entregue na conversa quando a sessão não alcança a pasta dele. Não grave dentro da skill: ela vive em um repositório git e CVs gerados não devem ir para lá.

## Veracidade

Tudo o que entra no CV precisa estar em uma das três fontes ou ter sido dito pelo usuário na conversa. Reordenar, resumir, traduzir e trocar um termo pelo sinônimo que a vaga usa é personalizar. Acrescentar tecnologia, número, cargo, escopo de equipe ou domínio que as fontes não mostram é inventar, e um CV inventado cai na primeira pergunta técnica da entrevista, queimando a candidatura e a referência.

- Números saem das fontes exatamente como estão. Quando divergirem, siga a precedência de `references/fontes.md`.
- Cargo: use uma das formas que as fontes trazem para aquele emprego, a mais próxima do vocabulário da vaga. Não crie cargo novo.
- Experiência adjacente não vira especialidade. O plugin do MercadoPago é integração de pagamentos para lojistas, não processamento de pagamentos; liderar times com engenheiros de dados não é ser engenheiro de dados.
- Palavra-chave da vaga sem evidência fica fora, mesmo que derrube a cobertura no `check_cv.py`. Lacuna declarada ao usuário é útil; lacuna maquiada no CV é risco.

## O que omitir

O CV base já é o resultado de um corte. Para a vaga, corte de novo, com o critério: esta linha ajuda alguém a decidir que ele serve para esta posição?

- **Marcadores sem relação com a vaga** saem, mesmo quando são bons resultados. Cada linha fraca dilui as fortes.
- **Empregos recentes pouco relevantes** ficam com o cabeçalho e 1 marcador. Não remova o emprego: buraco na linha do tempo chama mais atenção que experiência lateral, e ATS soma tempo de experiência pelas datas.
- **Experiência antiga** (antes de 2014) vira uma entrada única de linhas curtas, como "Other Experiences" no CV base, ou sai. Recupere um item antigo quando a vaga pedir exatamente aquilo (mobile, telecom, educação).
- **Docência e produção acadêmica** (aulas, livro, artigos, palestras) entram com destaque quando a vaga valoriza isso: educação, pesquisa, treinamento, developer relations, cargos em que formar pessoas é parte do trabalho. Em vaga de mercado comum, reduza a uma linha ou omita, e tire do resumo: ocupa espaço e sugere agenda dividida.
- **Tecnologias** que a vaga não pede e que não dizem nada sobre senioridade saem da lista de competências. Lista curta e aderente vale mais que lista longa.
- **"How I Work"** só fica se sobrar espaço e a vaga for de liderança.
- **Dados pessoais** nunca: veja a lista em `references/fontes.md`. Local, só cidade/região e país, e só quando a vaga tem requisito de local, fuso ou modelo híbrido/presencial.

## O que destacar

- **Título** (campo `titulo`, logo abaixo do nome): o cargo da vaga, quando ele descreve com verdade o que o Marcelo já exerceu; senão, o cargo real mais próximo. É a primeira coisa que filtro e recrutador comparam com a vaga.
- **Resumo**: 3 a 5 linhas reescritas para a vaga. Abra com cargo e escopo (anos de liderança, tamanho de time, domínios), siga com os 2 ou 3 fatos que mais respondem aos requisitos obrigatórios e inclua os termos principais da JD. Sem adjetivos de autopromoção nem frase pessoal.
- **Competências**: logo após o resumo, só as que a vaga pede ou que sustentam a senioridade, agrupadas quando houver mais de umas 10 (ex.: Leadership, Cloud & Data, Languages). Escreva o termo como a vaga escreve.
- **Experiência**: dentro de cada cargo, ordene os marcadores por relevância para a vaga, não pela ordem das fontes. Empregos recentes e aderentes levam 3 a 5 marcadores; os demais, 1 ou 2. O LinkedIn tem resultados que o CV base não traz: use-os quando respondem à vaga.
- **Marcadores**: verbo de ação, o que foi feito, resultado medido. Até 2 linhas cada. Corrija a gramática ao reescrever, sem mudar o fato.
- **Vocabulário da vaga**: quando a fonte e a vaga falam da mesma coisa com nomes diferentes, use o da vaga e mantenha o original se ele ajuda. Fonte "Kafka/MSK", vaga "Apache Kafka": escreva "Apache Kafka (AWS MSK)". Escreva siglas por extenso na primeira vez quando a vaga usa a forma longa.
- **Formação e certificações**: as que a vaga pede vêm primeiro. Detalhes do Lattes (tema da dissertação, orientador, bolsa CNPq) entram quando o tema conversa com a vaga, como IA, agentes ou big data.
- **Idiomas**: use a formulação do CV base. O certificado CEFR B2 só é citado quando a vaga pede comprovação formal e B2 atende ao nível exigido; se a vaga pede mais que B2, citá-lo anuncia um teto abaixo do requisito.

## Idioma do CV

O da JD, a menos que ela ou o usuário digam outro. `idioma` aceita `en`, `pt` e `es` e define os títulos das seções. As fontes de conteúdo estão em português e o CV base em inglês: traduza com o vocabulário técnico do mercado do idioma de destino, sem traduzir nomes de produtos, empresas e tecnologias.

## Leitura por filtros automáticos e IAs

O `build_cv.py` cuida da parte estrutural: texto real, fontes padrão, sem tabelas nem imagens, metadados preenchidos e texto gravado na ordem de leitura. O conteúdo é com você:

- **Layout**: `ats` (uma coluna) é o padrão, porque todo extrator de texto o lê na ordem certa. `classico` reproduz as duas colunas do CV base; use quando o usuário pedir o visual idêntico ou disser que o PDF vai direto para uma pessoa. Extratores que leem linha a linha misturam colunas lado a lado.
- **Títulos de seção padrão**: os do script. ATS localiza as seções pelo nome; "Foreign Proficiency" ou "Tech Stack" podem não ser reconhecidos como idiomas e competências.
- **Períodos** no formato `Mon YYYY - Mon YYYY` (`Aug 2024 - Sep 2026`; em português, `Ago 2024 - Set 2026`), um período por entrada. Dois períodos na mesma empresa viram duas entradas, em ordem cronológica inversa com as demais: é assim que o parser calcula tempo de experiência.
- **Uma entrada por emprego**, com cargo, empresa e período na mesma linha, que é o que o script monta.
- **Sem caracteres decorativos**: o script troca travessões, aspas curvas e setas por equivalentes simples e recusa o que não consegue representar.
- **Palavras-chave em contexto**: o termo dentro de um marcador com resultado pesa mais para uma IA do que solto na lista de competências. Os mais importantes aparecem nos dois lugares.

## Spec

Veja `references/exemplo_spec.json`. Campos:

| Campo | Conteúdo |
|---|---|
| `arquivo` | Nome do PDF. Padrão: `CV - MARCELO TOMIO HAMA - <Empresa>.pdf`. |
| `idioma`, `layout`, `densidade` | `en`/`pt`/`es`; `ats`/`classico`; `normal`/`compacta` (use `compacta` só se faltarem poucas linhas para fechar a página). |
| `vaga` | `empresa`, `cargo` e `palavras_chave`: 12 a 25 termos copiados da JD como ela os escreve, inclusive os que não têm evidência. O `check_cv.py` mede a cobertura por eles. |
| `nome`, `titulo`, `contato` | Contato: `telefone`, `email`, `linkedin`, `local` (opcional). |
| `resumo` | Um parágrafo. |
| `competencias` | Lista de textos, ou lista de `{"grupo", "itens"}`. |
| `experiencias` | `cargo`, `empresa`, `periodo`, `local` (opcional), `itens`. |
| `formacao` | `curso`, `instituicao`, `periodo`, `local`. |
| `certificacoes` | `nome`, `emissor`, `ano`, `url` (vira link no nome). |
| `idiomas` | `idioma`, `nivel`. |
| `secoes_extras` | `titulo`, `itens`, `coluna` (`direita` ou `esquerda`, só para o layout `classico`). Para publicações, docência, "How I Work". |
| `rotulos` | Opcional: troca o título de uma seção padrão. |

`**texto**` vira negrito. Use pouco: negrito demais não destaca nada.

## Relato final

Curto, no idioma do usuário, junto com o PDF:

- o que foi destacado e por quê, em uma ou duas linhas;
- o que foi omitido em relação ao CV base;
- **lacunas**: requisitos da vaga sem evidência nas fontes. Se o usuário tiver a experiência e ela só não estiver escrita, ele informa e o CV é refeito;
- divergências entre fontes que afetaram o que entrou, e qual versão foi usada;
- resultado do `check_cv.py` (páginas, cobertura de palavras-chave, avisos que ficaram).
