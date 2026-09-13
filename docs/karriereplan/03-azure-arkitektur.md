# Azure-arkitektur: fra bruger til designer af platformen

> Du bruger allerede Azure dagligt, men nedefra: en ticket peger på en ressource, du retter noget, du går videre. Forskellen på at bruge og at designe er ikke at kende flere services — det er at kunne sige hvad et valg koster, og ved hvilken målbar tærskel du ville vælge om. I et hus med ni ansatte er der ingen der har prissat platformen, ingen der har kørt et Well-Architected review, og ingen der kan modsige dig når du har egne tal. Det er ikke en mangel du skal vente på bliver fyldt — det er den åbning hele dette spor udnytter.

## Cert-beslutningen, som er ændret siden alt det materiale du finder på nettet

Rådet "tag AZ-204 først" er dødt. AZ-204 blev pensioneret **31. juli 2026** og erstattet af AI-200 (Azure AI Cloud Developer Associate) — en AI-udviklereksamen med containeriseret hosting, vector search og RAG, ikke en generel .NET-eksamen. Enhver plan der anbefaler AZ-204, er skrevet før juli 2026 og skal kasseres i sin helhed, ikke bare på det punkt.

Ruten er nu præcis to eksamener: **AZ-104 → AZ-305**. AZ-104 er ikke valgfri: du kan bestå AZ-305 uden den, men titlen *Azure Solutions Architect Expert* udstedes ikke før AZ-104 er bestået **og aktiv**. Udløbne certifikater tæller ikke.

Begge certifikater udløber efter 12 måneder. Renewal er gratis, unproctored og open-book på Microsoft Learn. Konsekvens for rækkefølgen: tag ikke AZ-104 i måned 2 hvis AZ-305 først kommer i måned 11 — så skal du renewe midt i det hele. **Optimal afstand er 3-6 måneder.**

| Eksamen | Beslutning | Timing | Pris | Forberedelse | Hvorfor |
|---|---|---|---|---|---|
| AZ-104 Azure Administrator | **Tag** | Md. 4-5 | 165 USD ≈ 1.060 DKK | 40-70 t | Hård gate for titlen. Skills measured opdateret 17. apr. 2026: Identities and Governance op til 20-25%, Networking ned til 15-20%. Indeholder typisk en live hands-on lab — den kan ikke læses sig til, men spike-serien er forberedelsen |
| AZ-305 Designing Azure Infrastructure Solutions | **Tag** | Md. 9-10 | 165 USD ≈ 1.060 DKK | 40-60 t | 40-60 spørgsmål, 120 min, bestå ved 700/1000. Case studies er den del der ligner arkitektarbejde. Opdateret 17. apr. 2026 — tredjepartsmateriale fra før har drift |
| AI-200 | **Fravælg** | — | — | 0 t | Kend den, tag den ikke. At kunne forklare hvorfor du fravalgte den er i sig selv et modenhedssignal |
| SC-500, AB-100, AI-103, AZ-900 | **Fravælg** | — | — | 0 t | Skriv fravalget ned én gang, ellers genforhandles det hver måned. AB-100 hedder "Architect" og er ekstra fristende — men det er agentic AI i Business Applications, en anden karrierevej |
| Exam dumps | **Fravælg** | — | — | 0 t | Bryder eksamensaftalen, er ofte forkerte efter april 2026-opdateringen, og producerer præcis den kompetenceløse titel du ikke vil have |

AZ-305-vægte efter 17. april 2026: infrastructure 30-35%, identity/governance/monitoring 25-30%, data storage 20-25%, business continuity 15-20%. Læs **change log-sektionen** i study guiden først — den sparer timer.

Cert-nyhedsnichen er i 2026 domineret af AI-genereret SEO-spam; flere sider påstår at Expert-tieren er afskaffet og samlet under "Advanced", hvilket er forkert. Stol kun på learn.microsoft.com og techcommunity.microsoft.com på cert-status, priser og pensum.

## Rækkefølgen: fire faser

Azure-sporet må maks tage 6-8 timer om ugen i snit, ca. 380 timer af året. Resten går til læsning, skrivning og de eksterne feedback-loops.

