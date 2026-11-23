---
name: varredura-ats
description: Varre os portais de vagas (ATSs) listados em ats-fontes.md da Recolocação 2026, coleta todas as posições abertas, filtra as de liderança e engenharia sênior em tecnologia, calcula o fit de cada uma contra o CV do Marcelo (critério do cv-job-fit) e entrega a lista de URLs com fit ≥ 75%, registrada no vault e na planilha vagas-fit.xlsx. Use sempre que o pedido for buscar, varrer, garimpar ou levantar vagas nos ATSs ou portais de carreira das empresas, "achar vagas com fit", "rodar a varredura", "atualizar a lista de vagas", ou repetir a busca nos ATSs, mesmo sem citar a skill. Para avaliar uma única vaga já em mãos, use cv-job-fit; para decidir e preparar a candidatura de uma vaga, use pipe-triage.
---

# Varredura de ATSs por fit

Esta skill percorre todos os portais de vagas que o Marcelo acompanha e devolve só as posições em que vale gastar esforço. O gargalo da busca não é achar vagas: são milhares nos portais. O trabalho é separar, com critério consistente, as poucas que encaixam no perfil, e registrar o resultado onde ele já trabalha.

## Fontes e saídas

| Item | Caminho |
|---|---|
| Lista de portais (fonte da verdade) | `C:\Users\marce\OneDrive\Documentos\SegundoCerebro\10-Projetos\Recolocacao-2026\ats-fontes.md` |
| CV e experiências | `C:\Users\marce\OneDrive\Documentos\SegundoCerebro\30-Recursos\curriculo\` (o PDF `CV - MARCELO TOMIO HAMA.pdf` é a base) |
| Planilha principal (histórico de candidaturas) | `...\Recolocacao-2026\Recolocação-2026.xlsx`, aba Aplicações. **Só leitura** nesta skill |
| Planilha de resultados | `...\Recolocacao-2026\vagas-fit.xlsx`, aba Vagas, colunas `Tier, Empresa, Posição, Link, Contato, Status, Histórico` |
| Nota da varredura | `...\Recolocacao-2026\busca-vagas-AAAA-MM-DD.md`, listada no `INDEX.md` do projeto |

Se a lista de portais mudou de lugar, pergunte antes de seguir. Ela é a única origem da busca, e varrer de memória traria portais errados.

## Fluxo

### 1. Coletar

```bash
python -I scripts/coletar_vagas.py --fontes "<ats-fontes.md>" --out "<pasta temporária>"
```

O script lê a tabela de portais e coleta pelas APIs públicas: Greenhouse, Lever, Ashby, Gupy, Workday e Mercado Livre, além dos sites próprios mapeados em `BOARD_CONHECIDO`. Ele devolve:

- `candidatas.json`: vagas que passam no filtro de título e local, já com JD;
- `requisitos.txt`: o trecho de requisitos de cada candidata, para ler rápido;
- `pendentes.json`: portais sem coletor;
- `log.txt`: contagem por portal.

O filtro de título é deliberadamente largo:

- **inclui** gerência, coordenação, tech lead, staff/principal, arquitetura e especialista em tecnologia, nas formas masculina e feminina;
- **exclui** só funções claramente de negócio ou de entrada.

Domínios de negócio no título ("Crédito", "Produtos Financeiros", "Pagamentos", "Segurança") não excluem a vaga: aparecem em títulos de vagas técnicas. É melhor ler algumas vagas a mais do que perder uma boa por causa do título.

### 2. Completar os portais pendentes com o navegador do app

Os portais em `pendentes.json` (Cornerstone, InHire, Oracle, Nodi, sites institucionais) montam a lista por JavaScript.

**Leia `references/coleta-navegador.md` antes de começar.** Ela traz o script de paginação de cada plataforma e as armadilhas de cada uma.

O ponto central é ler a lista **inteira**: todas as páginas, rolando até o fim. Uma primeira versão desta skill leu só a primeira página do Bradesco (25 de 233 vagas) e concluiu, erradamente, que não havia vaga de tecnologia.

1. Para cada portal, anote o total que ele informa e confira que coletou o mesmo número.
2. Aplique o mesmo filtro do script.
3. Para as candidatas, leia a JD na página.

Se um portal não tiver lista de vagas ou não carregar, registre isso nos limites da varredura e siga.

### 3. Ler requisitos e calcular o fit

Leia `requisitos.txt`. Quando o trecho não trouxer os requisitos, leia a JD completa da candidata. Calcule o fit com a régua do `cv-job-fit`, para que os números desta skill sejam comparáveis aos das outras análises:

**Pesos:**

| Componente | Peso |
|---|---|
| Requisitos obrigatórios | 70% |
| Diferenciais | 15% |
| Condições (local, modelo, idioma) | 15% |

**Pontuação por requisito:** Forte/Atende = 1, Parcial = 0,5, Fraco = 0,25, Ausente = 0.

**Tetos:**

- um gap eliminatório limita o fit a 65%;
- dois ou mais gaps eliminatórios limitam a 50%;
- **inglês acima de "professional working proficiency"** (avançado, fluente, C1) conta como gap eliminatório.

**Critérios do Marcelo que mudam a leitura:**

- **Lacuna é ferramenta, não categoria de vaga.** Plataforma, SRE, dados, governança e arquitetura podem encaixar. O que derruba o fit é a stack que ele não tem: .NET/C#, JS/React/Node/TypeScript, Terraform/IaC hands-on, Vue, Flutter, ML/DS hands-on, segurança ofensiva/defensiva.
- **Papel de IC (especialista, arquiteto, staff, tech lead) não é penalidade em si.** A régua é a mesma para IC e para gestão.
  - Conta como **Parcial**, e não como Ausente, só o requisito explícito de código hands-on diário ("perfil hands-on", "desenvolver e sustentar aplicações"), porque ele é gestor desde 2021.
  - Fora isso, avalie as ferramentas e o domínio como em qualquer vaga.
- **Ferramenta obrigatória ausente** (por exemplo "Azure (obrigatório)") é gap eliminatório e limita o fit a 65%. Quando a ferramenta só aparece listada, sem "obrigatório", conta como Fraco ou Parcial.
- **Cargo dois níveis acima do atual** (Director/Head vindo de Manager) em empresa onde ele não tem histórico: marque como despriorizado, mesmo com fit alto.
- **Regime PJ/contractor não elimina.** Sinalize e compare pela média mensal (CLT × 1,11; PJ sem 13º nem férias).
- **Local fora de SP** (BH, Curitiba, Recife) não elimina, mas entra como condição parcial e como risco a verificar.

Para cada vaga, guarde o fit, os 1 ou 2 requisitos que mais pesaram e o local/modelo. Não escreva o relatório completo do `cv-job-fit` vaga a vaga: numa varredura isso custa muito e não muda a decisão.

### 4. Cruzar com a planilha principal

Para cada vaga com fit ≥ 75%, procure a empresa e a posição na aba Aplicações de `Recolocação-2026.xlsx` (só leitura). Anote o que encontrar:

- já aplicada (e quando);
- rejeitada ou abandonada (pode ser republicação: diga isso);
- ausente.

Status de ATS ou etapa automática não contam como avanço. Só agenda com uma pessoa muda status.

### 5. Registrar

**Planilha `vagas-fit.xlsx`:** acrescente uma linha por vaga com fit ≥ 75% que ainda não esteja lá (compare pelo Link, sem duplicar).

| Coluna | Conteúdo |
|---|---|
| Tier | 1 se o fit for ≥ 80%; 2 se for 75–79% |
| Empresa | nome da empresa |
| Posição | título da vaga |
| Link | URL da vaga |
| Contato | só se houver um nomeado na planilha principal |
| Status | `triagem`, ou o status da planilha principal se a vaga já estiver lá |
| Histórico | `DD/MM varredura de ATSs: fit ~NN%, <local/modelo>. <risco ou observação>` |

Use fonte Arial, Link como hiperlink, e mantenha o filtro e o cabeçalho congelado. Faça backup antes de gravar e confirme que o arquivo não está aberto no Excel.

**Nota no vault `busca-vagas-AAAA-MM-DD.md`:**

- Frontmatter com `title`, `date`, `tags` e `status`.
- Seções:
  - **Método**: fontes, número de vagas coletadas e candidatas, e limites da coleta;
  - **Fit ≥ 75%**: tabela com fit, empresa, vaga, local, situação na planilha e URL;
  - **Quase (70–74%)**: com o que segura cada uma;
  - **Abaixo de 70%**: agrupado por motivo.
- Termine com `Related:` apontando para `ats-fontes.md`, `INDEX.md` e `plano-de-acao.md`.
- Liste a nota no `INDEX.md` do projeto e rode o lint do `obsidian-notes`.

### 6. Entregar

Ao final, mostre a lista numerada de URLs com fit ≥ 75%, do maior fit para o menor. Para cada uma, uma linha com empresa, cargo, fit, local e a situação na planilha principal. Depois, em poucas linhas:

- a vaga quase na linha de corte;
- os motivos de descarte mais comuns;
- os limites da coleta (portais que falharam ou só mostraram parte das vagas).

## Quando atualizar o script

Se um site próprio passar a usar um ATS conhecido, inclua o domínio em `BOARD_CONHECIDO`. Isso vale, por exemplo, quando um link "Ver vaga" levar a `boards.greenhouse.io/<board>`, `jobs.ashbyhq.com/<board>` ou `<sub>.gupy.io`. Atualize também a coluna Plataforma em `ats-fontes.md`. Isso tira o portal da lista de pendentes nas próximas varreduras.
