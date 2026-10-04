# As fontes: o que cada uma tem e onde divergem

Leia antes de redigir. As fontes foram escritas em momentos e para públicos diferentes, então contam o mesmo fato com palavras, datas e números ligeiramente diferentes. Um CV que mistura versões se contradiz na entrevista.

## Papel de cada fonte

| Arquivo | O que é | Use para |
|---|---|---|
| `assets/CV - MARCELO TOMIO HAMA.pdf` | CV padrão, em inglês, 1 página | Template, tom, tamanho dos marcadores, contato, e **desempate** de datas, cargos e números |
| `assets/LinkedInProfile.pdf` | Perfil completo do LinkedIn, em português | Conteúdo profissional: responsabilidades, resultados e stack de cada cargo, com mais detalhe que o CV base |
| `assets/Lattes.pdf` | Currículo Lattes completo | Conteúdo acadêmico: títulos e orientadores das dissertações, publicações, livro, palestras, eventos, vínculos de docência, produção técnica, cursos |
| `references/historias-star.md` | Banco de histórias STAR do Marcelo, em inglês | O como de cada resultado (runbook, comitê, cerimônias, método) e resultados que os PDFs não trazem |

## Ordem de precedência

1. O que o usuário disser na conversa (é a informação mais nova).
2. CV base, para datas, cargos, números e nível de idioma: é a versão que ele já envia.
3. LinkedIn, para tudo o que o CV base não traz sobre a carreira.
4. Banco de histórias STAR, para ações e resultados que os PDFs não trazem. Quando um número dele divergir do CV base ou do LinkedIn, valem estes; a lista está no fim de `historias-star.md`.
5. Lattes, para tudo o que é acadêmico; para carreira, só quando as outras se calam.

Quando uma divergência afetar algo que entrou no CV, diga no relato final qual versão foi usada.

## O que só existe em uma fonte

**Só no banco de histórias STAR**
- Pismo/Visa: runbook e comitê de Ops junto com o on-call; backlog de estabilidade e suporte zerado; retros e cerimônias de time, satisfação de 77 para 83 pontos, unificação de 2 squads; promoções a nível staff/consultant; processo de AIOps com Claude fechando +100 findings de segurança por mês; delay E2E do Autoloader de 30 min para 1 min.
- Itaú: crashes do app iti abaixo de 0,01% das sessões e App Score de 3 para 4,7; autenticação usada por 55 milhões de clientes.
- MercadoPago: meetups e parceria com a comunidade não oficial, +200% de clientes rastreados.
- NIC.br: Monitor Banda Larga entregue para Windows, macOS, iOS e Android; PoC do SIMET instalada por cerca de 1 milhão de usuários.

**Só no LinkedIn**
- Pismo/Visa: 2 squads (Assets e Interest Management); comitês de cybersec, inovação e backlog; colegiado de arquitetura; engenharia orientada a GenAI (Claude skills e agentes); +1500% de volume operacional com onboarding de 2 clientes; lançamento de 2 produtos (CDB Comandado e Conta Remunerada); tempo de resposta -76%.
- Natura 2023-2024: 60 milhões de processos/dia e 120k operações/s; consistency repair -60%; cofre de senhas em cloud.
- Natura 2021: 2 clusters Spark/EMR com mais de 200 jobs, expansão para mais 3 países; migração Kafka IaaS para MSK com -90% de incidentes.
- OLX: contratação de 3 engenheiros; A/B tests com +7% de leads; findings OWASP com -90% no score de risco.
- Itaú: MFA por fingerprint no canal Credicard; coautoria da lib de biometria facial; design da autenticação do PIX para o iti.
- MercadoPago: stack do plugin (PHP, GoLang, NodeJS).
- NIC.br: stack mobile (Java/Android, Objective-C/Swift), SIMET Mobile, integração com o backbone do .br.
- Consultoria 2010-2014 (MyWay, Siter, Spotwish@Wayra) com resultados por cliente; prêmio BEW Hackathon.
- Docência: disciplinas (Arquitetura de Software, Programação em Big Data, IA, Microserviços com Java, Advanced Backend, Algoritmos, Estruturas de Dados).
- Certificações: PLS CEFR B2; Build a Secure Google Cloud Network; Claude Code in Action & Claude Code 101.

