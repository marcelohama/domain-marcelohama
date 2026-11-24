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

## InHire (24 portais em `ats-fontes.md`)

**Coletor em lote.** Para não abrir portal por portal, mande um único `browser_batch` com um par de ações para cada URL InHire do `ats-fontes.md`: `navigate` para a URL e, em seguida, `javascript_tool` com o script abaixo. Em 23/11, 8 portais por lote rodaram sem expirar.

```js
await new Promise(r=>setTimeout(r,2500));
const links=()=>[...new Map([...document.querySelectorAll('a[href*="/vagas/"]')].map(a=>[a.href,a.innerText.split('\n')[0].trim()])).entries()];
let p=-1,s=0;
for(let i=0;i<25&&s<3;i++){
  [...document.querySelectorAll('*')].forEach(e=>{if(e.scrollHeight>e.clientHeight+50&&/auto|scroll/.test(getComputedStyle(e).overflowY))e.scrollTop=e.scrollHeight;});
  window.scrollTo(0,document.body.scrollHeight);
  await new Promise(r=>setTimeout(r,700));
  const n=links().length; if(n===p)s++; else{s=0;p=n;}
}
({empresa:document.title, inativo:document.title==='InHire'||/inactive|inativa/i.test(document.body.innerText), vagas:links().map(([url,titulo])=>({titulo,url}))})
```

- **Saída:** `empresa`, `inativo` e a lista `vagas` com título e URL. A lista não mostra local nem modelo de trabalho: leia-os na JD das candidatas.
- **Portal inativo:** o título da página fica "InHire" ou aparece "This company is temporarily inactive". Em 23/11 estavam assim Agrotools, CI&T e Tractian. Marque o portal como ❌ em `ats-fontes.md` e procure o canal atual da empresa.
- **Portal grande:** na Riachuelo, uma passada pegou 220 das 390 vagas. Quando a contagem passar de ~150, rode o script de novo na mesma página até o número parar de crescer.
- **Sem API:** não use a API interna do InHire (`api.inhire.app`). Ela não é documentada para uso público e o acesso direto é bloqueado pelas permissões. A coleta é sempre pela página.

**Detalhes da página:**

- As vagas são links com o padrão `/vagas/<uuid>/<slug>`.
- A lista carrega mais vagas ao rolar um **painel interno** da página, e rolar só a janela não basta. Uma varredura anterior parou em 60 das 390 vagas da Riachuelo por causa disso.
- Role a janela e todo elemento com `overflow-y` auto ou scroll, repetindo até a contagem de links parar de crescer. Mantenha cada chamada curta, porque o `javascript_tool` expira em 45 s:

```js
const g=()=>new Set([...document.querySelectorAll('a[href*="/vagas/"]')].map(a=>a.href)).size;
let prev=-1,same=0;
for(let i=0;i<25&&same<3;i++){
  [...document.querySelectorAll('*')].forEach(e=>{if(e.scrollHeight>e.clientHeight+50&&/auto|scroll/.test(getComputedStyle(e).overflowY))e.scrollTop=e.scrollHeight;});
  window.scrollTo(0,document.body.scrollHeight);
  await new Promise(r=>setTimeout(r,900));
  const n=g(); if(n===prev) same++; else {same=0;prev=n;}
}
g()
```

- Se a contagem ainda estiver crescendo no fim, rode o script de novo.
- Guarde o link completo, com o slug: `/vagas/<uuid>` sem o slug abre uma página de erro.
- A JD fica na própria página da vaga.

## Nodi (dLocal)

- O cabeçalho mostra o total ("58 Open Positions"), mas só uma parte das vagas aparece de início.
- Role e procure por botões de "load more" até a contagem bater com o total.
- As vagas são links `app.nodi.global/jobs/public/<uuid>`.

## Oracle Cloud HCM (PicPay)

- Aguarde cerca de 10 segundos para a lista carregar.
- A contagem aparece como "N VAGA(S) ABERTA(S)".
- Os links de vaga contêm `/job/`.

## Sites sem lista de vagas

Registre o portal nos limites da varredura e siga. Se descobrir o ATS real (um link "Ver vaga" para Gupy, Greenhouse e afins), atualize `ats-fontes.md` e `BOARD_CONHECIDO` no script.

## Experian (inclui Serasa Experian)

- O portal é global, e o filtro `location=Brazil` da URL não filtra.
- A listagem é HTML do servidor. Busque `/jobs?page=N&size=48` com `fetch` até não vir mais vaga, e leia o local no cartão de cada link `/job/...-jid-<n>`, no texto entre "Location" e "Employment".
- Fique com os locais no Brasil (em 22/11 eram 180 de 396 vagas) e baixe a descrição de cada candidata pela própria URL.