| Fase | Måned | Fokus | Spikes | Timer/uge |
|---|---|---|---|---|
| **1. Fundament og hjemmebane** | 1-3 | Budgetkontrol, WAF checklists + tradeoffs, multitenant-guiden, Retail Prices-værktøj | 0, 1, 2 | 7-8 |
| **2. Distribueret virkelighed** | 4-6 | Messaging, idempotens, observability, identitet uden secrets. **AZ-104 md. 4-5.** Forfrem én spike til permanent drift | 3, 4, 5 | 8 |
| **3. Platform og modstand** | 7-9 | Governance, landing zone i miniature, netværksisolation, threat model, datastore-bake-off. **AZ-305 md. 9-10** | 6, 7, 8, 9 | 8 |
| **4. Kalibrering** | 10-12 | Bagudkompatibilitet under drift, WAF-review nr. 3, reduktionsøvelsen som fast rutine | 10, 11, 12 | 6 |

Den ugentlige kritiske læsning nedenfor kører **alle 52 uger** — den er ikke en fase, den er en vane.

## Budgetloftet: 400 DKK/md, hård alert ved 600

Serien kan køre for 150-400 DKK/md hvis den designes omkring free tiers. Alle tal er ved 1 USD = 6,43 DKK (10. sept. 2026) og **før moms** — læg 25% oveni.

| Gratis, og dækker 80% af øvebanen | Hvad du får | Fælde |
|---|---|---|
| Azure SQL free offer | **Lifetime.** 100.000 vCore-sek. + 32 GB data + 32 GB backup pr. database/md, 10 serverless databaser pr. subscription | Vælg **auto-pause**, ikke "continue using" |
| Cosmos DB free tier | **Lifetime.** 1000 RU/s + 25 GB, én konto pr. subscription | Opt-in ved oprettelse, kan ikke tilføjes bagefter. Gælder **ikke** serverless-konti |
| Container Apps free grant | 180.000 vCPU-sek., 360.000 GiB-sek., 2 mio. requests/md | En app der skalerer til nul og bliver inden for grantet koster nul |
| Log Analytics | 5 GB ingestion gratis pr. billing account | Derefter ~14,80 DKK/GB. Det er derfor sampling ikke er akademisk |

| Ødelægger budgettet — læres på papir og i Retail Prices API | Pris |
|---|---|
| Azure Firewall | 1,25 USD/time ≈ **5.870 DKK/md**. En glemt firewall over en ferie er ikke lærepenge, det er en månedsløn |
| Application Gateway WAF v2 | fra 0,443 USD/time ≈ **2.080 DKK/md** |
| Front Door Premium | 330 USD/md ≈ **2.120 DKK/md**. Front Door Standard (~225 DKK/md) er den eneste der kan forsvares i et lab, og kun i én måned |
| AKS node pools | ~600-1.500 DKK/md (control plane gratis, noderne ikke). Du skal kunne *argumentere* om AKS, ikke drive den |
| Private Endpoint | ~47 DKK/md pr. stk. Hands-on i syv dage, derefter ned |

**Den farligste knap i Azure:** spending limit findes kun på free account og credit-baserede subscriptions. Fjerner du den for at gå på pay-as-you-go, kan den **aldrig** genaktiveres — PAYG har ingen spending limit, og Azure viser den ikke engang i portalen. Derefter er budget alerts eneste værn, og de er e-mails, ikke en bremse. Anomaly detection er gratis, men advarer typisk 1-2 dage *efter* anomalien. Læs den dokumentation før du opretter den første ressource.

Regn ikke med Visual Studio-abonnementets 50/150 USD månedlige Azure-credit: fra 13. februar 2026 er den flyttet til Partner Center som bulk-credits på organisationsniveau. Om LeanLinking kan stille noget tilsvarende til rådighed skal verificeres konkret, ikke antages.

## Ressourcerne

