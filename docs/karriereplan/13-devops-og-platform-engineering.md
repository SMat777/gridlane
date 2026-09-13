# 13. DevOps og platform engineering: at eje hele vejen til produktion

> Hos jer er der ingen platform-team, ingen release manager, ingen der hedder "DevOps engineer".
> Det er dig. Og det er ikke et mandat du mangler — det er et ansvar ingen har taget endnu.
> Den arkitekt der designer systemer men ikke ejer vejen til produktion, designer diagrammer, ikke systemer.
> Og i et firma med ni ansatte er skellet mellem "det virker lokalt" og "det kører i produktion" hele forskellen mellem en ide og et produkt.

## CI/CD-pipelinen som arkitekturbeslutning

En pipeline er ikke tooling. Den er et arkitekturdokument der siger hvad du stoler på, hvad du verificerer, og hvad du er villig til at vente på. Det er den eneste arkitekturbeslutning **samtlige** udviklere mærker **hver** dag.

| Designvalg | Arkitekturbeslutning der gemmer sig bag | Konsekvens hos jer |
|---|---|---|
| Pipeline-varighed | Hvad du tester i CI vs. hvad du deferrer | En 15-min pipeline med tre udviklere koster 1,5-2,5 timer/dag i kontekstskift. En 3-min pipeline ændrer deploy-kadence fra 1-2/dag til 5-10/dag |
| GitHub Actions vs. Azure DevOps Pipelines | Hvor jeres workflow lever, og hvem der kan læse det | GitHub Actions har bredere økosystem, bedre YAML-ergonomi og reusable workflows. Azure DevOps har native integration med Boards og Artifacts men er tungt for tre udviklere. Vælg én, skriv en ADR, og migrer ikke halvvejs |
| Hvad der kører i CI | Din tillid til testsuiten | Build, unit tests, linting, SBOM-generering, eventuelt en fitness function. Integration tests mod Testcontainers hører i CI. End-to-end mod Azure-ressourcer hører i en nightly eller pre-release pipeline |
| Hvad du ikke bygger selv | Din modenhed | Renovate/Dependabot til dependency-opdateringer, GitHub Advanced Security til secret scanning. At bygge det selv er forfængelighed |

**Mål pipeline-varighed som en metrik.** Registrer den i et dashboard, og sæt en SLO: 90% af builds under 4 minutter. Overskrides den, er det en arkitekturticket, ikke en ops-ticket. Den hyppigste årsag i .NET-projekter: NuGet restore uden cache, parallelle test-projekter der kører sekventielt, og Docker-builds der ikke udnytter layer caching.

GitHub Actions vs. Azure DevOps er ikke et teknisk valg — det er et organisationsvalg. Er jeres kode på GitHub, brug Actions. Er den på Azure Repos, brug Pipelines. At køre begge dele for tre udviklere er et beslutningsforfald, ikke fleksibilitet.

## Infrastructure as Code

ClickOps — at klikke infrastruktur sammen i portalen — har en skat du betaler hver gang nogen spørger "hvad har vi egentlig kørende?", "kan du sætte det op igen?", eller "hvad ændrede sig siden i tirsdags?". Skatten er usynlig, fordi den betales i tid-til-svar, ikke i kroner.

**Bicep vs. Terraform for jer:** Bicep. Tre grunde: (1) det er Azures eget sprog med dag-nul support for nye ressourcetyper, (2) ingen state-fil at administrere — Azure Resource Manager *er* state-backend, (3) jeres team er tre .NET-udviklere, ikke polyglotte infrastrukturingeniører. Terraform er det rigtige valg for multi-cloud og store teams. I er hverken.

Indfør IaC trinvist, ikke ved en rewrite:

1. **Wrap:** Eksportér en eksisterende ressource til Bicep med `az bicep decompile`. Resultatet er grimt. Commit det alligevel — det er sandhed, ikke æstetik.
2. **Extend:** Næste nye ressource skrives i Bicep fra starten. Den compliante vej er nu hurtigere end portalvejen for netop den ressource.
3. **Replace:** Når du alligevel rører en ClickOps-ressource, erstat den med Bicep. Over seks måneder eroderer ClickOps-andelen uden en stor migration.

