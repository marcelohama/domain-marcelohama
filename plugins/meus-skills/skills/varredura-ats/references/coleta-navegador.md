# Coleta pelo navegador do app

Estes portais montam a lista de vagas por JavaScript, e o script não os coleta. Use as ferramentas do navegador do app (`mcp__Claude_Browser__*`): `navigate` para abrir a página e `javascript_tool` para ler os links já renderizados.

**Leia sempre a lista inteira.** O erro que motivou esta página foi ler só a primeira página do Bradesco: 25 de 233 vagas.

Em todos os casos, aplique sobre cada título a mesma função `candidata()` do script: as regex `ROLE`, `TECH` e `EXCLUI`, mais o local. Copie as regex do script em vez de reescrevê-las.

## Cornerstone (CSOD), por exemplo Bradesco

- A lista é paginada de 25 em 25.
- O botão de próxima página tem `aria-label` "Next Page, N".
- **Cuidado:** no rodapé há um link com o texto "Next" que leva a outro site (o banco Next). Não procure o botão pelo texto.

Script para colar no `javascript_tool`, com a página inicial já aberta:

```js
function grab(){return [...document.querySelectorAll('a')].filter(a=>/requisition\/\d+/.test(a.href)).map(a=>{let c=a;for(let i=0;i<4&&c.parentElement;i++){c=c.parentElement;if(c.innerText.length>a.innerText.length+15)break;}return {t:a.innerText.replace(/\s+/g,' ').trim(),u:a.href.replace(/\?.*$/,''),info:c.innerText.replace(/\s+/g,' ').slice(0,220)};});}
let all=grab();
for(let p=0;p<40;p++){const nx=[...document.querySelectorAll('button')].find(b=>/^Next Page/.test(b.getAttribute('aria-label')||''));if(!nx||nx.disabled)break;const before=grab()[0]?.u;nx.click();let ok=false;for(let k=0;k<12;k++){await new Promise(r=>setTimeout(r,700));const g=grab();if(g.length&&g[0].u!==before){ok=true;break;}}if(!ok)break;all.push(...grab());}
const uniq=[...new Map(all.map(x=>[x.u,x])).values()];window.__vagas=uniq;uniq.length
```

**JD da vaga:** abra `.../requisition/<id>?c=<empresa>` e leia o texto entre "Como será seu dia a dia" e "O que você encontra aqui". Essa faixa contém atividades, modelo de trabalho, requisitos e diferenciais.

Não tente extrair tokens de API da página. A interface basta, e esse caminho é bloqueado pelas permissões.

## InHire (Pottencial, Riachuelo, Cielo)

- As vagas são links com o padrão `/vagas/<uuid>/<slug>`.
- A lista pode carregar mais itens ao rolar a página. Role até o fim (`window.scrollTo(0, document.body.scrollHeight)`) várias vezes, até a contagem de links parar de crescer.
- A JD fica na própria página da vaga.

## Nodi (dLocal)

- O cabeçalho mostra o total ("58 Open Positions"), mas só uma parte das vagas aparece de início.
- Role e procure por botões de "load more" até a contagem bater com o total.
- As vagas são links `app.nodi.global/jobs/public/<uuid>`.

## Oracle Cloud HCM (PicPay)

- Aguarde cerca de 10 segundos para a lista carregar.
- A contagem aparece como "N VAGA(S) ABERTA(S)".
- Os links de vaga contêm `/job/`.

## Sites sem lista (por exemplo F1rst)

Registre o portal nos limites da varredura e siga. Se descobrir o ATS real (um link "Ver vaga" para Gupy, Greenhouse e afins), atualize `ats-fontes.md` e `BOARD_CONHECIDO` no script.

## Experian

- O portal é global, e o filtro de local pela URL não funciona.
- Use o filtro "Location" da interface (Brazil) antes de ler os links `/job/...-jid-<n>`.
