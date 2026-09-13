# C03 — Azure-regningen tredoblet

| | |
|---|---|
| **Type** | Kostarkitektur og forhandling |
| **Primært modul** | 03 — Azure-arkitektur: fra bruger til designer af platformen |
| **Sekundære moduler** | 06 (Observability), 10 (Produkt og leverance), 07 (Governance) |
| **Timebox** | 6 timer, hård. Præmisskiftet lægges oveni og må koste maks. 45 minutter ekstra |
| **Sværhedsgrad** | 4 af 5. Let på teknik, hård på tal og på at skulle sige nej til den der betaler din løn. Giver mening i **måned 6-9**: før måned 6 har du hverken målte `_BilledSize`-tal fra O-4 eller egne compute-priser fra Spike 2, og så bliver kostmodellen citerede blogtal. Efter måned 10 er den for nem, fordi enhedsøkonomi-spiken i modul 12 har foræret dig metoden. Kør den igen i måned 11 med samme rubrik og sammenlign |
| **Afleveringsformat** | Otte artefakter: regningsanatomi (1 side + regneark), besparelseskatalog (maks. 2 sider), notat til stifteren (præcis 1 side, ikke-teknisk), ADR (maks. 1,5 side, MADR-minimal), enhedsøkonomi (regneark + 0,5 side), bestyrelsesbilag (1 side + én graf), guardrails (0,5 side), selvvurdering (0,5 side). I alt maks. 7 sider brødtekst, 2 regneark og én graf |

> Personerne er de samme opdigtede som i C01: Jens (stifter), Katrine (salg), Thomas (har bygget det meste), Rasmus (drift og produktionsadgang). Kunden Fjordhus og investoren er opdigtede. Alle kronebeløb i casen er konstruerede, men i den størrelsesorden en dansk SaaS-virksomhed med ni ansatte reelt ligger i. **Azures listepriser er ikke oplyst** — dem henter du selv via Retail Prices API, og gætter du, mærker du gættet som gæt i regnearket.

## Situationen

Torsdag den 10. september 2026, kl. 09.15. Lone i bogholderiet sender hver måned Azure-fakturaen videre uden kommentar. I går sendte hun den med en.

Fakturaen for august lyder på **116.412 kr. ekskl. moms**. I februar var den 38.204. Jens har regnet baglæns i hovedet, og han er kommet frem til at platformen nu koster mere end en fuldtidsudvikler. Han stod ved dit bord kl. 08.50 og sagde: "Vi skal have den halveret. Ikke skåret lidt — halveret. Og jeg har allerede sagt det til Peder."

Peder Lindhardt er den eksterne investor. Han ejer 24 procent, sad tidligere som økonomidirektør i et logistikhus, og han er den ene af tre i bestyrelsen. Jens ringede til ham tirsdag aften og sagde at regningen ville være halveret inden bestyrelsesmødet. Mødet ligger **onsdag den 30. september kl. 13.00**.

Fjordhus Retail Group A/S gik i luften den 2. juni. 340 byggemarkeder i Danmark, Sverige og Norge, 7.800 leverandørrækker i deres SAP-vendor master, en kvalitetsafdeling der kører scorecards, surveillance audits og CAPA-opfølgning i RELATIONS. Det er husets største kunde. Jens' udlægning i morges var kort: "Det er Fjordhus der har tredoblet den. Vi vidste godt de var store, men ikke at de var *så* dyre. Og de betaler os næsten en femtedel af hvad vi tjener, så det hænger ikke sammen."

Han har også allerede en løsning. Thomas sagde i mandags at Application Insights alene koster over 40.000 om måneden, og Jens hæftede sig ved det: "Kan vi ikke bare slukke Application Insights? Vi har klaret os uden i ti år. Vi kan altid tænde den igen hvis der er noget."

Der findes et notat fra marts hvor nogen har regnet ud at platformen kostede 11.400 kr. om måneden. Jens husker det tal. Ingen kan lige finde notatet, men Thomas mener det var Rasmus der lavede det.

Der er ingen tags på ressourcerne. Der er én budget-alert, sat til 45.000 kr., og den fyrede den 19. juli til `info@leanlinking.dk` — en fællespostkasse som Katrine tømmer når hun har tid. Ingen har set beskeden. Der er aldrig blevet fordelt en krone Azure-forbrug ud på en kunde, og der findes ingen model der kan gøre det.

Rasmus er den eneste ud over Jens med produktionsadgang. Han er 60 procent booket på restarbejdet i Fjordhus' ERP-integration frem til den 15. oktober. Thomas kan røre koden, men rører nødigt infrastruktur.

Du har seks timer. Jens vil have "noget på skrift jeg kan læse i weekenden" — han har ikke bedt om et design, han har bedt om et beløb. Han har heller ikke spurgt hvad du synes om at slukke Application Insights. Han har spurgt hvornår du kan gøre det.

## Det du skal aflevere

| # | Artefakt | Format | Krav der ikke kan forhandles |
|---|---|---|---|
| 1 | **Regningsanatomi** | 1 side + regneark | Augustregningen brudt op på mindst otte målertyper, hver med kr./md., andel af totalen og vækstfaktor mod februar. Plus en attribution af **stigningen**: hvor mange kroner skyldes hvad, med et spænd i procentpoint pr. post |
| 2 | **Besparelseskatalog** | Maks. 2 sider, tabel | Mindst syv indgreb. Hver med: sparet kr./md. **med spænd**, engangspris i både udviklerdage og kroner, hvad vi mister (indsigt, evne eller kontraktuel dækning), dage til effekt, og om det kan rulles tilbage. Rangeret på kroner-per-risiko, ikke på kroner |
| 3 | **Notat til Jens** | Præcis 1 side | Nul jargon. Skal indeholde: hvad hans eget forslag faktisk ville spare (ét tal), hvad det ville koste (ét tal og én kontraktuel konsekvens), hvad vi gør i stedet, og hvad halveringen koster. To muligheder, én anbefaling. Læsbar på fire minutter |
| 4 | **ADR** | Maks. 1,5 side, MADR-minimal | Rækkefølgen af indgreb som beslutning. Mindst to navngivne afviste alternativer, hvert afvist på **én målbar akse med et tal**. Afsnittet "Dette ville få os til at vælge om" med mindst tre betingelser, hver med tærskel og enhed |
| 5 | **Enhedsøkonomi** | Regneark + 0,5 side | Omkostning pr. tenant mod betaling pr. tenant for de fem største og fem mindste. Metoden skal stå eksplicit — hvilke proxies, hvilke antagelser — og **usikkerheden skal angives i procentpoint**, ikke som forbehold i prosa |
| 6 | **Bestyrelsesbilag** | 1 side + én graf | Forecast for oktober, november og december i tre scenarier, i kr./md. med spænd. Grafen viser kr./md. pr. tenant, ikke totalen |
| 7 | **Guardrails** | 0,5 side | 2-4 regler der gør gentagelsen usandsynlig. For hver: hvad den koster den rigtige vej i minutter, og hvem der ejer den med navn og udløbsdato |
| 8 | **Selvvurdering** | 0,5 side | Hvilke af dine tal er målte, hvilke er hentede, hvilke er gættede — og hvilket gæt bærer mest af anbefalingen |