Modulstruktur: et `infra/`-katalog med én `.bicep`-fil per logisk gruppe (app-service, sql, monitoring), en `main.bicep` der orkestrerer, og parametre i `.bicepparam`-filer per miljø. Mere end tre niveauer af moduler er over-engineering for 1-3 services.

**Drift detection:** Kør `az deployment group what-if` i en scheduled pipeline en gang om ugen. Den viser forskellen mellem din Bicep og det faktiske Azure-miljø. Er der drift, er det en ticket — ikke noget du fikser i portalen og glemmer.

## Deployment-strategier

Ved ni ansatte og 1-3 services behøver du ikke blue/green, canary eller traffic splitting. Du behøver én ting: **evnen til at rulle tilbage på under fem minutter.**

Den mindste levedygtige deploy-pipeline:

1. Build og test i CI
2. Deploy til staging slot (Azure App Service deployment slots — gratis i Standard-tier)
3. Smoke test mod staging
4. Swap staging til production
5. Monitorér i fem minutter
6. Swap tilbage hvis noget brænder

Feature flags (Azure App Configuration eller et simpelt `IFeatureManager`-lag) erstatter branching-strategier for feature-rollout. En feature flag er billigere end en langlivet branch: den koster én `if`-sætning, ikke en merge-konflikt.

**Databasemigrationer under zero-downtime deploys** er det ene sted, hvor det bliver svært for alvor. Mønsteret hedder expand-migrate-contract:

| Fase | Hvad der sker | Hvem der er i produktion |
|---|---|---|
| Expand | Tilføj ny kolonne/tabel, begge versioner af koden kan køre | Gammel kode |
| Migrate | Backfill data, deploy ny kode der skriver begge steder | Ny kode |
| Contract | Fjern gammel kolonne/kode, opryd | Ny kode |

Reglen: deploy koden **før** migrationen kræver den. Aldrig omvendt. Enhver migration der kræver nedetid er et designproblem, ikke et driftsproblem. Og test migrationen mod en kopi af produktionsdata, ikke mod en tom database — forskellen er der, problemerne bor.

## SRE for et lille team

Google SRE er skrevet til teams med 50+ ingeniører. Du skal stjæle tre koncepter og ignorere resten.

**Error budgets der virker ved jeres størrelse.** En SLO på 99,5% tilgængelighed giver ca. 44 minutters nedetid om måneden. Det er et budget du kan bruge: er budgettet brugt op, fryser du deploys og fikser stabilitet. Er det halvt fyldt, deployér oftere. Error budgettet er det eneste argument for at sige "vi stopper features og fikser tech debt" der virker på en stifter: det er et tal, ikke en mening.

**On-call der ikke brænder tre mennesker ud.** Til tre udviklere: én uge primær, de andre to sekundære, rotation hver uge. Alarmer kun på **kundesynlige symptomer**, aldrig på årsager. Realistisk: 0-2 alarmer om ugen for en B2B SaaS med normal trafik. Mere end det, og dine alarmer er forkert kalibreret, ikke dit system. Brug Azure Monitor action groups med SMS eller Teams-webhook. PagerDuty er en løsning på et koordinationsproblem, I ikke har endnu.

**Runbooks som eksekverbar dokumentation.** En runbook er ikke en wiki-side — det er en checkliste en stresset person kan følge kl. 02.00. Format: symptom, verifikation (KQL-query der bekræfter problemet), afhjælpning (trin med copy-paste-kommandoer), og eskalering (hvem der ringes op). Gem dem i repoet, ikke i en wiki — de skal reviewes i PR'er. Start med tre: "servicen svarer ikke", "databasen er fuld", "et certifikat er udløbet". Tilføj én efter hver rigtig hændelse.

**Toil-budgettet.** Toil er arbejde der er manuelt, repetitivt, automatiserbart, taktisk og uden varig værdi. Mål det: før en log over manuelt driftsarbejde i to uger. Er mere end 30% af din tid toil, er automatisering den højest prioriterede arkitekturopgave — uanset hvad backloggen siger. Det mest givtige enkelttiltag: automatisk oprettelse af en incident-ticket når en alarm fyrer, med link til den relevante runbook.

## Platform engineering mindset

Platform engineering er ikke et team, du bygger — det er en tænkemåde, du anlægger. Spørgsmålet er: "hvad kan jeg gøre én gang, så det er rigtigt for alle næste gang?"

