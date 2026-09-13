# 09. Domæneekspertise: rygraden i hele strategien

> Du har ingen arkitekt at spørge, ingen arkitektstige at klatre op ad, og 10-15 timer om ugen. Det ene sted hvor du kan bygge et forspring ingen kan tage fra dig, er domænet. Du sidder allerede i tre af branchens sværeste problemklasser: heterogen ERP-integration, versioneret metrikberegning på beskidte data, og dokument- og certifikatlivscyklus. Du skal ikke lede efter arkitekturproblemer. Du skal holde op med at behandle dem som tickets. Og du kan starte i morgen uden at spørge nogen om lov.

## Forskellen på lokal viden og domæneekspertise

Lokal viden er "sådan gør vi". Domæneekspertise er "sådan gør vi, og årsagen er, og det koster os følgende". Lokal viden ophører med at have værdi den dag du skifter job. Domæneekspertise følger med. Det er sektionens negative kontrol: besvarer du et domænespørgsmål med den første formulering og ikke den anden, har du bygget vane, ikke kompetence.

Den anden halvdel er at domæneekspertise **forværrer** din største risiko. Jo mere du ved om leverandørkæder, jo færre kan modsige dig, og jo mere selvsikker bliver du i tekniske valg ingen kalibrerer. Derfor er hvert artefakt her skriftligt: skriftlige artefakter er det eneste du kan lægge foran en fremmed.

## Domænets syv områder

Du skal kunne tegne dem på en tavle uden noter, placere enhver ticket i én af kasserne og sige hvilken naboklasse den påvirker. Det alene lægger dig foran de fleste udviklere i huset.

| # | Område | Kernespørgsmålet | Hvor arbejdspladsen ligger |
|---|---|---|---|
| 1 | Sourcing | Hvad køber vi, af hvem, hvorfor. Kategoristrategi, Kraljic | Berøres via segmentering og supplier strategy |
| 2 | Onboarding og kvalificering | Kan denne leverandør overhovedet blive leverandør, og har vi papirer på det | Kerne i RELATIONS |
| 3 | Compliance og dokumentation | Certifikater, politikker, erklæringer og deres livscyklus | Kerne |
| 4 | Audit | Planlagte og udløste revisioner, findings, CAPA-lukning | Kerne |
| 5 | Performance | OTIF, PPM, RFT, claims, scorecards, business reviews | Kerne, og firmaets tungeste beregning |
| 6 | Risiko | Finansiel, geografisk, sanktioner, koncentration, single-source, ESG | Risk og quality control |
| 7 | Udvikling og exit | Forbedringsplaner, eskalation, afvikling | Supplier development |

Produktet dækker tydeligt 2 til 7. Kortet viser også de hvide pletter — område 1 og 7 er hvor et modul enten mangler eller er tyndt, og det er en samtale du kan starte med en Product Manager når du kan tegne kortet.

## De fire måletal, og fælden i det første

OTIF (On Time In Full — andelen af ordrer leveret både på aftalt dato og i fuld mængde; fejler den ene test, fejler hele linjen). PPM (defekte dele pr. million). RFT (Right First Time). Claims cost (omkostningen ved reklamationer, aggregeret pr. leverandør). Du skal kunne sige dem i et møde uden at slå op.

Vigtigere er fælden: **OTIF er ikke ét tal.** Tre valg afgør resultatet, og alle tre er lovlige:

| Valg | Mulighederne | Konsekvens |
|---|---|---|
| Hvilken dato tæller | Kundens ønskede dato, leverandørens oprindelige løfte, eller seneste genløfte | Scorer man mod genløfter, kan en leverandør skride tre gange og stadig levere 98 procent |
| Hvad er "til tiden" | Dagen præcis, eller plus/minus to dage | Flytter typisk flere procentpoint |
| Hvilket niveau | Ordre eller linje | Én kort linje fælder en ordre på 40 linjer: 86 mod 97,5 procent |

Kan du regne et eksempel igennem og få tre tal ud af samme datasæt, har du forstået domænet. Kan du kun gengive definitionen, har du læst om det.

## 90-dages plan: bliv husets mest domænekyndige person

Størstedelen ligger i **arbejdstiden** og koster ikke af dine 10-15 timer. Det er pointen: arbejdet og øvebanen skal fodre hinanden, ikke konkurrere. Kun kolonnen "egne timer" trækker på ugebudgettet.