**Só no Lattes**
- Mestrado: dissertação "UAVAS: An Agent Oriented Infrastructure for Unmanned Aerial Vehicles Development", orientador Rafael H. Bordini, bolsa CNPq.
- MBA: trabalho "O Big Data na Área Financeira: Estudos dos Casos das Criptomoedas e do e-Commerce", 600h.
- Graduação: TCC sobre métodos ágeis Scrum/XP em objetos de aprendizagem.
- Livro (Lap Lambert, 2013, ISBN 3659476277), 2 artigos completos em anais, 4 apresentações, podcast Enzimas #285 (2025).
- Material didático "Advanced Backend" (Descomplica, 2023); organização do WooCommerce Day 2017 e do 2o Hackathon FMU 2019.
- Vínculos de docência com datas: FMU 2018-2024, FIAP 2024, Infnet 2026-atual.
- Participação em eventos (PHP Experience, WordCamp, Campus Party, Agile Brazil e outros).
- Idiomas adicionais: japonês e italiano.

## Divergências conhecidas (levantadas em 03/10/2026)

Se os PDFs em `assets/` forem trocados por versões mais novas, reconfira esta tabela contra o texto extraído. As divergências do banco de histórias STAR estão no fim de `historias-star.md`.

| Assunto | CV base | LinkedIn | Lattes |
|---|---|---|---|
| Pismo/Visa, período | Aug/2024 a Sep/2026 | ago/2024 a "Present" | 2024 a 2026 |
| Pismo/Visa, cargo | IT & Data Engineering Manager | Gerente de Engenharia, Plataforma TechFin | Software and Data Manager |
| Pismo/Visa, MTTR | -17% | 16,5% | |
| Pismo/Visa, segurança | >90% de redução de findings | redução de vulnerabilidades em 100% | |
| Pismo/Visa, cobertura de testes | de 34% para 85% | +53% | |
| Natura, cargo | Tech Manager (os dois períodos) | Gerente de Projetos, Plataformas Globais (2023-24); Coordenador de TI, Plataforma de Indicadores (2021) | Gerente de Programas e Projetos; Coordenador de Projetos de TI |
| OLX, início | Dec/2021 | nov/2021 | 2021 |
| OLX, segurança | corrigiu +10 vulnerabilidades AWS ECR | findings OWASP, -90% no score de risco | |
| Itaú, cargo | IT Tech Lead | Engenheiro de TI Sênior, Techlead de Autenticação | Analista Engenheiro de TI Seg. Inf. |
| MercadoLibre, cargo | Staff Software Engineer | Engenheiro de Software Sênior | Analista de Desenvolvimento de Software |
| MBA FIA, período | May/2015 a Dec/2016 | abr/2015 a dez/2017 | 2015 a 2017 (título em 2016) |
| Graduação UNESP, fim | Feb/2010 | 2010 | 2009 |
| Consultoria | 2011 a 2016 (VIVO e start-ups) | nov/2010 a abr/2014 | Spotwish 2011-12, Siter 2012-13, MyWay e Agendalize 2014-16 |
| Anglo Prudentino | 2006 a 2010 | ago/2008 a fev/2010 | 2006 a 2010 |
| Inglês | Professional working proficiency | "Full Professional" na lista; "CEFR B2" no headline e nas certificações | compreende, fala, escreve e lê bem |
| Espanhol | avançado nas quatro habilidades | não lista | compreende e lê bem; fala e escreve razoavelmente |
| Certificações AWS | AWS AI Practitioner | headline diz "2x AWS Certified", mas a lista mostra só a AIF-C01 | |

## Pontos em aberto

- **Segunda certificação AWS**: o headline do LinkedIn fala em duas, as fontes só nomeiam a AWS Certified AI Practitioner (AIF-C01). Cite apenas esta, a menos que o usuário informe a outra.
- **Emissor e ano das certificações**: o CV base traz só nome e link. Emissor e ano conhecidos: Formação Executiva em Estratégia Empresarial, FGV, 2020-2021, 64h (Lattes). Para as demais, deixe o ano vazio em vez de supor.

## O que nunca entra no CV

Estão nas fontes, mas não pertencem a um CV: endereço residencial e profissional, data e local de nascimento, ID Lattes, Facebook, e-mail alternativo, hobbies e a frase pessoal do resumo do LinkedIn, hashtags, o curso técnico interrompido e os cursos de 1998 a 2013 sem relação com a vaga.