**Golden paths, ikke golden cages.** En golden path er den anbefalede måde at gøre noget — deploy en service, oprette en database, konfigurere monitoring — pakket som en template, en CLI-kommando eller et Bicep-modul. Den er hurtigere end alternativet, ikke obligatorisk. Tvang producerer workarounds; bekvemmelighed producerer adoption.

Hos jer er golden paths tre ting:

1. **En service-template** med pipeline, Bicep, health endpoint, OTel-instrumentering og Testcontainers fra dag ét. `dotnet new` med en custom template, eller et template-repo på GitHub. Prisen: en dags arbejde. Gevinsten: hver ny service starter compliant i stedet for at blive rettet bagefter.
2. **En `infra/`-mappe** med Bicep-moduler for de ressourcer I faktisk bruger: App Service, Azure SQL, Key Vault, Application Insights. Ikke et internt NuGet-feed med abstraktioner — en mappe med filer folk kopierer og tilpasser.
3. **En "sådan gør vi"-side** på maks to A4 med links til templates, pipelines og runbooks. Mere end to sider, og ingen læser den.

**Hvornår du bygger en platform vs. hvornår du skriver dokumentation:** Hvis tre mennesker gør det samme manuelt mere end én gang om måneden, automatisér det. Hvis det sker sjældnere, skriv en checkliste. En platform til tre udviklere er en mappe med scripts og templates, ikke et Backstage-setup.

**Self-service infrastruktur** ved jeres størrelse er et parametriseret Bicep-modul med en pipeline-trigger: commit en `.bicepparam`-fil, og miljøet provisioneres. Ingen Terraform Cloud, ingen Pulumi, ingen intern portal. Simpelheden er featuren.

## Ressourcer

| Prioritet | Ressource | Timer | Hvad du henter | URL |
|---|---|---|---|---|
| Kerne | Accelerate (Forsgren, Humble, Kim) — kun Del 1 om DORA-metrikker | 4-5 | De fire nøglemetrikker og hvorfor de korrelerer med organisatorisk performance. Læs ikke Del 2 om kultur endnu | https://itrevolution.com/product/accelerate/ |
| Kerne | Team Topologies (Skelton & Pais) — kap. 1-4 | 5-6 | Stream-aligned, platform, enabling, complicated-subsystem. Ved ni ansatte er I ét stream-aligned team. Resten er viden om hvad der skal ske ved 20+ | https://teamtopologies.com/book |
| Kerne | Google SRE Book kap. 3-4, 6, 11 (gratis online) | 4-5 | Error budgets, toil, on-call. Spring kap. om Borg over | https://sre.google/sre-book/table-of-contents/ |
| Kerne | Bicep-dokumentation: modules, deployment stacks, what-if | 4 | IaC-fundamentet. Læs docs, ikke blogposts — de er bedre | https://learn.microsoft.com/azure/azure-resource-manager/bicep/ |
| Kerne | GitHub Actions: reusable workflows, caching, security hardening | 3-4 | Pipeline-arkitektur. Eller Azure Pipelines YAML reference, hvis I er der | https://docs.github.com/actions |
| Støtte | Azure DevOps vs. GitHub sammenligning | 2 | Beslutningsgrundlag, ikke feature-liste. MS's egen migreringsguide er den ærligste kilde | https://learn.microsoft.com/azure/devops/migrate/migrate-from-azure-devops-to-github |
| Støtte | DORA Quick Check | 0,5 | Baseline-måling af jeres fire metrikker lige nu. Gentag kvartalsvis | https://dora.dev/quickcheck/ |
| Støtte | Azure deployment slots og swap-dokumentation | 2 | Zero-downtime deploy-mekanikken for App Service | https://learn.microsoft.com/azure/app-service/deploy-staging-slots |
| Senere | Platform Engineering on Kubernetes (Salatino) — kun kap. 1-2 | 3 | Hvad platform engineering er, abstraheret fra Kubernetes. Resten er irrelevant for jer | https://www.manning.com/books/platform-engineering-on-kubernetes |

**Fravalgt bevidst:** Kubernetes i enhver form (I har 1-3 services, App Service er rigeligt), Backstage/Port/Cortex (interne udviklerportaler til tre udviklere er satire), ArgoCD/Flux (GitOps for Kubernetes I ikke har), Terraform i dybden (Bicep er det rigtige for jer, skriv en ADR), og HashiCorp Vault (Azure Key Vault dækker jer).