| Uge | Handling | Arbejdstid | Egne timer |
|---|---|---|---|
| 1 | Læs hele arbejdsgiverens eget site på én aften. Notér hvert fagord: segmentering, kvalificering, governance, scorecard, corrective action, claim | — | 3 |
| 1 | Afklar headcount ved frokosten: CVR siger ni ansatte og syv årsværk, aggregatorer antyder 20-23 på to kontinenter (uverificeret). Du skal vide hvem der rører kodebasen | 0,5 | — |
| 2-3 | Begrebsdivergens-tabellen: sådan siger kunden det, sådan skriver marketing det, sådan hedder klassen. I et system med ti års historik finder du tyve rækker der ikke stemmer | 6 | 2 |
| 2-4 | Peppol BIS 3: Ordering og Despatch Advice — datamodel, kodelister, valideringsregler, release notes | — | 7 |
| 3-4 | Tegn systemarkitekturen som den ER: integrationer, datastrømme, hvad der kører om natten. Bed husets dygtigste udvikler om at rive den i stykker | 8 | 2 |
| 5-6 | Læs supportkøen seks måneder **bagud**. Kategorisér, tæl, find de tre største grundårsager, estimer timer pr. årsag | 8 | 2 |
| 5-7 | Ariba Supplier Management-API'erne. Notér de to bevidste separationer og gæt begrundelsen | — | 6 |
| 6-8 | Byd ind på drift: deployments, databasevedligehold, incident-opfølgning. Ingen i et nimandsfirma siger nej til det tilbud | løbende | — |
| 7-8 | Coupas cXML-materiale plus GACI CertSearch-dokumentationen (IAF og ILAC fusionerede til GACI 1. januar 2026) | — | 5 |
| 8-12 | Lyt med på kundeopkald. Sig hvad du vil have ud af det og hvad du giver igen: du vil forstå hvordan de bruger scorecards, og du skriver et referat af de tekniske implikationer. Referatet er betalingen. Mål: ti samtaler på tolv måneder | 6 | 2 |
| 9-12 | Spike 1 (certifikatgyldighed som tilstandsmaskine) | — | 20-25 |
| Løbende | ADR på hver ikke-triviel ticket. Én side: kontekst, muligheder, valg, konsekvenser, faldsbetingelser | 1/uge | — |
| Løbende | Kalibreringslog: hver gang produktionen modsiger din forventning — "jeg troede X, det var Y, årsagen var Z" | 0,5/uge | — |

Egne timer over 90 dage: cirka 50-55, altså 4-5 om ugen. Resten af budgettet går til de tekniske spor plus mindst ét eksternt kalibreringspunkt om måneden.

Tre spørgsmål åbner domænet hurtigst. Til salg: hvilken funktion lukker handlen, og hvilken indvending taber vi på. Til stifteren: hvilken arkitekturbeslutning fortryder du. Til en kunde: **hvad gør I stadig i Excel ved siden af vores system**. Det sidste er planens mest værdifulde spørgsmål — Excel-arbejdet er produktets ufuldstændighed, kortlagt af kunden selv, gratis.

## Ressourcetabel

