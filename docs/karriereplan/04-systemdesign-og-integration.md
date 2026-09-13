# 04. Systemdesign, distribuerede systemer og integrationsmoenstre

> Du sidder midt i det svaereste stof i faget: data fra ERP-systemer du ikke kontrollerer, dokumenter der skal holde til en audit aar efter upload, og kunder med hver deres compliancekrav i samme kodebase.
> Forskellen paa dig og en arkitekt er ikke at han kender flere moenstre. Det er at han kan sige hvad han fravalgte, og hvad fravalget kostede.
> Denne sektion giver dig ordforraadet, valgkriterierne og de maalinger der goer ordene til dine egne i stedet for laante.

## Moenstervokabularet

Maalet er ikke at definere moenstre, men at kunne sige "det er en Content Enricher med en Idempotent Receiver foran, og claim check'et ligger i blob" i stedet for tre saetninger om det samme. Ordforraad er komprimering, og komprimering er det der goer at en samtale naar frem til trade-offs paa den tid du faar.

| Moenster | Hvad det loeser | Dit domaeneeksempel |
|---|---|---|
| Anti-Corruption Layer | Kundens model laekker ikke ind i din | Kunden opgraderer Business Central, `supplierStatus` skifter fra streng til enum |
| Raw landing zone | Bevisfoerelse: hvad modtog vi, hvornaar | Payload gemt uaendret med hash og tidsstempel, 90 dages retention |
| Canonical model | Én intern model, N eksterne dialekter | SAP, Business Central og en CSV-kunde bliver til én leverandoerrepraesentation |
| Idempotent Receiver | Samme faktum to gange giver ét resultat | Godkendelse ankommer baade via webhook og natlig pull |
| Transactional Outbox | Ingen dual write mellem DB og broker | Godkendelse committet, men beskeden til kundens ERP forsvandt |
| Dead Letter Channel | De 0,3% blokerer ikke de 99,7% | Én tenants misdesignede stamdata stopper ikke de andres flow |
| Claim Check | Store payloads ud af beskedstroemmen | Beskeden baerer en blob-reference, ikke en 500 MB PDF |
| Valet Key | Upload uden om din API-proces | Kortlivet user delegation SAS fra leverandoerens browser |
| Retry med jitter, Circuit Breaker | Transiente fejl bliver usynlige; doed downstream haemmer dig ikke ihjel | Registerservice svarer 503 i to minutter |

Laer dem via opslag. Laeser du katalogerne forfra, braender du ti timer paa genkendelse uden anvendelse.

## Det foerste reelle valg: hvordan data kommer ind

| Integrationsstil | Latens | Kobling | Hvem ejer fejlen | Vaelg naar |
|---|---|---|---|---|
| Filoverfoersel / batch | Timer | Loesest | Dig | Kunden har en ERP-eksport og ingen udviklere |
| Pull-API mod kunden | Minutter-timer | Du er conformist | Dig | Kunden eksponerer OData og aendrer det uden varsel |
| Push / webhook | Sekunder | Delt kontrakt | Delt, og derfor farligst | Kunden kan sende, volumen er moderat |
| Messaging (koe/topic) | Sekunder | Loes i tid | Dig, med DLQ og replay | Internt mellem dine egne komponenter |
| Event streaming | Sub-sekund | Kraever schema-disciplin | Forbrugeren | Genafspilning og flere uafhaengige forbrugere |

To saetninger du skal kunne sige uden at taenke. **Du vaelger ikke transport, du vaelger hvem der ejer fejlen.** Og: **kan kunden ikke aendre noget, er dit design laast paa deres side af graensen** - saa handler arbejdet om anti-corruption layer, raw landing zone og reconciliation, ikke om protokolvalg.

## Leveringssemantik: at-least-once er praksis

Exactly-once findes ikke over en netvaerksgraense. Det der findes er exactly-once *processing*: at-least-once levering plus idempotens hos modtageren. Den indsigt flytter en samtale fra "senior udvikler" til "arkitekt" hurtigere end noget andet.

