# 04. Systemdesign, distribuerede systemer og integrationsmønstre

> Du sidder midt i det sværeste stof i faget: data fra ERP-systemer du ikke kontrollerer, dokumenter der skal holde til en audit år efter upload, og kunder med hver deres compliancekrav i samme kodebase.
> Forskellen på dig og en arkitekt er ikke at han kender flere mønstre. Det er at han kan sige hvad han fravalgte, og hvad fravalget kostede.
> Denne sektion giver dig ordforrådet, valgkriterierne og de målinger der gør ordene til dine egne i stedet for lånte.

## Mønstervokabularet

Målet er ikke at definere mønstre, men at kunne sige "det er en Content Enricher med en Idempotent Receiver foran, og claim check'et ligger i blob" i stedet for tre sætninger om det samme. Ordforråd er komprimering, og komprimering er det der gør at en samtale når frem til trade-offs på den tid du får.

| Mønster | Hvad det løser | Dit domæneeksempel |
|---|---|---|
| Anti-Corruption Layer | Kundens model lækker ikke ind i din | Kunden opgraderer Business Central, `supplierStatus` skifter fra streng til enum |
| Raw landing zone | Bevisførelse: hvad modtog vi, hvornår | Payload gemt uændret med hash og tidsstempel, 90 dages retention |
| Canonical model | Én intern model, N eksterne dialekter | SAP, Business Central og en CSV-kunde bliver til én leverandørrepræsentation |
| Idempotent Receiver | Samme faktum to gange giver ét resultat | Godkendelse ankommer både via webhook og natlig pull |
| Transactional Outbox | Ingen dual write mellem DB og broker | Godkendelse committet, men beskeden til kundens ERP forsvandt |
| Dead Letter Channel | De 0,3% blokerer ikke de 99,7% | Én tenants misdesignede stamdata stopper ikke de andres flow |
| Claim Check | Store payloads ud af beskedstrømmen | Beskeden bærer en blob-reference, ikke en 500 MB PDF |
| Valet Key | Upload uden om din API-proces | Kortlivet user delegation SAS fra leverandørens browser |
| Retry med jitter, Circuit Breaker | Transiente fejl bliver usynlige; død downstream hæmmer dig ikke ihjel | Registerservice svarer 503 i to minutter |

Lær dem via opslag. Læser du katalogerne forfra, brænder du ti timer på genkendelse uden anvendelse.

## Det første reelle valg: hvordan data kommer ind

| Integrationsstil | Latens | Kobling | Hvem ejer fejlen | Vælg når |
|---|---|---|---|---|
| Filoverførsel / batch | Timer | Løsest | Dig | Kunden har en ERP-eksport og ingen udviklere |
| Pull-API mod kunden | Minutter-timer | Du er conformist | Dig | Kunden eksponerer OData og ændrer det uden varsel |
| Push / webhook | Sekunder | Delt kontrakt | Delt, og derfor farligst | Kunden kan sende, volumen er moderat |
| Messaging (kø/topic) | Sekunder | Løs i tid | Dig, med DLQ og replay | Internt mellem dine egne komponenter |
| Event streaming | Sub-sekund | Kræver schema-disciplin | Forbrugeren | Genafspilning og flere uafhængige forbrugere |

To sætninger du skal kunne sige uden at tænke. **Du vælger ikke transport, du vælger hvem der ejer fejlen.** Og: **kan kunden ikke ændre noget, er dit design låst på deres side af grænsen** - så handler arbejdet om anti-corruption layer, raw landing zone og reconciliation, ikke om protokolvalg.

## Leveringssemantik: at-least-once er praksis

Exactly-once findes ikke over en netværksgrænse. Det der findes er exactly-once *processing*: at-least-once levering plus idempotens hos modtageren. Den indsigt flytter en samtale fra "senior udvikler" til "arkitekt" hurtigere end noget andet.

Idempotensnøglen skal være en **business key**, ikke et message-id: samme forretningsfaktum ankommer ofte gennem to kanaler med to forskellige message-id'er - samme certifikatgodkendelse via natlig pull og via webhook. Brugbar nøgle i dit domæne: `leverandør-id + dokumenttype + kundens versionsstempel`. Det svære spørgsmål: hvad sker der når kunden ændrer et felt der indgår i nøglen.