| Ressource | Prio | Tid | Hvad du henter — og hvad du springer over |
|---|---|---|---|
| Peppol BIS v3 ([docs.peppol.eu/poacc/upgrade-3/](https://docs.peppol.eu/poacc/upgrade-3/)) | 1 | 6-8 t | Konsensusforhandlede modeller for Order, Order Response, Despatch Advice. Release notes viser hvordan man versionerer en model uden at brække halvdelen af Europa. Spring Access Point-drift, AS4, SMP/SML og fakturering over |
| Arbejdsgiverens egne case studies og guides ([leanlinking.com/case-studies/](https://leanlinking.com/case-studies/)) | 1 | 3 t | Marketing har allerede skrevet firmaets domænemodel ned. Spring intet over |
| SAP Ariba API-dokumentation ([help.sap.com/docs/r/product/ARIBA_APIS/latest/en-US](https://help.sap.com/docs/r/product/ARIBA_APIS/latest/en-US)) | 1 | 5-6 t | Hele onboarding-modellen: supplier data, questionnaires, statusskift. Supplier data ligger bevidst uden for Operational Reporting, og Analytical er skilt fra Operational. Spring Sourcing, Contract og BTP over |
| GACI CertSearch API (tidl. IAF CertSearch; IAF + ILAC → GACI pr. 1. jan 2026) ([iafcertsearch.org/services/api-certificate-search](https://www.iafcertsearch.org/services/api-certificate-search)) | 1 | 2 t | Beviset for at udløbsdato ikke er sandhed: alarmer ved suspension og tilbagetrækning markedsføres som noget andet end udløb. Notér dækningshullerne. Verificér om domænet er migreret til gaci.org |
| EDPB Guidelines 02/2025 plus CEF-rapporten om ret til sletning (vedtaget 10. februar 2026) | 1 | 4-5 t | Det kryptografiske sletningskriterium, og backup som det svageste led. Spring blockchain-afsnittet over |
| Designing Data-Intensive Applications, 2. udg., Kleppmann og Riccomini, marts 2026 | 1 | 2 t/uge i 4 mdr. | Fire-fem kapitler, ikke forfra: replikering, konsistens, batch mod stream, dataintegritet. Spring konsensusalgoritmer over |
| CIPS Intelligence Hub, Kraljic og supplier preferencing ([cips.org/intelligence-hub/...](https://www.cips.org/intelligence-hub/supplier-relationship-management/kraljic-matrix)) | 2 | 4-5 t | Indkøbernes sprog, gratis. Supplier preferencing er det spejlvendte perspektiv: hvordan ser leverandøren på os |
| GLEIF API ([gleif.org/en/lei-data/gleif-api](https://www.gleif.org/en/lei-data/gleif-api)) | 2 | 2-3 t | Eneste gratis kilde med en juridisk entitetsmodel inklusive ejerskabshierarki — nøglen til sanktionsscreening. Spring kommercielle berigelsestjenester over |
| OpenSanctions og FollowTheMoney ([opensanctions.org/docs/](https://www.opensanctions.org/docs/)) | 2 | 3-4 t | Hvordan man modellerer en verden hvor "hvad er en ting" ikke er indlysende. Virksomhedsbrug kræver licens |
| Coupa supplier integration ([docs.coupa.com/.../supplier-integration-resources](https://docs.coupa.com/en/supplier-documentation/coupa-for-suppliers/supplier-integration-resources)) | 2 | 3-4 t | Den modsatte filosofi af Ariba: kravet om OrderResponse inden for 60 sekunder er en SLA skrevet ind i protokollen |
| PostgreSQL 19, temporal tables ([postgresql.org/docs/19/ddl-temporal-tables.html](https://www.postgresql.org/docs/19/ddl-temporal-tables.html)) | 2 | 2-3 t | PG18 gav WITHOUT OVERLAPS og temporale FK'er med PERIOD, PG19 tilføjer FOR PORTION OF — men stadig ingen system-versionering. PG19 var i beta i sensommeren 2026 |

## Problemkataloget: hvad der faktisk er svært i domænet

Råmateriale, ikke en to-do-liste. Med dit timebudget bygger du realistisk seks til otte på tolv måneder.

| Problem | Kernehårdheden | Kompetence det træner |
|---|---|---|
| Certifikatgyldighed | Udløbsdato er ikke gyldighed | Domænemodellering, kildepræcedens |
| Idempotent ERP-indlæsning | Ingen stabil global leverandørnøgle | Integrationsarkitektur, anti-corruption layer |
| Append-only revisionsspor | Sporet skal overleve skemamigrationer | Kryptografisk integritet, skemaevolution |
| Bitemporal modellering | Hvad viste systemet indkøberen den 14. marts 2024 | Temporal modellering, platformevaluering |
| Sletning under legal hold | Tre indbyrdes modstridende krav, ingen løsning uden ulemper | Jura til arkitektur, nøglehåndtering |
| Scorecard-definitioner | Metrikken er politik, ikke kode | Event-tid mod behandlingstid |
| Regler som versioneret data | Lovgivning ændrer sig hurtigere end release-kadencen | Temporal gyldighed, forklarbarhed |
| AI-udtræk med bevisværdi | En konfidensscore er ikke bevis | Proveniens, probabilistik ude af beslutningsstien |

## Tre spikes med fysisk output

### Spike 1: Certifikatgyldighed som tilstandsmaskine (20-25 t)

ISO-certifikater kører treårige cyklusser med årlige surveillance audits. Et certifikat kan suspenderes midt i cyklussen — typisk med 90 dage til at lukke afvigelser — eller trækkes tilbage ved svig eller ulukkede major nonconformities, **uden at den trykte udløbsdato ændrer sig**. En model der siger `expiry_date > now()` er forkert på en måde der først opdages når nogen bliver sagsøgt.

Modellér tilstandene valid, suspended, withdrawn, expired, unknown, unverifiable plus tre felter: `last_verified_at`, `verification_source` og `source_trust_level`. Byg en præcedensmodel over tre kilder: akkrediteret register (høj tillid, delvis dækning), leverandør-uploadet PDF (lav tillid, fuld dækning), certificeringsorganets side (mellem). Byg ikke mod GACI's (tidl. IAF's) rigtige API — mock den mod den offentlige dokumentation.

**Output:** kørende model med tests for seks scenarier — normalt udløb, suspension med gyldig dato tilbage, ophævet suspension, tilbagetrækning, autoritativ kilde nede i 72 timer, to kilder uenige. Plus en to-siders ADR der begrunder præcedensmodellen og lister hvad akkrediterede registre **ikke** dækker (BRCGS, FSSC 22000, Sedex/SMETA, forsikringscertifikater) og hvad systemet gør der. Den svære del er ikke koden. Det er at turde modellere "vi ved det ikke" som en førsteklasses tilstand i stedet for at defaulte til valid.

### Spike 2: Idempotent indlæsning af leverandørstamdata fra N ERP-systemer (30-35 t)

Der findes ingen stabil global leverandørnøgle. Et SAP-vendornummer er unikt pr. company code, ikke pr. juridisk enhed — samme selskab optræder som fem leverandører i én kundes ERP. Dertil delvise payloads, ude-af-orden-ankomst hvor gårsdagens forsinkede opdatering overskriver dagens korrekte data, uklar slettesemantik og poison messages der blokerer køen.

Byg en pipeline med et anti-corruption layer der oversætter tre syntetiske ERP-eksportformater til én intern model. Idempotensnøgle af (tenant, kildesystem, kildenøgle). Håndtér gentagen levering, monoton versionsstempling mod ude-af-orden, feltniveau-merge i stedet for hel-objekt-overskrivning, og fravær der ikke betyder sletning.

**Output:** test-suite der beviser at ti gentagne afspilninger giver identisk sluttilstand, at omvendt rækkefølge giver samme resultat som korrekt, og at 20 procent korrupte rækker havner i en dead letter med en **forretningslæsbar** fejlbesked uden at blokere resten. Plus en ADR om hvorfor sletning er tombstone og ikke fravær.

### Spike 3: Scorecard-metrikker som versioneret, tenant-specifik politik (30-35 t)

Byg en scorecard-motor hvor metrikdefinitionen er versioneret data med gyldighedsperiode, ikke kode i en assembly. Implementér de tre OTIF-definitioner side om side på **samme** datasæt. Tilføj forsinkede ERP-posteringer der ankommer 30 dage efter periodeafslutning, og implementér begge svar: frosne scorecards med separat korrektionsnotat, mod fuld genberegning med lineage. Byg watermark-logik der afgør hvornår en periode er lukket nok til at offentliggøres.

**Output:** én tabel med tre lovlige OTIF-tal fra samme data — 86,5, 89,4 og 97,5 procent. Det er planens mest overbevisende enkeltartefakt, fordi enhver indkøbschef straks forstår hvorfor det er farligt, og enhver ingeniør straks har en mening. Plus begge korrektionsstrategier, en watermark-regel og en ADR om hvornår en score må ændre sig efter offentliggørelse.

## Faldgruber

- **At læse Evans' blå bog forfra.** Fem hundrede sider taktiske mønstre hvor dit behov er strategisk: bounded contexts, ubiquitous language, context mapping. Du giver op omkring side 200 og tror det er din skyld. Evans er opslagsværk — start med Khononovs Learning Domain-Driven Design (udgivelsesstatus uverificeret).
- **At bygge en generisk multi-tenant SaaS-boilerplate eller to-do-app.** Der findes tusind på GitHub, de demonstrerer ingenting, og de æder de timer der skulle være gået til domænespikes. Hentes problemet ikke fra leverandørkæde-, dokumentations- eller compliance-domænet, så lad være.
- **At bygge event sourcing på alt fordi du har hørt ordet audit trail.** Event sourcing løser rekonstruktion af tilstand, ikke bevisførelse. En append-only tabel med hash-kæde plus en bitemporal kernemodel er billigere og lettere at forklare til en revisor. Vælg gerne event sourcing — men skriv ned hvad du gav afkald på. Kan du ikke det, er svaret nej.
- **At læse konkurrenternes marketingsider i stedet for API-referencerne.** Fejlkodelisten fortæller hvad der går galt, pagineringen hvor store deres data er, feltnavnene hvilke begreber der overlevede ti års kundekrav.
- **TOGAF, ArchiMate og CIPS-certificering.** Bygget til organisationer med hundredvis af systemer og forandringsudvalg. Du har tre til fem udviklere. CIPS' gratis artikler giver 90 procent af sprogværdien for nul kroner.
- **At kalde en samtale for en Event Storming-workshop.** Booker du to dage og køber orange post-its, ligner du en der har læst en bog. Stil spørgsmålene ved kaffemaskinen og skriv resultatet ned.
- **At tro Kraljic-matricen er datamodellen.** Den er en samtaleramme fra 1983. Implementerer du den som fire faste kategorier, brækker den hos den første kunde der har fem.
- **At bygge før du har læst hvordan andre har løst det** — og omvendt: 30 timers læsning og to timers byggeri giver en kompetence der ikke kan verificeres.
- **At lade kataloget blive en to-do-liste.** Halvfærdige spikes tæller nul. Én færdig spike med målte tal og en ADR slår fire påbegyndte.
- **At tro at domæneekspertise alene giver arkitektkompetence.** Du kan blive den i Danmark der ved mest om compliance i leverandørkæder og stadig træffe dårlige tekniske valg, fordi ingen på arbejdet kan modsige dig.
- **At regne med at regulatorisk viden holder.** På tolv måneder blev CSDDD's anvendelsesområde skåret cirka 70 procent ned, EUDR udskudt igen og AI Act's højrisiko-forpligtelser skubbet halvandet år. Genlæs primærkilderne hvert halve år. Næsten ingen udviklere gør det.

## Sådan ved du at du kan det

| Måned | Test | Bestået når |
|---|---|---|
| 3 | **Tavletesten.** Du tegner de syv områder uden noter og placerer modulerne. En kollega tager tilfældige tickets fra backloggen | Du rammer rigtigt på 8 ud af 10, inklusive naboområdet den påvirker |
| 3 | **OTIF-testen.** Du forklarer uden hjælpemidler hvorfor tre lovlige OTIF-tal kan komme ud af samme datasæt | Du regner et konkret eksempel igennem og får forskellige tal frem, og kan navngive de tre valg |
| 4 | **Certifikattesten.** Treårig ISO-cyklus, surveillance audits, suspension mod tilbagetrækning, tre certifikattyper uden for akkrediterede registre | En ikke-teknisk kollega fra salg kan gentage argumentet bagefter |
| 5 | **Kodebase-divergensen.** Mindst 15 begreber hvor kundens sprog, marketingsproget og klassenavnet ikke stemmer, med hvad rettelsen koster | Kollegerne kan straks se om rækkerne er rigtige — og de er |
| 6 | **Supportkø-analysen.** Seks måneders sager kategoriseret og talt, tre største grundårsager med timeestimat | Tallene overrasker mindst én kollega — det gør de, fordi ingen har talt før |
| 6 | **Konkurrent-API-notatet.** Maks fire sider om hvordan Ariba, Coupa og Peppol modellerer samme begreb, med tre arkitektoniske beslutninger og deres sandsynlige begrundelse | Begrundelserne er falsificerbare og kan udfordres af enhver der læser samme dokumentation |
| 7 | **Den offentlige tekst.** Én publiceret artikel med nok substans til at nogen kan være uenig | Mindst én fagligt kvalificeret fremmed har givet substantiel modstand. Nul kritik er en dumpet test |
| 9-10 | **Domænedelen af kompetenceporten.** To færdige spikes fremlagt for en ekstern arkitekt der ikke kender virksomheden | Du forklarer problemet uden intern jargon, fremlægger målte tal, har en ADR pr. spike med et afsnit om hvad løsningen ikke løser, og besvarer tre kritiske spørgsmål uden "sådan gør vi". Bedømmeren siger at afvejningerne er rimeligt forstået — ikke at løsningen er rigtig |
| 10 | **Aktualitetstesten.** CSDDD efter Omnibus I, EUDR's to datoer, NIS2 i Danmark, AI Act efter Digital Omnibus | 100 procent korrekt. Der findes ingen delvis kredit på fakta |
| Løbende | **ADR-tællingen.** 50 ADR'er på tolv måneder | Hvert dokument har et afsnit om hvad der ville få os til at ændre beslutningen. Mangler det, er det en begrundelse, ikke en beslutning |
| Løbende | **Kalibreringsloggen.** 30 poster af typen "jeg troede X, virkeligheden var Y, årsagen var Z" | Faldende hyppighed over året — det eneste mål på dømmekraft du ikke kan spille |