**Artefakt 1 og 5** er dem der har tal med angivet usikkerhed. **Artefakt 3** er det ikke-tekniske, og det eneste af de otte Jens reelt læser. **Mindst ét indgreb i artefakt 2 skal have en engangspris over 15.000 kr. eller over fem udviklerdage** — og den pris skal også stå i artefakt 3, ikke kun i regnearket. Et katalog hvor alt er gratis er ikke et katalog, det er en ønskeseddel.

## Skjulte oplysninger

Du må kun læse svaret på et spørgsmål, du **faktisk har skrevet ned** før du begyndte at foreslå indgreb. Læser du hele tabellen først, har du ikke lavet casen — du har læst en løsning, og du kan ikke score over 1 på K1 og K2.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Hvordan fordeler augustregningen sig på målertype, mod februar? | Alle tal afrundet til nærmeste 100 kr., så summen rammer 4-12 kr. ved siden af fakturaen. Log Analytics + App Insights **4.900 → 41.300**. Azure SQL (elastic pool + én dedikeret db) 11.400 → 23.800. App Service Plans (2 prod, 1 test, 1 dev) 7.600 → 14.200. Blob storage + transaktioner 2.900 → 8.700. Backup og long-term retention 1.800 → 6.400. Egress 900 → 5.100. Front Door Standard 2.100 → 2.100. Service Bus + Functions 1.700 → 4.900. Defender for Cloud (fem planer) 2.400 → 5.200. Øvrigt (Key Vault, DNS, forældreløse diske, ubrugte offentlige IP'er, snapshots) 2.500 → 4.700 |
| 2 | Hvor mange GB faktureret ingest, og hvilke tabeller? | **2.180 GB** faktureret i august mod 265 GB i februar. `AppTraces` 61 %, `AppDependencies` 18 %, `AppRequests` 9 %, `AppExceptions` 4 %, resten 8 %. Af `AppTraces` kommer **74 %** fra én logger-kategori: `Relations.Integration.Idoc`, som logger hele IDoc-payloaden pr. leverandørrække |
| 3 | Blev der ændret noget i juni eller juli? | To ting, begge udokumenterede. **14. juni kl. 22.10:** Thomas satte `Logging:LogLevel:Default` til `Debug` i App Configuration under en go-live-hændelse på Fjordhus' SAP-eksport. Aldrig rullet tilbage. Han husker det ikke. **7. juli:** Rasmus hævede workspace-retention fra 90 til **730 dage** — på hele workspacet, ikke pr. tabel. Han gjorde det fordi Katrine bad om det |
| 4 | Har vi lovet en kunde noget skriftligt om logopbevaring? | **Ja.** Katrine besvarede Fjordhus' sikkerhedsspørgeskema den 2. juli, og besvarelsen er vedhæftet kontrakten som bilag 6. Punkt 4.11: *"Audit logs and access logs are retained for 24 months and are available for customer audit on request."* Samme sætning står i to andre kunders spørgeskemaer fra 2025. Bemærk hvad der **ikke** står: intet om diagnostisk telemetri, applikationslogs eller traces |
| 5 | Hvad står der i Fjordhus-kontrakten om oppetid og hændelser? | 99,5 % månedlig oppetid på webapplikationen. Servicekredit på 4 % af månedsbetalingen pr. påbegyndt 0,5 procentpoint derunder, maks. 25 %. Notifikation om drifts- og sikkerhedshændelser **inden for 24 timer efter opdagelse**. Der findes ingen ekstern oppetidsmåling — den eneste kilde til det tal vi fakturerer imod, er Application Insights availability tests |
| 6 | Hvad koster en udviklerdag, og hvem kan røre logging-stien? | To tal, og de giver forskellige svar. Fuldt belastet kostpris: **3.100 kr./dag**. Den interne kalkulation salg bruger, altså timeprisen kundetilpasninger faktureres til: **8.400 kr./dag**. Kun Rasmus og Thomas kan røre logging- og infrastruktur-stien. Rasmus har ledig kapacitet fra 15. oktober, Thomas har ca. én dag om ugen |
| 7 | Hvad betaler Fjordhus, og hvad er dækningsbidraget? | 1.180.000 kr. over 36 måneder = **32.778 kr./md.**, plus 240.000 i onboarding betalt i maj. Det er **7,7 % af ARR** på 5,1 mio., ikke en femtedel. Deres anslåede infrastrukturomkostning i august var ca. 31.000 kr./md. Bruttomarginen på husets største kunde var i august under 6 % |
| 8 | Har vi reservationer, savings plans eller Hybrid Benefit? | Nej. Alt kører pay-as-you-go. Ingen har nogensinde set på det, ingen ved om der findes SQL-licenser i huset der kunne aktivere Hybrid Benefit, og ingen har regnet på hvad en binding koster i fleksibilitet |
| 9 | Hvor mange miljøer findes der, og hvem ejer dem? | Seks resource groups i samme subscription: `rg-relations-prod`, `rg-relations-test`, `rg-relations-dev`, `rg-poc-ai-doc` (oprettet 3. marts, sidste deployment 11. marts, kører stadig med en App Service P1v3 og en SQL S2), `rg-fjordhus-migration` (skulle være slettet efter go-live den 2. juni), og en uden navnekonvention som ingen kan gøre rede for. **Ingen af dem har en ejer** |
| 10 | Hvor ligger revisionssporet — det revisor skal bruge? | I applikationens egen `audit_trail`-tabel i Azure SQL, hash-kædet, med 41 mio. rækker. **Ikke** i Log Analytics. Fjordhus' interne revision kræver at ændringer på nonconformities og CAPA-lukninger kan spores 24 måneder tilbage, og det udtræk kommer fra SQL. Ingen i huset har bemærket at de to ting ligger forskellige steder — heller ikke Katrine, da hun svarede på spørgeskemaet |
| 11 | Er der legal hold på noget lige nu? | Ja. Fjordhus har en claims-sag mod en polsk emballageleverandør. Deres advokat bad den 21. august skriftligt om at alt materiale vedrørende den leverandør bevares indtil sagen er afsluttet. Der findes **ingen legal hold-mekanisme i produktet**. Anmodningen er indtil videre en mail i Rasmus' indbakke, og ingen har afgrænset hvilke data den omfatter |
| 12 | Hvad driver SQL- og egress-posterne? | SQL: elastic pool på 200 eDTU (Standard), gennemsnitlig udnyttelse **34 %**, peak **91 %** natten mellem den 1. og 2. når scorecards genberegnes. Fjordhus fik en dedikeret S3-database i maj "for en sikkerheds skyld"; gennemsnitlig udnyttelse **11 %**. Egress: Fjordhus' kvalitetsafdeling henter hele dokumentarkivet (ca. 210 GB) via API **hver nat** til deres eget DMS, fordi de vil have en lokal kopi. Ingen har spurgt om et delta ville være nok |
| 13 | Hvad har bestyrelsen faktisk spurgt om? | Peder sendte en mail den 4. september med ét spørgsmål: *"Hvad er jeres bruttomargin pr. kunde, og hvilken vej går den?"* Ordet halvering optræder ikke i mailen. Det er Jens der har oversat spørgsmålet til et sparemål, og han har lovet halveringen på eget initiativ |
| 14 | Hvad koster vi pr. tenant i dag? | **Det ved vi ikke.** Der er ingen tags pr. tenant på nogen ressource, og `tenant_id` blev bevidst fjernet som telemetri-dimension i februar efter et kardinalitetsproblem. Fordelingen kan kun estimeres via proxies — antal dokumenter, antal integrationskørsler, storage-forbrug, antal aktive brugere — og estimatet bærer et spænd på **±25-40 procentpoint** pr. tenant. Det er ikke en manglende oplysning der kan skaffes inden mandag. Det er et arkitekturvilkår, og det skal stå i bilaget til bestyrelsen |

## Præmisskiftet

**Åbnes først når 3 timer og 36 minutter af timeboxen er gået (60 %). Ikke før. Sæt en timer.**

Søndag den 13. september kl. 19.40 sender Jens én mail. Tre linjer i den ændrer opgaven.

1. **Mødet er rykket frem.** Peder kan ikke den 30. Bestyrelsesmødet ligger nu **tirsdag den 22. september kl. 9.00**, og han vil have materialet i hånden **søndag den 20. kl. 18.00**. Der er otte dage færre, og ingen af dem er en hel faktureringsmåned.
2. **En antagelse er forkert.** Rasmus har kigget på det: morgenrapporten til Fjordhus' kvalitetsafdeling — afviste leverandørrækker med afvisningsårsag, sendt kl. 06.30 hver hverdag, nævnt i kontraktbilag 3 punkt 4.2 — bygges af en KQL-query mod `AppTraces`. Præcis den logger du ville slukke. Ombygning så rapporten kommer fra applikationens egen database: **5-8 udviklerdage**, og Rasmus har ikke tid før 15. oktober.
3. **Volumen er på vej op.** Katrine underskrev fredag en hensigtserklæring med Fjordhus Sverige AB: 2.900 leverandører, planlagt go-live 1. februar 2027. Jens skriver: *"Regningen må ikke over 70.000 når begge kører."*

**Hvad skiftet er en test af**

- Om du **regner om** frem for at forklare hvorfor kataloget stadig holder. En opdateret rangering og et opdateret forecast inden for 45 minutter er beviset. En velformuleret redegørelse er det ikke.
- Om linje 2 flytter et indgreb fra "gratis" til "prissat" — eller om du finder en mellemvej (bevar én logger-kategori på et billigere table plan, drop resten) og **prissætter mellemvejen** i stedet for at vælge mellem alt og intet.
- Om du opdager at linje 1 gør en realiseret besparelse **umulig at bevise**: seks dage giver ingen månedsfaktura. Kan du i stedet levere et målt kr./dag-forbrug med angivet måleperiode og målestøj, har du forstået forskellen på et resultat og et bevis for et resultat.
- Om linje 3 ændrer **hvad du tilbyder**, ikke bare hvad du bygger. Et loft på 70.000 for to tenants er et krav om en omkostning pr. tenant, og det er en anden slags dokument end en spareplan.
- Om din egen faldsbetingelse fra ADR'en faktisk **udløses** af linje 2 — og om du så følger den, eller finder på en grund til at lade være. Det er det skarpeste enkeltmålepunkt i casen.

## Rubrik

Tolv kriterier, hvert scoret 0-3, med vægt. Maksimum er **93 point**. Ankrene er tællelige med vilje: en bedømmer skal kunne sætte scoren uden at kende kandidaten og uden at bruge ordet "god".

| # | Kriterium | Vægt | Maks. |
|---|---|---|---|
| K1 | Spørgsmål før første indgreb | 3 | 9 |
| K2 | Spørgsmålene rammer de poster der bærer regningen | 2 | 6 |
| K3 | Regningen dekomponeret og stigningen attribueret, med spænd | 3 | 9 |
| K4 | Enhedsøkonomi pr. tenant med metode og usikkerhed | 2 | 6 |
| K5 | Indgreb rangeret på kroner-per-risiko, med engangspris | 3 | 9 |
| K6 | Nej'et der kan læses af en ikke-teknisk stifter | 3 | 9 |
| K7 | Fravalgene afvist på en målbar akse | 3 | 9 |
| K8 | Faldsbetingelsen | 3 | 9 |
| K9 | Det afgivne svar, SLA'en og kontrakten som omkostningsvilkår | 2 | 6 |
| K10 | Iteration ved præmisskiftet | 3 | 9 |
| K11 | Guardrails med pris på den rigtige vej | 2 | 6 |
| K12 | Commitment-instrumenter og rækkefølgen | 2 | 6 |
| | **I alt** | **31** | **93** |

### K1 — Spørgsmål før første indgreb (vægt 3)

*Findes fordi:* en tredoblet regning udløser reflekshandling. Den der begynder at slukke ting inden han ved hvad der driver tallet, sparer typisk 6 % og ødelægger noget der var betalt for.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen spørgsmålsliste, eller den er skrevet bagefter. Første konkrete besparelsesforslag inden for de første 20 minutter |
| 1 | 3-6 spørgsmål, ikke tidsstemplede, og mindst ét er et forslag i spørgeform ("skal vi ikke sætte retention ned?") |
| 2 | 8-11 tidsstemplede spørgsmål skrevet før første indgreb, ingen løsninger forklædt som spørgsmål, mindst fem rammer skjulte oplysninger |
| 3 | 12+ tidsstemplede spørgsmål, mindst otte rammer skjulte oplysninger, hver linje har en note om hvad svaret ville ændre i rangeringen, og listen gennemgås til sidst med markering af hvilke der **stadig** er ubesvarede i det afleverede katalog |

### K2 — Spørgsmålene rammer de poster der bærer regningen (vægt 2)

*Findes fordi:* femten spørgsmål om logging er ét spørgsmål. De seks poster der bærer tallet her er: log-ingest og retention, SQL-tier og udnyttelse, altid-tændt compute inklusive non-prod, egress, backup og long-term retention, samt sikkerheds- og platformsabonnementer der er tilvalgt og aldrig genbesøgt.

| Score | Sådan ser det ud |
|---|---|
| 0 | Kun log-ingest berørt, eller ingen af de seks |
| 1 | 1-2 af de seks |
| 2 | 4 af de seks, og mindst ét spørgsmål indeholder selv et tal ("er de 41.300 ingest eller retention?") |
| 3 | Alle seks, plus mindst ét spørgsmål der ville have afdækket en modsigelse mellem to ting huset selv har gjort — fx at retention blev hævet for at dække et krav, der viste sig at ligge i en anden datastore |

### K3 — Regningen dekomponeret og stigningen attribueret, med spænd (vægt 3)

*Findes fordi:* totalen er ikke diagnosen. En regning der er steget 78.208 kr. er fire uafhængige historier, og halveringen ligger i tre af dem. Uden attribution rammer indgrebene tilfældigt.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen dekomponering, eller kun totalen og "det er Application Insights" |
| 1 | 4-6 poster med kr./md., ingen sammenligning mod februar, ingen attribution af stigningen |
| 2 | Mindst 8 poster med kr./md., andel og vækstfaktor mod februar, plus en attribution der fordeler mindst 80 % af stigningen på navngivne årsager |
| 3 | Ovenstående, plus **spænd i procentpoint pr. attribueret årsag**, plus mindst to navngivne fejlkilder i sammenligningen (fx at februar har 28 dage og august 31, og at to miljøer opstod imellem) — og en konklusion om hvor stor en del af stigningen der er **valgt** mod **ikke valgt af nogen** |

### K4 — Enhedsøkonomi pr. tenant med metode og usikkerhed (vægt 2)

*Findes fordi:* det er det spørgsmål bestyrelsen faktisk stillede, og det er det eneste tal der overlever mødet. En total i kroner er et budgetproblem; kroner pr. tenant mod betaling pr. tenant er en forretningsmodel.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen fordeling pr. tenant, eller "det kan vi ikke uden tags" som slutpunkt |
| 1 | En fordeling, men metoden står ikke, eller usikkerheden nævnes kun som forbehold i prosa |
| 2 | Fordeling på mindst tre proxies med metoden skrevet ned, usikkerhed angivet i procentpoint, og dækningsbidrag beregnet for mindst husets største kunde |
| 3 | Ovenstående for fem største og fem mindste, plus at det manglende tagging **selv** rapporteres som et fund med en pris på at rette det, plus mindst én tenant hvor konklusionen er kontraintuitiv og forklares |

### K5 — Indgreb rangeret på kroner-per-risiko, med engangspris (vægt 3)

*Findes fordi:* enhver kan lave en liste over ting der kan slukkes. Rangeringen er arkitektarbejdet, og prisen på indgrebet er den halvdel folk udelader.

| Score | Sådan ser det ud |
|---|---|
| 0 | Færre end fem indgreb, eller en liste uden kroner |
| 1 | 5-6 indgreb med sparede kroner, men uden engangspris og uden hvad der mistes |
| 2 | Mindst 7 indgreb, hver med sparet kr./md. **med spænd**, engangspris i udviklerdage og kroner, hvad der mistes, og dage til effekt. Rangeringen er eksplicit begrundet |
| 3 | Ovenstående, plus mindst ét indgreb med engangspris over 15.000 kr. eller fem udviklerdage hvor prisen også står i notatet til Jens, plus at kandidaten angiver **hvilken af de to udviklerdags-kostpriser** han regner med og hvorfor, plus mindst ét indgreb der eksplicit **ikke** anbefales selvom det sparer penge |

### K6 — Nej'et der kan læses af en ikke-teknisk stifter (vægt 3)

*Findes fordi:* stifterens forslag rammer det rigtige sted med det forkerte instrument. Et nej uden tal er en holdning, og et nej uden alternativ gør dig til Ham Der Siger Nej inden for et halvt år.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forslaget besvares teknisk, eller slet ikke. Ordene telemetri, ingest, retention eller observability optræder i notatet |
| 1 | Notatet siger nej og forklarer hvorfor observability er vigtigt, uden et tal for hvad forslaget ville spare |
| 2 | Præcis én side. Indeholder alle fire: hvad forslaget faktisk sparer i kr./md., hvad det koster (både et tal og én kontraktuel konsekvens), hvad vi gør i stedet, og hvad halveringen koster i kroner og udviklerdage. To muligheder, én anbefaling |
| 3 | Ovenstående, plus at stifteren får **anerkendt at han pegede på det rigtige sted** — posten er reelt den største — plus én sætning han kan sende videre til Peder uden at trække sit eget udsagn tilbage, plus at en ikke-teknisk læser kan gengive konsekvensen korrekt bagefter |

### K7 — Fravalgene afvist på en målbar akse (vægt 3)

*Findes fordi:* værdien i en ADR ligger i de afviste alternativer. Afvises de på smag, er dokumentet en begrundelse for noget der allerede var besluttet.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen afviste alternativer, eller de nævnes uden begrundelse |
| 1 | To alternativer nævnt, afvist med ord: "for risikabelt", "for dyrt", "giver ikke mening for os" |
| 2 | Mindst to alternativer afvist, hvert på **én navngiven, målbar akse med et tal** — fx daily cap afvist på "blind i gennemsnitligt 4,2 dage pr. måned ved nuværende ingestprofil", eller fuld sletning af workspace-historik afvist på "bryder bilag 6 punkt 4.11" |
| 3 | Ovenstående, plus at kandidaten kan argumentere overbevisende **for** ét af sine egne fravalg i selvvurderingen, plus at mindst ét fravalg er af noget kandidaten selv havde lyst til at bygge |

### K8 — Faldsbetingelsen (vægt 3)

*Findes fordi:* en spareplan uden faldsbetingelser er en engangshandling. Prisbilledet skifter med volumen, med en ny kunde og med en tier-ændring, og den der ikke har skrevet tærsklen ned, opdager skiftet på næste faktura.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen faldsbetingelse |
| 1 | Én betingelse formuleret som "hvis det bliver et problem, kigger vi på det igen" |
| 2 | Mindst tre betingelser, hver med en **tærskel og en enhed** — fx "hvis faktureret ingest overstiger 900 GB/md. i to på hinanden følgende måneder", "hvis en tenant passerer 6.000 kr./md. i allokeret forbrug", "hvis SQL-poolens peak-udnyttelse overstiger 85 % tre nætter i træk" |
| 3 | Ovenstående, plus at hver betingelse har en **navngiven ejer og et sted den måles**, plus at mindst én af dem faktisk udløses af præmisskiftet og kandidaten selv konstaterer det |

### K9 — Det afgivne svar, SLA'en og kontrakten som omkostningsvilkår (vægt 2)

*Findes fordi:* et svar i et sikkerhedsspørgeskema er ikke marketing, det er et kontraktbilag. Og en oppetids-SLA er en omkostningspost der kun findes hvis nogen måler.

| Score | Sådan ser det ud |
|---|---|
| 0 | Retention foreslås skåret på hele workspacet uden at nogen kontrakt nævnes |
| 1 | Nævner at "der er nok noget om retention i en aftale", uden at slå det op og uden at skelne |
| 2 | Skelner mellem **audit- og adgangslog** (24 måneder, kontraktligt bundet) og **diagnostisk telemetri** (ikke bundet af noget), og finder at revisionssporet ligger i SQL, ikke i Log Analytics. Servicekreditten er nævnt som en omkostningspost |
| 3 | Ovenstående, plus at servicekreditten er **regnet ud** i kroner ved et konkret nedbrud, plus at legal hold-anmodningen behandles som et åbent vilkår med en ejer og en frist, plus én sætning om hvad der skal svares anderledes i næste spørgeskema |

### K10 — Iteration ved præmisskiftet (vægt 3)

*Findes fordi:* det er det ene observerbare kriterium i modul 01 der ikke kan trænes ved at læse, og det er præcis det danske interviewere måler.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forsvarer kataloget. Intet tal ændres |
| 1 | Ændrer rangeringen, men regner ikke om — eller regner om uden at sige hvad der nu er blevet forkert i den første version |
| 2 | Inden for 45 minutter: opdateret rangering, opdateret forecast, én navngiven beslutning der er omgjort og én der **ikke** er berørt, med begrundelse |
| 3 | Ovenstående, plus at kandidaten selv peger på sin udløste faldsbetingelse, plus at han leverer en mellemvej på det ramte indgreb med en pris i stedet for at vælge mellem alt og intet, plus at han adresserer at seks dage ikke kan producere en månedsfaktura og siger hvad han så måler i stedet |

### K11 — Guardrails med pris på den rigtige vej (vægt 2)

*Findes fordi:* problemet her er ikke at nogen valgte forkert. Det er at fire mennesker ændrede noget uden at nogen så det i tolv uger. Uden en mekanisme sker det igen i marts.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen guardrails, eller "vi skal være bedre til at holde øje" |
| 1 | Foreslår flere alerts eller en månedlig gennemgang, uden ejer og uden udløbsdato |
| 2 | 2-4 konkrete regler — fx obligatorisk `owner`- og `env`-tag håndhævet i audit først, budget-alert til en navngiven person frem for en fællespostkasse, en PR-check på logniveau-konfiguration, en ugentlig `Usage`-query — hver med navngiven ejer og udløbsdato |
| 3 | Ovenstående, plus at hver regel har **hvad den koster den rigtige vej i minutter**, plus at mindst én af dem er indført i audit-tilstand frem for som blokering, plus at kandidaten navngiver den regel han **ikke** indfører og hvorfor |

### K12 — Commitment-instrumenter og rækkefølgen (vægt 2)

*Findes fordi:* reservationer og savings plans er det første en økonomiperson foreslår, og det farligste at gøre først. Køber du en binding på et fodaftryk du ikke har trimmet, har du betalt for spildet et år frem.

| Score | Sådan ser det ud |
|---|---|
| 0 | Nævner dem slet ikke, eller anbefaler en binding uden at have set på udnyttelsesgrad |
| 1 | Nævner at "vi kunne købe reserverede instanser", uden tal og uden rækkefølge |
| 2 | Regner på mindst ét commitment-instrument med et hentet tal, og siger eksplicit at det først må købes **efter** højre-dimensionering, med en begrundelse i kroner |
| 3 | Ovenstående, plus at bindingens pris opgøres som **bundet kapital over løbetiden** og som tabt fleksibilitet ved et kendt kommende volumenskift, plus at valget mellem 12 og 36 måneder afgøres af et navngivet forhold i virksomheden og ikke af rabattens størrelse |

**Beståelsesgrænse:** mindst **59 af 93 point (63 %)**, **og** mindst 2 på hver af K1, K3, K5, K7, K8 og K10, **og** intet 0 på noget kriterium. Falder ét af de tre led, er casen dumpet uanset totalen. En besvarelse der scorer 64 point og har et 0 på fravalg er ikke en god besvarelse med en svaghed — det er en spareplan uden arkitektur.

**"Stærk" kræver:** mindst **75 af 93 (81 %)**, **og** 3 på mindst tre af K3, K5, K7, K8 og K10, **og** mindst 2 på alle tolv, **og** at timeboxen er holdt (maks. 6 timer 45 minutter inklusive præmisskiftet). Det svarer til kompetencemodellen i modul 01: kompetent på alle akser og stærk på ingen er en dumpet port, fordi rollen bæres af trade-off-analyse og kostmodellering. Er du over 75 point men over tid, er scoren ikke gyldig — evnen der testes, er at levere et forsvarligt beslutningsgrundlag **inden for** seks timer, ikke at levere et godt et.

## Kalibrering: skriv dette ned FØR du går i gang

Fem forudsigelser. Skriv dem i en fil, gem den, rør den ikke før timeboxen er slut. Uden dette punkt er hele casen en øvelse i at have ret bagefter.

1. **Hvor stor en andel af augustregningen udgør log-ingest og retention tilsammen?** Skriv ét procenttal og et spænd, fx "45 % ± 15". Skriv det før du har set fordelingen.
2. **Hvor mange kroner om måneden kan du fjerne uden at bruge en eneste udviklerdag?** Ét tal i kr./md. De fleste skriver for lidt.
3. **Hvor mange af dine indgreb ender med at have en pris du ikke havde forudset da du skrev dem ned?** Skriv et tal mellem 0 og 7.
4. **Hvor mange af de seks timer går til regnearket?** Ét tal med én decimal. De fleste skriver 1,5 og bruger 2,8.
5. **Hvad bliver sværest?** Én sætning, maks. 15 ord.

**Hvad var jeg sikker på og tog fejl om** — udfyldes efter timeboxen, mindst tre linjer, hver af formen "jeg troede X, det var Y, årsagen var Z". Er feltet tomt eller siger "ingenting", er kalibreringen dumpet, ikke perfekt. En kandidat der ikke tog fejl om noget på seks timer i et system ingen har målt, har ikke målt noget.

## Modelbesvarelsens omrids

**LÆS FØRST EFTER FORSØG.** Dette er ikke et facit. Det er et omrids af hvad en stærk besvarelse indeholder, og hvilke veje der er forsvarlige.

**Tre forsvarlige veje**

- **A. Kirurgisk telemetri-reduktion først, resten senere.** Rul debug-flaget tilbage, læg en DCR-transformation der dropper payload-felter før de bliver til penge, split retention så audit- og adgangslog beholder 24 måneder i en separat tabel og diagnostisk telemetri falder til 30-45 dage. Størst effekt pr. udviklerdag, virker inden for en uge, og rammer præcis den post stifteren pegede på. Falder på ét punkt: uden en analyse af hvad der læser `AppTraces` slukker du en kontraktlig leverance. Er den analyse ikke lavet, er vejen ikke valgt — den er gættet.
- **B. Bred reduktion på fire poster uden binding.** Telemetri plus non-prod-oprydning plus SQL-højre-dimensionering plus en samtale med Fjordhus om delta-eksport i stedet for en natlig fuldkopi. Langsommere til fuld effekt, kræver et nedetidsvindue og en kundesamtale Katrine skal føre, men ingen låst kapital og ingen kontraktuel eksponering. Kræver at du kan sige hvilke to indgreb der ikke kan nå at virke inden den 20.
- **C. Reduktion og derefter commitment.** Som B, men med et savings plan eller en reservation på det stabile compute- og SQL-fodaftryk **efter** højre-dimensioneringen. Lavest varigt niveau. Forsvarlig hvis — og kun hvis — rækkefølgen står eksplicit, bindingen opgøres som bundet kapital over løbetiden, og den svenske søsterkæde er behandlet som en kendt risiko for at fodaftrykket ændrer sig igen inden bindingen udløber.

Alle tre er forsvarlige. Den urimelige er kun én: at slukke Application Insights fordi stifteren foreslog det.

**Hvad en stærk besvarelse desuden indeholder**

- Attributionen står klart: cirka to tredjedele af stigningen er noget **ingen har valgt** — et debug-flag der ikke blev rullet tilbage, en retention-ændring foretaget for at dække et krav der viste sig at ligge i en anden datastore, og to miljøer der skulle have været slettet. Den sætning er hele diagnosen, og den er kortere end den var værd.
- Fjordhus' dækningsbidrag i august er regnet ud og står i bestyrelsesbilaget med sit spænd. Det er svaret på Peders spørgsmål. Halveringen er svaret på Jens' oversættelse af Peders spørgsmål, og de to ting siges begge, høfligt.
- Mindst ét indgreb er eksplicit **ikke** anbefalet: daily cap som besparelse, fordi prisen er at blive blind midt i en hændelse på en kunde med 24-timers notifikationskrav.
- Skellet mellem audit-/adgangslog og diagnostisk telemetri er ført helt igennem: to stores, to retentions, én af dem kontraktligt bundet, den anden ikke. Og en note om at bilag 6 punkt 4.11 blev besvaret uden at nogen vidste hvor revisionssporet lå.
- Fund undervejs der ikke stod i opgaven: at der ikke findes en legal hold-mekanisme, og at ordet "bevar alt" fra en advokat uden en mekanisme er en risiko der bliver dyrere jo længere den ligger som en mail.
- Én sætning om at Application Insights availability tests er den eneste kilde til det oppetidstal virksomheden fakturerer imod, og at forslaget derfor ville fjerne beviset for den SLA man skylder penge på.

**Hvad der adskiller den stærke fra den kompetente**

| Den kompetente | Den stærke |
|---|---|
| Dekomponerer regningen | Dekomponerer stigningen og siger hvor stor en del af den nogen faktisk valgte |
| Sætter kroner på syv indgreb | Sætter kroner **og** engangspris på syv, siger hvilken kostpris pr. udviklerdag han regner med, og anbefaler ét af dem fra |
| Skriver et nej til stifterens forslag | Skriver et nej der begynder med at give stifteren ret i hvor pengene ligger, og slutter med en sætning han kan sende videre |
| Angiver en usikkerhed | Angiver usikkerheden i procentpoint og siger hvilket enkelt gæt der bærer mest af anbefalingen |
| Opdaterer kataloget efter præmisskiftet | Siger også hvad der **ikke** ændrer sig, og at han ikke kan bevise en månedsbesparelse på seks dage |
| Foreslår tags og alerts | Prissætter guardrailen i minutter for den der skal følge den, og navngiver den regel han fravælger |
| Leverer en halvering | Leverer en halvering **og** en omkostning pr. tenant der kan bære en kunde nummer to |

## Sådan ser en dårlig besvarelse ud

Skrevet som du selv ville formulere det. Formålet er genkendelse, ikke skam.

1. *"Debug-loggen var tændt, jeg slukkede den, det sparer 32.000, sagen er lukket."* — Du har fundet det rigtige og stoppet der. Du opdagede aldrig at en kontraktlig morgenrapport hang i den, du regnede aldrig på hvad de resterende 46.000 består af, og du besvarede aldrig bestyrelsens spørgsmål.
2. *"Jeg satte retention ned til 30 dage på workspacet, det er standardanbefalingen."* — Du har brudt bilag 6 punkt 4.11 i den største kundes kontrakt for at spare cirka 5.000 kr., og du finder ud af det næste gang deres revisor spørger. Bemærk at ingen ville have rettet dig.
3. *"Jeg lavede en tabel over de typiske Azure-besparelser: right-sizing, auto-shutdown, reservationer, storage tiers."* — Det er en generisk liste. Den kunne være skrevet uden at have set regningen, og det kan enhver læser se.
4. *"Jeg regnede med cirka 15 kr. pr. GB, det er vist normalt."* — Måske. Men du hentede det ikke, du mærkede det ikke som gæt, og hele attributionen hviler på det. En kostmodel med ét umærket gæt i bunden er en påstand med decimaler.
5. *"Jeg købte et treårigt savings plan, det giver 62 procent."* — Du har bundet kapital i tre år på et fodaftryk du ikke har trimmet, i et firma med syv årsværk, ni dage før en hensigtserklæring om at fordoble volumen. Rabatten var ægte. Rækkefølgen var forkert.
6. *"Jeg skrev til Jens at vi ikke bare kan slukke Application Insights, fordi vi så mister observability og ikke kan fejlsøge."* — Intet tal, intet alternativ, og et ord han ikke bruger. Du har brugt din ene side på at have ret. Det er sådan man bliver rutet udenom, og det tager under et halvt år.
7. *"Præmissen ændrede sig, men rangeringen holder faktisk stadig hvis man ser på det på den her måde."* — Det er forsvar. Det er også præcis den sætning en interviewer lytter efter, og den eneste der ikke kan bortforklares bagefter.
8. *"Enhedsøkonomien nåede jeg ikke, der er jo ikke tags, så det kunne alligevel ikke lade sig gøre."* — Det manglende tagging **er** fundet, og proxy-estimatet med et ærligt spænd er leverancen. Du har afleveret en spareplan til et spørgsmål om bruttomargin.

## Hvor i materialet svaret står

Ubarmhjertig version. To kriterier er ikke dækket af noget modul, og det er et fund i materialet, ikke i casen.

| Kriterium | Modul | Præcis sektionsoverskrift | Hvad du henter der |
|---|---|---|---|
| **K1** Spørgsmål før første indgreb | 01 | `### Øvelse 3: Trade-off-kata på tid` | "Mindst otte kravsspørgsmål stillet **før** første diagram", timeboxen og selvkontrollen til sidst. Suppl.: 01 `## Arkitektur er de dyre beslutninger` om at springe til teknologi før volumen og budget er kendt |
| **K2** Spørgsmålene rammer de bærende poster | 03 | `## Sådan ved du at du kan det` | Punkt 2: "du svarer inden for 30 minutter med et tal, en kilde og en usikkerhedsmargin, inklusive egress, log ingestion, private endpoints og backup" — de seks poster står navngivet dér. Suppl.: 03 `## Budgetloftet: 400 DKK/md, hård alert ved 600` for hvilke services der reelt vælter et budget |
| **K3** Dekomponering og attribution med spænd | 06 | `## Cost er et arkitekturproblem, ikke et driftsproblem` | Fakturamekanikken: per GB ingest, `_IsBillable`, hvilke tabeller der er gratis, faktureret størrelse ~25 % under rå JSON, table plans og deres fælder. Suppl.: 06 `## På jobbet, uden at spørge om lov` for `Usage`-queryen der giver dekomponeringen på en time |
| **K4** Enhedsøkonomi pr. tenant med usikkerhed | 12 | `## Tre spikes med fysisk output` (punkt 4, "Enhedsøkonomi pr. tenant") | Modellen der fordeler forbrug pr. tenant på storage, egress, compute og backup-retention; grafen omkostning mod betaling; proxy-metoden når tags mangler; og sætningen "findes der ikke tags pr. tenant, *er* dét fundet" |
| **K5** Indgreb rangeret på kroner-per-risiko | 06 | `## Spikes: hvad du bygger, og hvad der ligger på disken bagefter` (række **O-4**) | Outputkravet "notat med tre indgreb: kroner sparet mod indsigt tabt" og modellen på målte `_BilledSize` ved 1x/10x/100x. Suppl.: 06 `## Cost er et arkitekturproblem, ikke et driftsproblem` for rækkefølgen af indgreb i den orden en arkitekt siger dem, og for daily cap som forsikring frem for besparelse |
| **K6** Nej'et til en ikke-teknisk læser | 11 | `## Oversæt til kroner og risiko` | De fire enheder, forbuddet mod at præsentere én løsning, og formen "Vi har X i dag. Problemet er Y. Spørgsmålet er hvordan vi Z. Mit svar er A, det koster B, alternativet C koster D". Suppl.: 10 `## Shape Up, og aldrig et nej uden prisskilt` for tredelingen og for risikoen ved at blive Ham Der Siger Nej |
| **K7** Fravalg på en målbar akse | 01 | `## Kompetencemodellen: ti akser` (rækken "Trade-off-analyse og ADR'er") | "Afviser på en akse han kan måle eller prissætte, og siger hvad der ville vende valget" — kolonnen *Stærk* er ordret dette kriterium. Suppl.: 07 `## Faldgruber` om at værdien i en ADR ligger i de afviste alternativer |
| **K8** Faldsbetingelsen | 06 | `## Sådan ved du at du kan det` | "Mindst én ADR hvor du siger nej til noget populært med en eksplicit genovervejelsesbetingelse". Suppl.: 09 `## Sådan ved du at du kan det` (rækken "ADR-tællingen"): mangler afsnittet om hvad der ville ændre beslutningen, er det en begrundelse, ikke en beslutning |
| **K9** Det afgivne svar, SLA'en og kontrakten som omkostningsvilkår | — | **IKKE DÆKKET** | Delvist dækket to steder: 08 `## Trade-off-øvelsen der skiller arkitekt fra senior udvikler` giver **designsvaret** ("Audit-log 365 dage, diagnostisk log 30 — to forskellige stores") og fejlklasse-kolonnen; 12 `## Tre spikes med fysisk output` (punkt 3, Spørgeskema-maskinen) giver klassifikationen *dokumenteret / sandt men udokumenteret / ikke sandt*. Der mangler: hvad man gør når svaret **allerede er afgivet** og nu er et kontraktbilag der binder en omkostningsbeslutning; at en oppetids-SLA med servicekredit er en omkostningspost der kun eksisterer hvis nogen måler; og hvordan man beregner eksponeringen. Materialet lærer dig at svare rigtigt fremad, ikke at rydde op i et svar der er sendt |
| **K10** Iteration ved præmisskift | 01 | `## Sådan ved du at du kan det` (2. punkt) | "Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse." Suppl.: 01 `### Øvelse 3: Trade-off-kata på tid`, sidste afsnit om den eksterne der ændrer en præmis undervejs |
| **K11** Guardrails med pris på den rigtige vej | 07 | `## Guardrail eller gatekeeper` | De to sætninger man skal kunne besvare for enhver regel — hvordan gør den den rigtige vej hurtigere, og hvad koster den den forkerte — plus testen tid-til-compliant mod tid-til-non-compliant. Suppl.: 07 `## Progressiv håndhævelse: manøvren der giver mandat` for audit før deny, og 03 `### Spike 0 — Sikker landing (uge 1, 4-6 timer)` for budget-alerts, tagging og navnestandard før første ressource |
| **K12** Commitment-instrumenter og rækkefølgen | — | **IKKE DÆKKET** | Materialet nævner præcis ét commitment-instrument, og kun for at afvise det: 06 `## Cost er et arkitekturproblem, ikke et driftsproblem` — "Commitment tiers starter ved 100 GB/dag og gælder kun Analytics — altså ikke dig". Der findes **intet** om reservations, savings plans, Azure Hybrid Benefit eller CSP-/EA-rabatter i nogen af de tolv moduler. Modul 03 lærer dig at læse listepriser via Retail Prices API, ikke at forhandle dem eller at binde dem. Konkret mangler: hvilke instrumenter der findes, hvad de koster i bundet kapital og fleksibilitet, og den vigtigste regel af alle — at man højre-dimensionerer først og binder bagefter, aldrig omvendt. For en case af typen "kostarkitektur og forhandling" er det materialets største enkelthul |

## Ekstern kalibrering

Din egen score er værdiløs alene, og en kollega i et nimandsfirma tæller halvt. Mindst to af disse skal have givet **skriftlig** kritik, før casen tælles som gennemført. Spørg hver om én ting — ikke om en helhedsvurdering, for den får du en høflig udgave af.

| Hvem | Hvor du finder dem | Det konkrete spørgsmål |
|---|---|---|
| Praktiserende cloud- eller platformarkitekt med FinOps-erfaring | Aarhus .NET User Group eller GOTO-meetup; bed om 30 minutter efter oplægget, ikke under | "Her er min attribution af en regning der er steget 78.000. Hvilken post har jeg tilskrevet forkert, og hvilken har jeg slet ikke set?" |
| Microsoft-partner eller CSP-reseller (fx en dansk Azure-partner virksomheden allerede handler gennem) | Gennem Jens eller Lone; det er en samtale de kan tage uden dig, men bed om at være med | "Hvad ville I have foreslået først på denne fordeling, og hvilke rabat- eller bindingsinstrumenter er relevante for et forbrug på 100.000 kr./md.?" — bemærk at de sælger noget, og notér hvad de **ikke** nævner |
| Økonomiperson uden it-baggrund — en revisor, en controller, Lone selv | Internt, 20 minutter, uden forberedelse | Giv dem artefakt 3 og sig intet. Bed dem bagefter gengive: hvad koster forslaget, hvad anbefaler jeg, og hvad går vi glip af. Alt de misforstår er en fejl i notatet, ikke i deres forståelse |
| Ekstern design-review-mentor (1-2 t/md., 15.000-25.000 kr./år, jf. modul 10) | ADPList eller en betalt aftale rammesat som "ekstern review af vores arkitekturbeslutninger" | "Angrib min rangering, ikke mine tal. Hvorfor er nummer fire ikke nummer et?" |
| Code review-byttepartneren fra måned 3 | Fast kadence, 45 minutter | "Læs mine to fravalg. Kan du argumentere mig ned på ét af dem?" |
| En SRE eller driftsansvarlig i et større hus | LinkedIn, kold henvendelse til en der skriver om Azure Monitor eller omkostningsstyring | "Jeg foreslår at skære diagnostisk telemetri med cirka 80 %. Hvilket spørgsmål kunne I ikke besvare bagefter, som I ikke vidste I ville få brug for?" |

Notér for hver: hvad de sagde, hvad du ændrede, og hvad du valgte at lade stå — plus hvorfor. Den tredje kolonne er den en kommende arbejdsgiver spørger ind til.