Tal du skal kunne citere om Azure Service Bus (Microsoft Learn-URL'er er bekræftet via søgeindeks, ikke hentet direkte):

- Duplicate detection findes **ikke** i Basic-tier, og Basic har heller ikke topics.
- Default duplikatvindue er **10 minutter** (min 20 sekunder, max 7 dage) og virker **kun på MessageId** - altså ikke på forretningsniveau.
- Default `MaxDeliveryCount` er **10** før dead-lettering.
- En dead-letteret sessionsbesked mister sin rækkefølge ved replay: den får nyt enqueue-tidspunkt og sekvensnummer. Præsenterbar indsigt, fordi de fleste tror DLQ-replay er gratis.
- Ældre SDK'er og SBMP er meldt til retirement 30. september 2026 (uverificeret). Brug `Azure.Messaging.ServiceBus`.

På HTTP-siden: `Idempotency-Key` er beskrevet i IETF draft-ietf-httpapi-idempotency-key-header-07 (15. oktober 2025) - **stadig et draft, ikke en RFC**, og den siger ikke hvor længe du skal huske nøglen, hvilket er hele det svære.

## Konsistens: hold op med at bruge CAP

CAP er bevist for ét read-write register under total partition, siger intet om multi-objekt-transaktioner, og ingen reel database kan entydigt klassificeres som CP eller AP. Siger du "vi valgte AP frem for CP", hører en erfaren arkitekt en der har læst en systemdesignguide. Brug PACELC: konsistens/latens-afvejningen gælder også når netværket er sundt, og det er den du designer efter til daglig.

Oversættelsen til forretningen er halvdelen af rollen. Ikke "systemet er eventually consistent", men:

> Når indkøberen godkender certifikatet, er det gemt med det samme. Kundens ERP har det inden for 60 sekunder i 99% af tilfældene. Tager det længere, kan de se det i statusfeltet, og vi får alarm efter 5 minutter.

Det er et SLO, ikke en undskyldning. Træn det på en rigtig person og bed dem gengive konsekvensen bagefter.

## Nedbrydning: modulær monolit er defaulten

"Vi burde splitte det op i services" er det hurtigste selvmål i en arkitektsamtale. Microservices betaler sig ved organisatorisk skala eller genuint divergerende skaleringsbehov - ikke ved ambition. Med tre til fem udviklere i huset er ingen tærskelværdi i nærheden af opfyldt, og det skal du kunne sige uden at lyde undskyldende.

Den vindende formulering: modulgrænser håndhævet af compileren nu, så vi kan splitte om to år hvis behovet opstår - og her er arkitekturtesten der håndhæver det. Fowlers MonolithFirst og MicroservicePremium giver dig autoriteten på under en time. Et bredt citeret 2026-tal siger at ca. 42% har konsolideret microservices tilbage (uverificeret - indikation, ikke citat).

Betingelserne du skal kunne navngive før et split: deploy-frekvenskonflikt mellem moduler, teams der blokerer hinanden, divergerende skaleringsprofil (dokumentbehandling vs. portaltrafik), forskellige dataopbevaringskrav pr. modul. Tærskelværdier, ikke fornemmelser.

## Dokumenttunge flows

Dokumenthåndtering i skala er 90% metadata, retention, adgangskontrol og lifecycle - 10% at gemme bytes.

1. **Upload går uden om din API-proces.** Valet Key med kortlivet user delegation SAS. En 500 MB fil gennem din egen proces er et selvpåført problem.
2. **Søgning på metadata, ikke scanning.** "Certifikater der udløber inden for 30 dage" må ikke scanne 20 mio. blobs. Blob index tags er ét svar, databasemetadata et andet - lifecycle-regler kan maks. bruge 10 index tag-betingelser pr. regel.
3. **Retention kolliderer med sletteret.** Immutable containers med legal hold betyder at lifecycle-sletning ikke virker. Kræver en kunde sine data slettet mens en audit løber, er det ikke en teknisk fejl - det er en konflikt du skal have et skrevet svar på. Omnibus I (i kraft 18. marts 2026) udskød CSDDD's anvendelse til 26. juli 2029; presset forsvinder ikke, det forskydes.

## Fire spikes med fysisk output

Hver spike lukkes efter maks to uger, uanset om den føles færdig. ADR'en skrives **før** beslutningen - har du aldrig skiftet mening midt i at skrive en, skriver du dem på det forkerte tidspunkt. Brug MADR's minimale variant uændret.

**Spike A - Idempotent ingest fra et ERP du ikke kontrollerer (2 uger).** Byg en puller mod en åben offentlig API som stand-in. Kilden paginerer ustabilt, har intet pålideligt ændringstidsstempel og skifter felttyper uden varsel. Krav: ingen dubletter, ingen tabte opdateringer, genstart fra vilkårligt punkt, bevisførelse for hvad du modtog hvornår. Begrænsning: kilden ændrer sig ikke for din skyld, og rådata må ikke gemmes over 90 dage. Byg raw landing zone med indholds-hash, anti-corruption layer til canonical model, idempotens på business key, optimistic concurrency, checkpointing og reconciliation. Injicér fire fejl: dubletter, afbrudt kørsel midt i en side, ændret felttype, en record der forsvinder fra kilden.
*Output:* ADR "Idempotensnøgle - business key frem for message-id". Fejlinjektionssuite i CI. Målt dublet- og tabsrate før og efter idempotenslaget. Dataflow-diagram raw -> canonical.

**Spike B - Outbox uden framework (1-2 uger).** Gem en certifikatgodkendelse i databasen **og** publicér beskeden. Krav: intet publiceres for en rullet-tilbage transaktion; ingen commit ender uden at beskeden til sidst publiceres; rækkefølge pr. leverandør bevares. Begrænsning: ingen distribuerede transaktioner og **intet messaging-framework** - hånd-rul den. Outbox-tabel i samme transaktion som domæneændringen, relay der publicerer at-least-once, sessions med leverandør-id som SessionId. Dræb relay'et med `kill -9` i tre vinduer: efter commit før publish, efter publish før markering, midt i en batch. Kør gratis lokalt på Service Bus-emulatoren via Testcontainers.
*Output:* ADR "Outbox vs. dual write vs. change data capture". Måletabel over tab og dubletter i de tre kill-scenarier. Sekvensdiagram med fejlvinduerne markeret. Svar på hvad relay'et koster i latens, og hvornår polling holder op med at duere.

**Spike C - Poison messages, DLQ og replay (1-2 uger).** 0,3% af beskederne kan ikke behandles, af tre blandede årsager: ødelagte payloads, midlertidigt nedbrud downstream, og én tenant med misdesignede data. Krav: de 0,3% må ikke bremse resten; fejlede beskeder skal kunne genafspilles uden dubletter; "hvad fejlede for tenant 12 i går mellem 14 og 16" besvares på under to minutter. Klassificér transient vs. permanent, backoff med jitter for transient, øjeblikkelig dead-lettering for permanent. Byg en replay-CLI med filter på tenant og tidsrum, som respekterer idempotenslaget fra spike B. Afslut med en blindtest: en scriptet joker injicerer fejlen, du tager tid på at finde den.
*Output:* ADR "Retry- og DLQ-politik". Kørende replay-værktøj. Målt tid-til-diagnose. Reproduceret ordering-brud ved DLQ-replay med konsekvensen i klartekst. Liste over fejl der **ikke** kan klassificeres automatisk.

**Spike D - Saga med kompensation forretningen kan acceptere (2 uger).** Leverandøronboarding i fem trin: opret, anmod om certifikater, validér mod ekstern registerservice, opret i kundens ERP, aktivér. Trin 3 og 4 er eksterne, kan time out, og processen kan tage dage fordi et menneske skal uploade. Byg **begge** varianter i lille skala - orchestration og ren choreography - injicér timeout i trin 4 og fejl i trin 3, og mål det afgørende: hvor mange steder skal du kigge for at finde en hængende saga, og hvor lang tid tager det. Vigtigst er ikke koden: skriv kompensationen for hvert trin i klartekst og udpeg dem der **ikke** kan automatiseres. Anmodede certifikater kan ikke uanmodes. Rollback betyder sjældent DELETE, snarere "status Afvist, behold dokumenterne, notificér indkøberen".
*Output:* ADR "Orchestration vs. choreography" med de to målte diagnosetider som begrundelse. State-diagram med alle kompensationsstier og de menneskelige eskaleringspunkter.

**Timebudget:** ca. 20-24 timer læsning og 55-70 timer på de fire spikes. Med 10-15 timer om ugen dækker det måned 2-5, og kun hvis to-ugers-loftet holdes.

## Ressourcer

| Ressource | Prioritet | Tid | Hvad du henter |
|---|---|---|---|
| Azure Service Bus-dok: sessions, duplicate detection, DLQ, message loss | Kerne | 3-4 t, linje for linje | Tallene du skal kunne citere |
| DDIA 2. udg., Kleppmann & Riccomini (marts 2026) | Kerne | 25-35 t, selektivt | Replikation, partitionering, transaktioner, distribuerede fejl |
| Kleppmann: "Please stop calling databases CP or AP" | Kerne | 30 min | Fjerner den dyreste enkeltmisforståelse |
| Fowler: MonolithFirst, MicroservicePremium, StranglerFig | Kerne | 1 t samlet | Autoritet til at afvise et split |
| `microservices.io/patterns`, `enterpriseintegrationpatterns.com`, Azure Cloud Design Patterns | Støtte | 6-8 t, kun som opslag | Ordforrådet: Outbox, Saga, Claim Check, Valet Key. Læs aldrig Hohpe forfra |
| The Hard Parts - distribuerede transaktioner, data ownership | Støtte | 8-10 t | Trade-offs uden facit |
| `github.com/kgrzybek/modular-monolith-with-ddd` (.NET 8 - port mønstrene) | Kerne | 6-8 t | Modulgrænser i praksis |
| MADR (`adr.github.io/madr`) | Kerne | 30 min | Skabelonen. Opfind ikke din egen |
| System Design Interview (Alex Xu) | Spring over | 0 t | Hyperscale consumer-systemer; dit problem er kobling |

## Certificeringer

| Eksamen | Status (verificeret sep. 2026) | Rolle |
|---|---|---|
| AZ-305 | Aktiv; opdateret 17. april 2026 | Deadline-motor og vokabular. **AZ-104 er hård forudsætning for Expert-badget** |
| AZ-400 | Aktiv; opdateret 27. juli 2026 | Kun på CI/CD-sporet. Forudsætning: AZ-104 eller Developer Associate |
| AZ-204 | **Pensioneret 31. juli 2026** | Enhver kilde der stadig anbefaler den, er forældet |
| AI-200 | Efterfølgeren, AI-drejet | Ikke en generel .NET-eksamen. Ventes som AZ-400-forudsætning (uverificeret) |
| TOGAF / iSAQB CPSA-F | - | Fravælg eksplicit; begrundelsen er et modenhedssignal |

## Priser

| Post | Pris | Note |
|---|---|---|
| Container Apps | 0 kr. inden for gratistildelingen | 180.000 vCPU-sek., 360.000 GiB-sek., 2 mio. requests/md. `minReplicas` over 0 faktureres alle 730 timer/md. |
| Service Bus Standard | Fast månedlig udgift | Basic har hverken topics eller duplicate detection (pris uverificeret) |
| Defender for Storage, on-upload scan | Ca. 0,15 USD/GB, første 50 TB/md. | Default-loft 10.000 GB/md. pr. konto (uverificeret) |
| MassTransit v9 (jan. 2026) | Kommerciel, fra ca. 400 USD/md. | v8 er Apache-2.0, mister support ultimo 2026. MIT: Wolverine, Rebus, Brighter |

Budget alert på dag ét. Prissæt før du deployerer.

## Faldgruber

- **Microservice-svaret.** Foreslår du et split, taber du rummet øjeblikkeligt.
- **Event sourcing fordi det ser arkitektonisk ud.** Dokumenterede 2025-2026-erfaringer: 300 linjers upcasting-kode, fire samtidige event-schemaer, read models der gjorde skrivninger langsommere. Kun når revisionssporet **er** forretningskravet, og kun i én bounded context.
- **At bygge et produkt i stedet for en spike.** Symptomet er præcist: første gang du får lyst til en dashboardside, er du holdt op med at lære arkitektur.
- **Ikke at måle.** En spike uden et tal er et blogindlæg.
- **Duplicate detection forvekslet med idempotens.** Den virker på MessageId i et 10-minutters vindue. Dit problem er forretningsniveau og timer eller dage.
- **Kun Microsoft-kilder fordi du er på Azure.** AWS' SaaS Lens er skarpere på tenant isolation og control plane vs. application plane. Kan du kun én leverandørs ordforråd, afslører du dig i mødet med en anden stack.
- **Ingen ekstern modstand.** Ingen på arbejdet kan presse dig på et designvalg. Får spike A-D aldrig øjne udefra, kan du øve det forkerte i tolv måneder uden at opdage det. Book modstanden i kalenderen.

## Sådan ved du at du kan det

1. Du tegner de fem integrationsstile på under 10 minutter uden noter, med latens, kobling og fejlejerskab for hver.
2. Du kan forklare hvorfor idempotensnøglen er en business key og ikke et message-id, med **din egen** nøgle fra spike A, og sige hvad der sker når kunden ændrer et felt i den.
3. Du kan fremvise en måletabel over tab og dubletter i tre kill-scenarier, før og efter outbox. Tal fra din egen kørsel.
4. Du kan citere fire konkrete Service Bus-begrænsninger og sige hvad hver af dem **ikke** løser.
5. Du forklarer konsistensvinduet til en ikke-teknisk person på under tre minutter uden ordet "eventual", og personen gengiver konsekvensen korrekt.
6. Du har en målt tid-til-diagnose fra en blindtest og ved hvad der forkortede den.
7. Du kan navngive tærskelværdierne der ville få dig til at splitte en modulær monolit - og sige højt at ingen af dem er opfyldt der hvor du sidder.
8. Du kan pege på mindst tre kompensationsstier i en saga der **ikke** kan automatiseres, og beskrive den forretningsproces de kræver.
9. Du har fire ADR'er fra sektionen med navngivne fravalgte alternativer og en eksplicit "dette ville få mig til at ombestemme mig"-betingelse.
10. En fremmed senior arkitekt har presset dig i 45 minutter på trade-offs i ét af spike-problemerne uden at du faldt tilbage på lærebogsformuleringer. Det eneste kriterium der ikke kan bedømmes indefra, og derfor det tungeste ved kompetenceporten.