| Ressource | Prioritet | Tid | Spring over |
|---|---|---|---|
| [Well-Architected Framework — pillars, checklists, **tradeoffs**](https://learn.microsoft.com/en-us/azure/well-architected/pillars) | Kerne | 8-10 t, derefter opslag | Service guides indtil en spike rammer servicen; alle workload-assessments (SAP, AVD, IoT) |
| [Well-Architected Review assessment (~60 spørgsmål)](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/) | Kerne | 90 min × 4 over året | — |
| [Architect multitenant solutions on Azure](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/overview) + [SaaS and multitenant solution architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/) | Kerne | 14-17 t | IoT, AI/ML, Media. Læs kun compute, data, networking, identity, governance, cost |
| [Architecture Center — Browse Architectures](https://learn.microsoft.com/en-us/azure/architecture/browse/) | Kerne | 45 min/uge i 12 mdr. | "Solution ideas" — marketingskitser. Gå efter Reference architectures og Example workloads |
| [Azure Retail Prices REST API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices) | Kerne | 4-6 t, derefter genbrug | Uautentificeret: kræver ingen adgang og intet mandat |
| [Spending limit, budgets og cost alerts](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit) | Kerne | 90 min, **før** noget deployes | EA- og Partner Center-scenarier |
| [Cloud Design Patterns, ~12 relevante](https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer) | Kerne | 6-8 t | De øvrige ~30. Katalogets fuldstændighed er en fælde |
| [Azure Monitor OpenTelemetry Distro for .NET](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable) | Kerne | 10-14 t | Alt med TelemetryClient/TrackEvent |
| [AZ-305 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-305) · [AZ-104](https://learn.microsoft.com/en-us/credentials/certifications/exams/az-104/) · [AZ-305](https://learn.microsoft.com/en-us/credentials/certifications/exams/az-305/) | Kerne | Se cert-tabel | Betalte bootcamps: 25.000-45.000 DKK for at komprimere noget der skal modne |
| [Azure Verified Modules (Bicep)](https://github.com/Azure/Azure-Verified-Modules) | Støtte | 6-8 t | **ALZ-Bicep classic.** Og Terraform i denne plan — to IaC-sprog på 12 måneder er halv kompetence i begge |
| [CAF — Ready + Govern](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/) | Støtte | 8-10 t | Strategy, Plan og Adopt **helt** — skrevet til CIO'er, største tidsfælde i CAF. Læs [subscription vending](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/subscription-vending) teknisk, ikke som ceremoni |
| [Microsoft Learn AZ-305 learning paths](https://learn.microsoft.com/en-us/training/paths/design-infranstructure-solutions/) | Støtte | 25-35 t | Brug som lakuneudfylder **efter** spikes. Omvendt rækkefølge er 30 timers passiv læsning du glemmer |
| [John Savill's Technical Training](https://www.youtube.com/playlist?list=PLlVtbbG169nHSnaP4ae33yQUI3zcmP5nP) | Støtte | 6-8 t | Master class som lineært forløb. Tjek udgivelsesdato: den mest citerede cram er ældre end april 2026 |
| Azure Landing Zones IaC Accelerator, `azure.github.io/Azure-Landing-Zones` (uverificeret URL) | Støtte | 10-14 t | Den fulde "complete" starter, multi-region, connectivity — den deployer mere end du har råd til |

## Fire spikes med fysisk output

### Spike 0 — Sikker landing (uge 1, 4-6 timer)

Eget abonnement, adskilt fra arbejdets — arbejdsgiverens subscription til privat læring er både en cost- og en compliance-fejl. Budget med alerts på 50/75/90/100%, forecast-alerts og anomaly detection aktiv. Naming convention og tagging-standard fastlagt **før** første ressource. Ét resource group pr. spike, så alt kan slettes med én kommando.

**Output:** ADR-001 om subscription- og spending limit-strategi med eksplicit risikovurdering. Screenshot af budgetkonfiguration. Naming/tagging-standard på én side. Teardown-script. En "dyre services"-liste du selv har prissat via Retail Prices API. Springes spiken over, ender de næste elleve med en uventet regning og et opgivet projekt.

### Spike 1 — Multi-tenant isolationsmodel for leverandørdokumentation (12-16 t)

Din ene reelle hjemmebanefordel. Design datalags- og adgangsisolation for et system hvor virksomheder uploader leverandørcertifikater og compliance-dokumentation. **Krav:** tenant A må aldrig kunne læse tenant B's dokumenter; én stor kunde kræver kontraktligt fysisk adskilte data; onboarding af ny tenant under 10 minutter; 50 små og 3 store tenants. **Begrænsning:** maks 40 DKK infrastruktur pr. lille tenant pr. måned. Evaluér tre modeller: delt database med tenant-kolonne plus Row-Level Security, database-pr-tenant, og bridge-modellen hvor små deler pool og store får silo.

**Output:** ADR med alle tre modeller, for og imod, og en **talfæstet tærskel** for hvornår en tenant flyttes fra pool til silo. C4 container-diagram. Fungerende .NET-prototype med RLS via SESSION_CONTEXT på Azure SQL free tier, plus en integrationstest der forsøger cross-tenant-læsning og fejler — skriv den negative test først. Cost-model for alle tre ved 50, 500 og 5.000 tenants. Den værdifulde del er ikke koden, men tærsklen: hvornår skifter matematikken.

### Spike 2 — Compute bake-off med egne tal (12-16 t)

Byg den samme .NET minimal API (ét endpoint der læser fra Azure SQL, ét der skriver) og deploy den tre gange: App Service B1, Container Apps med scale-to-zero, og Functions **Flex Consumption** (ikke den gamle Consumption-plan). Mål cold start efter 30 minutters inaktivitet, p95-latency ved 50 samtidige requests, DKK pr. 1.000 requests ved 10.000 / 1 mio. / 20 mio. pr. måned, og deployment-tid.

**Output:** én tabel med **faktiske egne målinger**, ikke citerede tal fra en blog. ADR med anbefaling og eksplicit brudpunkt. Beslutningstræ på én side. Load-test-scripts i repoet så målingen kan gentages. Slet App Service B1 (~84 DKK/md) straks efter måling. Egne tal kan ikke modsiges — det er derfor denne spike giver mest interviewmateriale pr. time.

### Spike 7 — Netværksisolation, og hvad den faktisk koster (10-14 t, maks 7 dage åben)

Flyt Azure SQL og Storage bag Private Endpoints. VNet med subnets, privat DNS-zone, VNet-integration for Container Apps. Bevis at offentlig adgang nu fejler, og dokumentér hvordan navneopløsningen faktisk fungerer — det er der 90% fejler.

**Output der er hele pointen:** en ADR med en **anbefaling om at lade være** for et system på din skala. To Private Endpoints er ~94 DKK/md, en ny klasse af svært diagnosticerbare fejl, og en DNS-afhængighed ingen forstår kl. 03. Dokumentér samtidig hvornår det bliver rigtigt: en kunde med kontraktligt krav om netværksisolation. Plus et papir-design af hub-spoke med App Gateway og Front Door, prissat via Retail Prices API, ikke deployet. Byg det, mål det, riv det ned — outputtet er evnen til at sige nej med tal.

## Sådan læser du en reference architecture kritisk

Microsofts reference architectures er delvist salgsmateriale forklædt som ingeniørarbejde: greenfield, en skala over din, et platform team der ikke findes hos jer, og næsten altid optimeret på Reliability og Security mens Cost og Operational Excellence efterlades som en øvelse til læseren. Færdigheden er ikke at kopiere dem, men at skrive den mindste version der opfylder 80% af kravene — og prisfastsætte begge.

Fast rutine, 45 minutter, én arkitektur om ugen, samme seks spørgsmål:

1. Hvilken skala antages, og hvad er den mindste version der stadig virker?
2. Hvilke pillars optimeres, og hvilke ignoreres?
3. Hvor mange komponenter skal patches, betales for og forstås kl. 03?
4. Hvilken organisation antages — findes det platform team hos jer?
5. Hvad er udeladt: pris, drift, vagtordning, migration, data residency, rollback, tenant-onboarding?
6. Hvor gammel er den? Tjek `ms.date` i GitHub-kilden bag siden (`MicrosoftDocs/architecture-center`). En arkitektur fra 2022 anbefaler services der er erstattet.

Skriv hver gang den reducerede version og prisfastsæt begge. Reduktionen skal have en **ærlig pris**: hvad den ikke kan, og ved hvilken vækst hver udeladt komponent bliver nødvendig. Uden den er analysen propaganda i den anden retning. Efter ca. 40 gennemløb kan du gøre det mundtligt på 20 minutter, og det er den kompetence der får folk til at spørge dig til råds.

Samme blik hører til WAF. Alle fem pillars har nu identisk struktur: design principles, checklist, **tradeoffs**, recommendation guides, patterns. Tradeoffs-siderne er det eneste sted Microsoft systematisk skriver ned hvad et valg *koster*, og det eneste sted juniorer aldrig kigger. Læs én om ugen i de første fem uger, én pr. pillar, og skriv for hver et eksempel fra det system du arbejder i til daglig.

## Den ene ting du beder om på arbejdet

Bed om **Reader-rollen på et non-prod subscription**. Den kan ikke afvises med en risikobegrundelse: Reader kan intet ændre, ødelægge eller koste. Formuleringen der virker: "jeg vil gerne kunne se ressourcerne når jeg debugger mine tickets, så jeg ikke skal spørge jer hver gang." Den giver dig Azure Advisor, resource-topologien, faktiske SKU'er og Cost Analysis (følger cost-adgang ikke med, så bed separat om Cost Management Reader) — nok til at tegne systemet selv, kortlægge hvordan tenants faktisk er isoleret, og notere SKU og månedspris hver gang en ticket rører en ressource.

## Faldgruber

- **At overse at AZ-104 er en hård forudsætning.** Du består AZ-305 og opdager at titlen ikke udstedes.
- **At tro AZ-305 gør dig til arkitekt.** Den beviser at du kan genkende det rigtige svar blandt fire. Certifikatet åbner HR-filteret; artefakterne består interviewet.
- **At lære ALZ-Bicep classic.** Blandt de mest sandsynlige spildte 15 timer, fordi det er hvad tutorials fra 2023-2025 bruger. Fjernet fra acceleratoren 16. februar 2026, repo arkiveres 16. februar 2027. Microsoft accepterer ikke længere nye ikke-AVM Bicep-moduler.
- **At lære Application Insights classic SDK.** SDK 2.x for .NET pensioneres 31. marts 2027. SDK 3.x (feb. 2026) er en bro — kend den, men byg på OpenTelemetry Distro'en.
- **At bruge de gamle Service Bus-biblioteker.** `WindowsAzure.ServiceBus`, `Microsoft.Azure.ServiceBus` og SBMP pensioneres **30. september 2026**. Brug `Azure.Messaging.ServiceBus` — og tjek om de gamle findes i den kodebase du arbejder i. Det er et konkret, tidsstemplet fund med en dato på.
- **Ikke at slette ressourcer efter en spike.** Ét resource group, et teardown-script, en ugentlig påmindelse. Undtagelsen er den ene forfremmede driftsservice.
- **At lade spike-serien glide over i produktbyggeri.** Symptomerne: en login-side, en admin-UI, "jeg skal lige rydde op i koden først". Reglen: ingen spike må producere en brugergrænseflade — Postman, curl og en integrationstest er grænsefladen.

## Sådan ved du at du kan det

Observerbare kriterier. Ingen af dem kan bestås ved at læse.

- Du kan på et whiteboard, uden noter, på under 10 minutter tegne det system du arbejder i på container-niveau og pege på de tre svageste punkter med en begrundelse der holder over for en senior kollega.
- Nogen spørger "hvad koster den her arkitektur om måneden ved 200 tenants?" — du svarer inden for 30 minutter med et tal, en kilde og en usikkerhedsmargin, inklusive egress, log ingestion, private endpoints og backup.
- For hvert teknisk valg i din portefølje kan du uopfordret navngive mindst én reel ulempe. Den hårde version: du kan argumentere overbevisende **for** det alternativ du selv fravalgte.
- Du kan køre et Well-Architected review på en arkitektur du ikke selv har bygget, på 90 minutter, og producere en prioriteret liste hvor hvert punkt har en omkostning i **begge** retninger — at rette og at lade være.
- Du kan læse en ukendt reference architecture og på 20 minutter mundtligt liste fem indbyggede antagelser, sige hvilke der er falske for din kontekst, og skitsere hvad der så ændrer sig — inklusive hvad der bliver **dyrere** ved at forenkle.
- Du har kørt samme WAF-review på samme service i måned 6, 9 og 12 og kan pege på dine egne tidligere fejlvurderinger. Det er kalibrering, og den kan ikke simuleres.
- AZ-104 bestået og **aktiv**, AZ-305 bestået, i den rækkefølge.
- Dit månedlige Azure-forbrug har over 12 måneder aldrig overskredet 600 DKK, og du kan forklare hvorfor hver post var der. Det er ikke et sparemål, men cost-disciplin under praksis — samme kompetence i lille skala som den en arbejdsgiver skal købe.