## Tre spikes med fysisk output

### D-1 — CI/CD fra nul til mål pipeline (2 uger, ~20 t)

Byg en komplet pipeline for én service: build, test, SBOM, deploy til staging slot, smoke test, swap til produktion, rollback-mekanisme. Mål varigheden af hvert trin. Optimer til under fire minutter. Dokumenter hvad du testede i CI, hvad du deferred, og hvorfor.

**Output:** Pipeline-kode i repoet, ADR "hvad vi tester i CI og hvad vi ikke gør" med tidsbesparelse per fravalg, baseline-måling af de fire DORA-metrikker (deployment frequency, lead time, change failure rate, time to restore), og en dokumenteret rollback du har udført mindst én gang.

**Måling:** Pipeline-varighed under 4 min i p90. Rollback under 5 min. Begge reproducerbare.

### D-2 — Infrastructure as Code: fra ClickOps til Bicep (2 uger, ~22 t)

Tag én eksisterende Azure-ressourcegruppe og wrap den i Bicep. Eksportér, opryd, parametrisér per miljø, sæt drift detection op som scheduled pipeline. Deploy derefter én ny ressource udelukkende via Bicep og mål tidsforskellen mod portalvejen.

**Output:** `infra/`-mappe i repoet med modulstruktur, ADR "Bicep over Terraform — og hvornår vi genovervejer" med konkrete kriterier for genovervejelsesbetingelsen (multi-cloud, team over 15, Terraform-kompetence i teamet), drift-rapport fra den første scheduled kørsel, og ClickOps-skatteberegning: timer/måned brugt på "hvad har vi kørende"-spørgsmål før vs. efter.

**Måling:** Nul ClickOps-ændringer i den wrappede ressourcegruppe i fire uger. Tid til "hvad har vi kørende?" under 2 minutter.

### D-3 — SRE-fundamentet: error budget, runbooks, on-call (2 uger, ~20 t)

Definér SLO'er for én service (fra modul 06). Beregn error budget. Byg tre runbooks for de tre hyppigste fejlscenarier. Sæt on-call-rotation op med Azure Monitor action groups. Provokér derefter mindst to af de tre scenarier og kør runbook'en under tidspres. Mål tid-til-detektion og tid-til-mitigering separat.

**Output:** SLO-dokument med error budget-beregning, tre runbooks i repoet (ikke i en wiki), on-call-rotationsplan, og en log over de provokerede hændelser med tre tidsstempler: fejlens opståen, din detektion, din mitigering. Skriv et kort retrospektiv for hver.

**Måling:** Tid fra alarm til mitigering under 15 minutter for kendte scenarier med runbook. Runbook følgelig for en kollega der ikke skrev den (test det).

## På jobbet: at indføre uden mandat

Ni ansatte. Ingen change advisory board, ingen platform-team, ingen der ejer CI/CD. Det er en fordel, ikke en hindring.

- **Start med pipeline-varighed.** Mål den, vis tallet, forkort den. Ingen spørger om lov til at gøre et build hurtigere. Det er det billigste synlighedskort i hele modulet, og det ændrer alle udvikleres dag.
- **Wrap den næste Azure-ressource i Bicep.** Ikke alle — den næste. Commit filen. Næste gang nogen spørger "hvad har vi i den ressourcegruppe?" siger du "læs `main.bicep`". Tredje gang gør folk det selv.
- **Skriv den første runbook efter den næste rigtige hændelse.** Ikke før — runbooks skrevet uden en hændelse bag er fiktion. Hændelsen giver dig både indholdet og mandatet. "Jeg skrev ned hvad jeg gjorde, så vi er hurtigere næste gang" er et ja ingen nægter.
- **Foreslå on-call som en fordeling af ansvar, ikke som en byrde.** "Hvem ringer kunden, hvis det går ned lørdag?" er spørgsmålet der åbner samtalen. Svaret er næsten altid "det ved vi ikke", og det er dit mandat.
- **Mål DORA-metrikker kvartalsvist med DORA Quick Check.** Vis dem til stifteren uden kommentar. Tallene argumenterer for sig selv. Foreslå aldrig en "DevOps-transformation" — foreslå én konkret forbedring med et forventet tal.
- **Tag den kedelige CI-ticket.** Flaky tests, langsom restore, manglende caching. Det er platform engineering forklædt som vedligeholdelse. Det giver dig legitim adgang til alles pipelines.