Idempotensnoeglen skal vaere en **business key**, ikke et message-id: samme forretningsfaktum ankommer ofte gennem to kanaler med to forskellige message-id'er - samme certifikatgodkendelse via natlig pull og via webhook. Brugbar noegle i dit domaene: `leverandoer-id + dokumenttype + kundens versionsstempel`. Det svaere spoergsmaal: hvad sker der naar kunden aendrer et felt der indgaar i noeglen.

Tal du skal kunne citere om Azure Service Bus (Microsoft Learn-URL'er er bekraeftet via soegeindeks, ikke hentet direkte):

- Duplicate detection findes **ikke** i Basic-tier, og Basic har heller ikke topics.
- Default duplikatvindue er **10 minutter** (min 20 sekunder, max 7 dage) og virker **kun paa MessageId** - altsaa ikke paa forretningsniveau.
- Default `MaxDeliveryCount` er **10** foer dead-lettering.
- En dead-letteret sessionsbesked mister sin raekkefoelge ved replay: den faar nyt enqueue-tidspunkt og sekvensnummer. Praesenterbar indsigt, fordi de fleste tror DLQ-replay er gratis.
- Aeldre SDK'er og SBMP er meldt til retirement 30. september 2026 (uverificeret). Brug `Azure.Messaging.ServiceBus`.

Paa HTTP-siden: `Idempotency-Key` er beskrevet i IETF draft-ietf-httpapi-idempotency-key-header-07 (15. oktober 2025) - **stadig et draft, ikke en RFC**, og den siger ikke hvor laenge du skal huske noeglen, hvilket er hele det svaere.

## Konsistens: hold op med at bruge CAP

CAP er bevist for ét read-write register under total partition, siger intet om multi-objekt-transaktioner, og ingen reel database kan entydigt klassificeres som CP eller AP. Siger du "vi valgte AP frem for CP", hoerer en erfaren arkitekt en der har laest en systemdesignguide. Brug PACELC: konsistens/latens-afvejningen gaelder ogsaa naar netvaerket er sundt, og det er den du designer efter til daglig.

Oversaettelsen til forretningen er halvdelen af rollen. Ikke "systemet er eventually consistent", men:

> Naar indkoeberen godkender certifikatet, er det gemt med det samme. Kundens ERP har det inden for 60 sekunder i 99% af tilfaeldene. Tager det laengere, kan de se det i statusfeltet, og vi faar alarm efter 5 minutter.

Det er et SLO, ikke en undskyldning. Traen det paa en rigtig person og bed dem gengive konsekvensen bagefter.

## Nedbrydning: modulaer monolit er defaulten

"Vi burde splitte det op i services" er det hurtigste selvmaal i en arkitektsamtale. Microservices betaler sig ved organisatorisk skala eller genuint divergerende skaleringsbehov - ikke ved ambition. Med tre til fem udviklere i huset er ingen taerskelvaerdi i naerheden af opfyldt, og det skal du kunne sige uden at lyde undskyldende.

Den vindende formulering: modulgraenser haandhaevet af compileren nu, saa vi kan splitte om to aar hvis behovet opstaar - og her er arkitekturtesten der haandhaever det. Fowlers MonolithFirst og MicroservicePremium giver dig autoriteten paa under en time. Et bredt citeret 2026-tal siger at ca. 42% har konsolideret microservices tilbage (uverificeret - indikation, ikke citat).

Betingelserne du skal kunne navngive foer et split: deploy-frekvenskonflikt mellem moduler, teams der blokerer hinanden, divergerende skaleringsprofil (dokumentbehandling vs. portaltrafik), forskellige dataopbevaringskrav pr. modul. Taerskelvaerdier, ikke fornemmelser.

## Dokumenttunge flows

Dokumenthaandtering i skala er 90% metadata, retention, adgangskontrol og lifecycle - 10% at gemme bytes.

1. **Upload gaar uden om din API-proces.** Valet Key med kortlivet user delegation SAS. En 500 MB fil gennem din egen proces er et selvpaafoert problem.
2. **Soegning paa metadata, ikke scanning.** "Certifikater der udloeber inden for 30 dage" maa ikke scanne 20 mio. blobs. Blob index tags er ét svar, databasemetadata et andet - lifecycle-regler kan maks. bruge 10 index tag-betingelser pr. regel.
3. **Retention kolliderer med sletteret.** Immutable containers med legal hold betyder at lifecycle-sletning ikke virker. Kraever en kunde sine data slettet mens en audit loeber, er det ikke en teknisk fejl - det er en konflikt du skal have et skrevet svar paa. Omnibus I (i kraft 18. marts 2026) udskoed CSDDD's anvendelse til 26. juli 2029; presset forsvinder ikke, det forskydes.

## Fire spikes med fysisk output

Hver spike lukkes efter maks to uger, uanset om den foles faerdig. ADR'en skrives **foer** beslutningen - har du aldrig skiftet mening midt i at skrive en, skriver du dem paa det forkerte tidspunkt. Brug MADR's minimale variant uaendret.

**Spike A - Idempotent ingest fra et ERP du ikke kontrollerer (2 uger).** Byg en puller mod en aaben offentlig API som stand-in. Kilden paginerer ustabilt, har intet paalideligt aendringstidsstempel og skifter felttyper uden varsel. Krav: ingen dubletter, ingen tabte opdateringer, genstart fra vilkaarligt punkt, bevisfoerelse for hvad du modtog hvornaar. Begraensning: kilden aendrer sig ikke for din skyld, og raadata maa ikke gemmes over 90 dage. Byg raw landing zone med indholds-hash, anti-corruption layer til canonical model, idempotens paa business key, optimistic concurrency, checkpointing og reconciliation. Injicér fire fejl: dubletter, afbrudt koersel midt i en side, aendret felttype, en record der forsvinder fra kilden.
*Output:* ADR "Idempotensnoegle - business key frem for message-id". Fejlinjektionssuite i CI. Maalt dublet- og tabsrate foer og efter idempotenslaget. Dataflow-diagram raw -> canonical.

**Spike B - Outbox uden framework (1-2 uger).** Gem en certifikatgodkendelse i databasen **og** publicér beskeden. Krav: intet publiceres for en rullet-tilbage transaktion; ingen commit ender uden at beskeden til sidst publiceres; raekkefoelge pr. leverandoer bevares. Begraensning: ingen distribuerede transaktioner og **intet messaging-framework** - haand-rul den. Outbox-tabel i samme transaktion som domaeneaendringen, relay der publicerer at-least-once, sessions med leverandoer-id som SessionId. Draeb relay'et med `kill -9` i tre vinduer: efter commit foer publish, efter publish foer markering, midt i en batch. Koer gratis lokalt paa Service Bus-emulatoren via Testcontainers.
*Output:* ADR "Outbox vs. dual write vs. change data capture". Maaletabel over tab og dubletter i de tre kill-scenarier. Sekvensdiagram med fejlvinduerne markeret. Svar paa hvad relay'et koster i latens, og hvornaar polling holder op med at duere.

**Spike C - Poison messages, DLQ og replay (1-2 uger).** 0,3% af beskederne kan ikke behandles, af tre blandede aarsager: oedelagte payloads, midlertidigt nedbrud downstream, og én tenant med misdesignede data. Krav: de 0,3% maa ikke bremse resten; fejlede beskeder skal kunne genafspilles uden dubletter; "hvad fejlede for tenant 12 i gaar mellem 14 og 16" besvares paa under to minutter. Klassificér transient vs. permanent, backoff med jitter for transient, oejeblikkelig dead-lettering for permanent. Byg en replay-CLI med filter paa tenant og tidsrum, som respekterer idempotenslaget fra spike B. Afslut med en blindtest: en scriptet joker injicerer fejlen, du tager tid paa at finde den.
*Output:* ADR "Retry- og DLQ-politik". Koerende replay-vaerktoej. Maalt tid-til-diagnose. Reproduceret ordering-brud ved DLQ-replay med konsekvensen i klartekst. Liste over fejl der **ikke** kan klassificeres automatisk.

**Spike D - Saga med kompensation forretningen kan acceptere (2 uger).** Leverandoeronboarding i fem trin: opret, anmod om certifikater, validér mod ekstern registerservice, opret i kundens ERP, aktivér. Trin 3 og 4 er eksterne, kan time out, og processen kan tage dage fordi et menneske skal uploade. Byg **begge** varianter i lille skala - orchestration og ren choreography - injicér timeout i trin 4 og fejl i trin 3, og maal det afgoerende: hvor mange steder skal du kigge for at finde en haengende saga, og hvor lang tid tager det. Vigtigst er ikke koden: skriv kompensationen for hvert trin i klartekst og udpeg dem der **ikke** kan automatiseres. Anmodede certifikater kan ikke uanmodes. Rollback betyder sjaeldent DELETE, snarere "status Afvist, behold dokumenterne, notificér indkoeberen".
*Output:* ADR "Orchestration vs. choreography" med de to maalte diagnosetider som begrundelse. State-diagram med alle kompensationsstier og de menneskelige eskaleringspunkter.

**Timebudget:** ca. 20-24 timer laesning og 55-70 timer paa de fire spikes. Med 10-15 timer om ugen daekker det maaned 2-5, og kun hvis to-ugers-loftet holdes.

## Ressourcer

| Ressource | Prioritet | Tid | Hvad du henter |
|---|---|---|---|
| Azure Service Bus-dok: sessions, duplicate detection, DLQ, message loss | Kerne | 3-4 t, linje for linje | Tallene du skal kunne citere |
| DDIA 2. udg., Kleppmann & Riccomini (marts 2026) | Kerne | 25-35 t, selektivt | Replikation, partitionering, transaktioner, distribuerede fejl |
| Kleppmann: "Please stop calling databases CP or AP" | Kerne | 30 min | Fjerner den dyreste enkeltmisforstaaelse |
| Fowler: MonolithFirst, MicroservicePremium, StranglerFig | Kerne | 1 t samlet | Autoritet til at afvise et split |
| `microservices.io/patterns`, `enterpriseintegrationpatterns.com`, Azure Cloud Design Patterns | Stoette | 6-8 t, kun som opslag | Ordforraadet: Outbox, Saga, Claim Check, Valet Key. Laes aldrig Hohpe forfra |
| The Hard Parts - distribuerede transaktioner, data ownership | Stoette | 8-10 t | Trade-offs uden facit |
| `github.com/kgrzybek/modular-monolith-with-ddd` (.NET 8 - port moenstrene) | Kerne | 6-8 t | Modulgraenser i praksis |
| MADR (`adr.github.io/madr`) | Kerne | 30 min | Skabelonen. Opfind ikke din egen |
| System Design Interview (Alex Xu) | Spring over | 0 t | Hyperscale consumer-systemer; dit problem er kobling |

## Certificeringer

| Eksamen | Status (verificeret sep. 2026) | Rolle |
|---|---|---|
| AZ-305 | Aktiv; opdateret 17. april 2026 | Deadline-motor og vokabular. **AZ-104 er haard forudsaetning for Expert-badget** |
| AZ-400 | Aktiv; opdateret 27. juli 2026 | Kun paa CI/CD-sporet. Forudsaetning: AZ-104 eller Developer Associate |
| AZ-204 | **Pensioneret 31. juli 2026** | Enhver kilde der stadig anbefaler den, er foraeldet |
| AI-200 | Efterfoelgeren, AI-drejet | Ikke en generel .NET-eksamen. Ventes som AZ-400-forudsaetning (uverificeret) |
| TOGAF / iSAQB CPSA-F | - | Fravaelg eksplicit; begrundelsen er et modenhedssignal |

## Priser

| Post | Pris | Note |
|---|---|---|
| Container Apps | 0 kr. inden for gratistildelingen | 180.000 vCPU-sek., 360.000 GiB-sek., 2 mio. requests/md. `minReplicas` over 0 faktureres alle 730 timer/md. |
| Service Bus Standard | Fast maanedlig udgift | Basic har hverken topics eller duplicate detection (pris uverificeret) |
| Defender for Storage, on-upload scan | Ca. 0,15 USD/GB, foerste 50 TB/md. | Default-loft 10.000 GB/md. pr. konto (uverificeret) |
| MassTransit v9 (jan. 2026) | Kommerciel, fra ca. 400 USD/md. | v8 er Apache-2.0, mister support ultimo 2026. MIT: Wolverine, Rebus, Brighter |

Budget alert paa dag ét. Prissaet foer du deployerer.

## Faldgruber

- **Microservice-svaret.** Foreslaar du et split, taber du rummet oejeblikkeligt.
- **Event sourcing fordi det ser arkitektonisk ud.** Dokumenterede 2025-2026-erfaringer: 300 linjers upcasting-kode, fire samtidige event-schemaer, read models der gjorde skrivninger langsommere. Kun naar revisionssporet **er** forretningskravet, og kun i én bounded context.
- **At bygge et produkt i stedet for en spike.** Symptomet er praecist: foerste gang du faar lyst til en dashboardside, er du holdt op med at laere arkitektur.
- **Ikke at maale.** En spike uden et tal er et blogindlaeg.
- **Duplicate detection forvekslet med idempotens.** Den virker paa MessageId i et 10-minutters vindue. Dit problem er forretningsniveau og timer eller dage.
- **Kun Microsoft-kilder fordi du er paa Azure.** AWS' SaaS Lens er skarpere paa tenant isolation og control plane vs. application plane. Kan du kun én leverandoers ordforraad, afsloerer du dig i moedet med en anden stack.
- **Ingen ekstern modstand.** Ingen paa arbejdet kan presse dig paa et designvalg. Faar spike A-D aldrig oejne udefra, kan du oeve det forkerte i tolv maaneder uden at opdage det. Book modstanden i kalenderen.

## Saadan ved du at du kan det

1. Du tegner de fem integrationsstile paa under 10 minutter uden noter, med latens, kobling og fejlejerskab for hver.
2. Du kan forklare hvorfor idempotensnoeglen er en business key og ikke et message-id, med **din egen** noegle fra spike A, og sige hvad der sker naar kunden aendrer et felt i den.
3. Du kan fremvise en maaletabel over tab og dubletter i tre kill-scenarier, foer og efter outbox. Tal fra din egen koersel.
4. Du kan citere fire konkrete Service Bus-begraensninger og sige hvad hver af dem **ikke** loeser.
5. Du forklarer konsistensvinduet til en ikke-teknisk person paa under tre minutter uden ordet "eventual", og personen gengiver konsekvensen korrekt.
6. Du har en maalt tid-til-diagnose fra en blindtest og ved hvad der forkortede den.
7. Du kan navngive taerskelvaerdierne der ville faa dig til at splitte en modulaer monolit - og sige hoejt at ingen af dem er opfyldt der hvor du sidder.
8. Du kan pege paa mindst tre kompensationsstier i en saga der **ikke** kan automatiseres, og beskrive den forretningsproces de kraever.
9. Du har fire ADR'er fra sektionen med navngivne fravalgte alternativer og en eksplicit "dette ville faa mig til at ombestemme mig"-betingelse.
10. En fremmed senior arkitekt har presset dig i 45 minutter paa trade-offs i ét af spike-problemerne uden at du faldt tilbage paa laerebogsformuleringer. Det eneste kriterium der ikke kan bedoemmes indefra, og derfor det tungeste ved kompetenceporten.
