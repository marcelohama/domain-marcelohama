"""Coleta vagas dos portais listados em ats-fontes.md e filtra as candidatas a fit.

Uso:
    python coletar_vagas.py --fontes <ats-fontes.md> --out <dir> [--extra-incluir REGEX]

Saídas em <dir>:
    todas.json       todas as vagas coletadas (empresa, plataforma, título, local, url, jd)
    candidatas.json  vagas que passam no filtro de título e local, com JD quando possível
    requisitos.txt   trecho de requisitos de cada candidata, para avaliar o fit
    pendentes.json   portais que o script não coleta (precisam do navegador)
    log.txt          resumo por portal

Só biblioteca padrão. As APIs usadas são públicas e não exigem login.
"""
import argparse, html, json, re, sys, unicodedata, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json,text/html,*/*"}
TIMEOUT = 40

# Sites próprios que usam um board conhecido por trás. Atualize ao descobrir novos.
BOARD_CONHECIDO = {
    "carreiras.inter.co": ("greenhouse", "inter"),
    "carreiras.quintoandar.com.br": ("greenhouse", "quintoandar"),
    "carreiras.ifood.com.br": ("greenhouse", "ifoodcarreiras"),
    "carreiras.btgpactual.com": ("greenhouse", "btgpactual"),
    "nu.com": ("ashby", "nubank"),
    "carreiras.itau.com.br": ("gupy", "https://vemproitau.gupy.io/"),
}

# Senioridade/liderança no título. Inclui formas femininas e trilhas de especialista,
# porque papel de IC não é motivo de descarte: o que derruba o fit é ferramenta que falta.
ROLE = re.compile(r"\b(gerente|manager|head|coordenador(a)?|coordenacao|lead|leader|lider|lideranca|diretor(a)?|director|superintendente|principal|staff|arquitet[oa]|architect|especialista|specialist|expert|chapter)\b")
# Tecnologia no título (inclui linguagens e funções técnicas comuns em títulos curtos, como "Tech Lead Java").
TECH = re.compile(r"(engenh|engineer|software|tecnolog|technology|\btech\b|\bti\b|\bit\b|plataform|platform|dados|\bdata\b|\bia\b|\bai\b|intelig.ncia artificial|cloud|sre|devops|arquitet|architect|sistemas|systems|desenvolvimento|development|developer|infra|mlops|backend|back-end|fullstack|java|python|golang|kotlin|solucoes|solutions|core banking)")
# Exclui só funções claramente de negócio ou de entrada. Domínios de negócio ("crédito",
# "financeiro", "pagamentos", "segurança") NÃO excluem: aparecem em títulos de vagas técnicas.
EXCLUI = re.compile(r"(vendas|comercial|loja|relacionamento|marketing|juridic|contab|fp&a|people|recursos humanos|\brh\b|logistic|\bdesign(er)?\b|product manager|product owner|account manager|customer success|\bsales\b|brand|auditor|tax|tribut|fiscal|recruit|talent|estagi|intern\b|trainee|aprendiz|analista|analyst|pleno|junior|jr\b|\bpl\b|scientist|cientista|data science|supply|compras|procurement|facilities|business development|partnership|growth|cobranca|advisor|enferm|medic|farmac|engenharia de projetos|planejamento comercial|agile coach|scrum master)")
LOCAL_OK = re.compile(r"(brasil|brazil|sao paulo|\bsp\b|remot|remote|latam|barueri|osasco|-sp|rio de janeiro|belo horizonte|curitiba|campinas|alphaville|porto alegre|florianopolis|recife|anywhere|^\s*$)")
REQ_HDR = re.compile(r"(requisit|requirement|qualifica|what you.?ll bring|what you bring|who you are|o que (voce precisa|esperamos|buscamos)|you have|must have|esperamos de voce|nao pode faltar|what we.?re looking|about you|sobre voce|diferencia)", re.I)


def norm(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def get(url, data=None, headers=None):
    h = dict(UA); h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    return urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "ignore")


def strip_html(t):
    t = html.unescape(t or "")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", t)
    t = re.sub(r"<li[^>]*>", "- ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def next_data(h):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    return json.loads(m.group(1)) if m else None


def vaga(emp, plat, title, loc, url, jd=""):
    return dict(empresa=emp, plataforma=plat, titulo=title.strip(), local=str(loc or ""), url=url, jd=jd)


# ---------- coletores ----------

def greenhouse(emp, board, eu=False):
    if not eu:
        j = json.loads(get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"))
        return [vaga(emp, "greenhouse", x["title"], (x.get("location") or {}).get("name", ""), x["absolute_url"], strip_html(x.get("content", ""))) for x in j["jobs"]]
    h = get(f"https://job-boards.eu.greenhouse.io/{board}")
    out = []
    for u, t in re.findall(rf'href="(https://job-boards.eu.greenhouse.io/{board}/jobs/\d+)"[^>]*>(.*?)</a>', h, re.S):
        title = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
        out.append(vaga(emp, "greenhouse-eu", title, "", u))
    return out


def lever(emp, slug):
    j = json.loads(get(f"https://api.lever.co/v0/postings/{slug}?mode=json"))
    out = []
    for x in j:
        jd = (x.get("descriptionPlain") or "") + "\n" + "\n".join(l.get("text", "") + "\n" + strip_html(l.get("content", "")) for l in x.get("lists", [])) + "\n" + (x.get("additionalPlain") or "")
        out.append(vaga(emp, "lever", x["text"], (x.get("categories") or {}).get("location", ""), x["hostedUrl"], jd))
    return out


def ashby(emp, slug):
    j = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}"))
    return [vaga(emp, "ashby", x["title"], x.get("location", "") + " " + " ".join(s.get("location", "") for s in x.get("secondaryLocations", [])), x["jobUrl"], x.get("descriptionPlain", "")) for x in j.get("jobs", [])]


def gupy(emp, url):
    sub = urllib.parse.urlparse(url).netloc.split(".")[0]
    j = next_data(get(f"https://{sub}.gupy.io/"))
    jobs = (j or {}).get("props", {}).get("pageProps", {}).get("jobs") or []
    out = []
    for x in jobs:
        w = x.get("workplace") or {}; a = w.get("address") or {}
        out.append(vaga(emp, "gupy", x["title"], f"{a.get('city', '')}-{a.get('stateShortName', '')} {w.get('workplaceType', '')}", f"https://{sub}.gupy.io/jobs/{x['id']}"))
    return out


def gupy_jd(url):
    j = next_data(get(url))
    job = (j or {}).get("props", {}).get("pageProps", {}).get("job") or {}
    return strip_html(" ".join(str(job.get(k, "")) for k in ["description", "responsibilities", "prerequisites", "relevantExperiences"]))


def workday(emp, url):
    p = urllib.parse.urlparse(url)
    tenant = p.netloc.split(".")[0]
    site = [s for s in p.path.split("/") if s][-1]
    api = f"https://{p.netloc}/wday/cxs/{tenant}/{site}/jobs"
    out, off, total = [], 0, None
    while True:
        r = json.loads(get(api, data=json.dumps({"appliedFacets": {}, "limit": 20, "offset": off, "searchText": ""}).encode(), headers={"Content-Type": "application/json"}))
        total = r.get("total", 0) if total is None else total
        for x in r.get("jobPostings", []):
            out.append(vaga(emp, "workday", x["title"], x.get("locationsText", ""), f"https://{p.netloc}{p.path.rstrip('/')}{x['externalPath']}"))
        off += 20
        if off >= total or off > 1000:
            return out


def meli(emp, url):
    out, start = [], 0
    while start <= 3000:
        r = json.loads(get(f"https://careers-meli.mercadolibre.com/api/positions?start={start}&num=100&location=Brazil&sort_by=timestamp"))
        items = r.get("positions") or []
        if not items:
            break
        for x in items:
            out.append(vaga(emp, "meli", x.get("name", ""), ", ".join(x.get("locations") or []), f"https://careers-meli.mercadolibre.com/pt/positions?id={x.get('id')}"))
        start += 100
    return out


def meli_jd(url):
    # A página da vaga é montada por JavaScript; a descrição vem desta API pública.
    pid = re.search(r"id=(\d+)", url).group(1)
    d = json.loads(get(f"https://careers-meli.mercadolibre.com/api/position-detail?id={pid}"))
    return strip_html(d.get("description") or "")[:12000]


def html_jd(url):
    return strip_html(get(url))[:12000]


# ---------- leitura de ats-fontes.md ----------

def ler_fontes(path):
    fontes = []
    for linha in open(path, encoding="utf-8"):
        if not linha.startswith("|") or "http" not in linha:
            continue
        cols = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cols) < 3:
            continue
        url = next((c for c in cols if c.startswith("http")), "")
        if not url or "portal.gupy.io" in url or "my.greenhouse.io" in url or "glassdoor" in url:
            continue  # áreas do candidato, não portais de vagas
        fontes.append(dict(empresa=cols[0], plataforma=cols[1], url=url))
    return fontes


def coletar(f):
    emp, url = f["empresa"], f["url"]
    host = urllib.parse.urlparse(url).netloc
    for dom, (plat, slug) in BOARD_CONHECIDO.items():
        if host.endswith(dom):
            return {"greenhouse": greenhouse, "ashby": ashby, "gupy": gupy}[plat](emp, slug)
    if "job-boards.eu.greenhouse.io" in url:
        return greenhouse(emp, url.rstrip("/").split("/")[-1], eu=True)
    if "greenhouse.io" in url:
        return greenhouse(emp, url.rstrip("/").split("/")[-1])
    if "jobs.lever.co" in url:
        return lever(emp, url.rstrip("/").split("/")[-1])
    if "ashbyhq.com" in url:
        return ashby(emp, url.rstrip("/").split("/")[-1])
    if ".gupy.io" in url:
        return gupy(emp, url)
    if "myworkdayjobs.com" in url:
        return workday(emp, url)
    if "careers-meli.mercadolibre.com" in url:
        return meli(emp, url)
    return None  # sem coletor: fica para o navegador


def candidata(v, extra=None):
    t, l = norm(v["titulo"]), norm(v["local"])
    if extra and re.search(extra, t):
        return True
    return bool(ROLE.search(t) and TECH.search(t) and not EXCLUI.search(t) and LOCAL_OK.search(l))


def trecho_requisitos(jd):
    linhas = [l.strip() for l in (jd or "").split("\n") if l.strip()]
    i = next((k for k, l in enumerate(linhas) if REQ_HDR.search(norm(l)) and len(l) < 90), None)
    corpo = linhas[i:i + 25] if i is not None else linhas[:20]
    return " | ".join(corpo)[:1400]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fontes", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--extra-incluir", default=None, help="regex extra de título a incluir mesmo fora do filtro")
    a = ap.parse_args()

    import os
    os.makedirs(a.out, exist_ok=True)
    todas, pendentes, log = [], [], []
    for f in ler_fontes(a.fontes):
        try:
            r = coletar(f)
            if r is None:
                pendentes.append(f); log.append(f"{f['empresa']}: navegador")
                continue
            todas += r; log.append(f"{f['empresa']}: {len(r)}")
        except Exception as e:
            pendentes.append(dict(f, erro=str(e))); log.append(f"{f['empresa']}: ERRO {e}")

    vistos, unicas = set(), []
    for v in todas:
        if v["url"] not in vistos:
            vistos.add(v["url"]); unicas.append(v)

    cands = [v for v in unicas if candidata(v, a.extra_incluir)]
    for v in cands:
        if v["jd"]:
            continue
        try:
            if ".gupy.io" in v["url"]:
                v["jd"] = gupy_jd(v["url"])
            elif v["plataforma"] == "meli":
                v["jd"] = meli_jd(v["url"])
            else:
                v["jd"] = html_jd(v["url"])
        except Exception as e:
            v["jd"] = f"ERRO ao baixar JD: {e}"

    json.dump(unicas, open(f"{a.out}/todas.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(cands, open(f"{a.out}/candidatas.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(pendentes, open(f"{a.out}/pendentes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(f"{a.out}/requisitos.txt", "w", encoding="utf-8") as fh:
        for i, v in enumerate(cands):
            fh.write(f"### {i} | {v['empresa']} | {v['titulo']} | {v['local'][:50]}\n{v['url']}\n{trecho_requisitos(v['jd'])}\n\n")
    log.append(f"TOTAL: {len(unicas)} vagas; {len(cands)} candidatas; {len(pendentes)} portais pendentes")
    open(f"{a.out}/log.txt", "w", encoding="utf-8").write("\n".join(log))
    sys.stdout.buffer.write(("\n".join(log) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