## Faldgruber

1. **At over-engineere CI/CD.** En pipeline med matrix builds, tre miljøer, approval gates, parallel test sharding og custom Actions for tre udviklere og én service er en arkitekturfejl — bare fordi den lever i YAML og ikke i kode. Start med det simpleste der deployer korrekt. Tilføj kompleksitet når et målt problem kræver det.
2. **At bygge et "platform-team" ved ni ansatte.** Platform engineering er en tænkemåde, ikke en organisationsstruktur. En mappe med Bicep-moduler og en service-template er en platform. Et Backstage-setup med plugins er et hobbyprojekt.
3. **Kubernetes uden behov.** App Service deployment slots giver dig zero-downtime deploys, autoscaling og slot-swap for en brøkdel af den kognitive og operationelle omkostning. Kubernetes er svaret på et problem, I ikke har. Genovervejelsesbetingelse: mere end 10 services, eller workloads der kræver GPU, custom scheduling eller multi-cloud. Skriv det i en ADR og dater det.
4. **At vælge Terraform "fordi alle bruger det".** Terraform er det rigtige for multi-cloud og store teams. Bicep er det rigtige for et lille Azure-team. At vælge det populære over det passende er det modsatte af arkitektur.
5. **At automatisere alt på én gang.** IaC-migration er en gradvis proces. At forsøge en big bang-konvertering af al infrastruktur til Bicep ender med en halvfærdig, utestet kodebase ingen stoler på. Wrap, extend, replace — i den rækkefølge.
6. **At forveksle deploy-frekvens med hastighed.** Høj deploy-frekvens med høj change failure rate er kaos, ikke DevOps. DORA måler fire ting, ikke én.
7. **Prematur incident management-tooling.** PagerDuty, Opsgenie og Rootly løser koordinationsproblemer mellem mange teams. I har ét team. Azure Monitor action groups, en Teams-kanal og en runbook i repoet er nok.
8. **At bygge golden paths ingen bruger.** En template er kun en golden path, hvis den er hurtigere end alternativet. Mål tid-til-deployment for template-vejen vs. den manuelle vej. Er forskellen under 20%, er templaten ikke god nok.

## Kompetenceport

Du består porten, når du har fysisk bevis for mindst 8 af 10.

| # | Kriterium | Beviset |
|---|---|---|
| 1 | Du har en pipeline der bygger, tester og deployer en service til produktion på under 4 minutter, og du kan vise fem på hinanden følgende deploys uden fejl | Pipeline-historik med tidsstempler |
| 2 | Du har udført en rollback under tidspres og kan vise tidsforløbet: fejl detekteret → beslutning → rollback fuldført under 5 minutter | Incident-log med tre tidsstempler |
| 3 | Mindst én Azure-ressourcegruppe er fuldt beskrevet i Bicep, og drift detection har kørt i mindst fire uger uden uforklaret drift | Bicep-repo plus drift-rapporter |
| 4 | Du kan deploye en ny instans af en service fra nul til kørende i et nyt miljø på under 30 minutter med kun Bicep og pipeline — ingen portalklik | Demonstreres live |
| 5 | Tre runbooks i repoet, og mindst én af dem er fulgt af en anden person end dig selv med dokumenteret resultat | Commit-historik og kollegaens feedback |
| 6 | Du kan tegne jeres deploy-flow fra commit til produktion på under 5 minutter og navngive hvert trin der kan fejle og hvad der sker når det gør | Tegnet foran en fremmed |
| 7 | Error budget er defineret, og du kan sige, med tal, om I har råd til en risky deploy denne uge | SLO-rapport med aktuel burn |
| 8 | Pipeline-varighed er målt som metrik over mindst otte uger, og du kan vise en forbedring du selv foretog med før/efter-tal | Dashboard og commit |
| 9 | Du har indført mindst ét artefakt fra dette modul i LeanLinkings faktiske workflow — en runbook, en Bicep-fil, en forbedret pipeline, en on-call-aftale | Artefaktet i brug, ikke bare committed |
| 10 | Du kan navngive jeres fire DORA-metrikker med tal og sige hvilken der er svageste, og hvad du ville gøre ved den | Baseline-måling plus forslag |
