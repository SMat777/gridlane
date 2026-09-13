# C05 — Tilgængelighed som salgsblokering

| | |
|---|---|
| **Type** | Frontend-arkitektur og grænser |
| **Primært modul** | 05 — Frontend-arkitektur set fra arkitektstolen |
| **Sekundære moduler** | 10 (Produkt, prioritering og leverance), 11 (Kommunikation og indflydelse) |
| **Timebox** | 6 timer, hård. Præmisskiftet lægges oveni og må koste maks. 45 minutter ekstra |
| **Sværhedsgrad** | 4 af 5. Let på teknik, hård på afgrænsning og på at skulle formulere en delvis overholdelse skriftligt til en offentlig kunde, mens en kollega allerede har svaret "ja" i et tilbud. Giver mening i **måned 6-9**: før måned 6 har du hverken læst WCAG 2.2's AA-kriterier filtreret eller bygget F1, og så bliver grænsediskussionen en mening; efter måned 10 har repo-auditrutinen og F3-driften foræret dig halvdelen af diagnosen. Bedst i **måned 7-8**. Kør den igen i måned 12 med samme rubrik |
| **Afleveringsformat** | Ti artefakter: kravsspørgsmålsliste (1 side, tidsstemplet), målt baseline (regneark + 0,5 side), skillelinjen salgsblokering mod teknisk gæld (maks. 1,5 side), udkast til tilgængelighedsredegørelse (maks. 2 sider, til ekstern ikke-teknisk læser), grænsenotat med de nej'er der skrives ned (1 side), ADR om eje eller leje tilgængelighedslaget (maks. 1,5 side, MADR-minimal), fravalgsnotat (1 side), seksugersplan med navne og timer (0,5 side), notat til Jens og Katrine (præcis 1 side, ikke-teknisk), selvvurdering (0,5 side). I alt maks. 9,5 sider brødtekst plus ét regneark |

> Alle personer, kunder og leverandører i denne case er opdigtede. Kontraktbeløb, timepriser og målte tal er konstrueret, men i den størrelsesorden en dansk ni-mandsvirksomhed med en offentlig rammeaftale reelt ligger i. **Slå ikke WCAG-kriterienumre op midt i timeboxen.** Casen kan ikke løses ved at læse W3C's quickref, og bruger du halvanden time på det, har du valgt den eneste del af opgaven der ikke kræver en afvejning. Skal et kriterienummer stå i et kundedokument, mærker du det som ukontrolleret og verificerer det efter timeboxen. Det er i øvrigt præcis den disciplin casen måler.

## Situationen

Torsdag den 10. september 2026, kl. 08.40. Katrine har printet noget ud, hvilket hun aldrig gør.

Kontrakten med Indkøbsfællesskab Midtjylland I/S blev underskrevet onsdag den 2. september. Fjorten kommuner, ca. 2.900 leverandører, 520.000 kr. om året i fire år med option på to. Det er husets største aftale nogensinde, og Katrine har tre andre offentlige indkøbsorganisationer i pipelinen for 2027 der har spurgt til den samme rammeaftale. Driftsstart er den 1. december.

Det hun har printet, er bilag 4. Der står noget om WCAG 2.2 niveau AA og om en redegørelse senest seks uger efter underskrift, altså den 14. oktober. Katrine har streget to linjer under og siger, at hvis vi ikke kan dokumentere at vi overholder WCAG 2.2 AA inden da, kan de gå fra kontrakten. Hun henviser til tilgængelighedsloven; det gjorde deres udbudsjurist også på kick-off-mødet. Hun har selv besvaret tilbuddets bilag 4 den 19. juni med et "Ja" uden forbehold og vedhæftet en Lighthouse-rapport med 94 ud af 100 i tilgængelighed. Hun kan ikke huske hvilken side rapporten er kørt på, men hun husker at Thomas sagde den var fin.

Thomas kigger op og siger, at vi bruger MUI, at MUI er tilgængeligt, og at resten er en uges arbejde hvis nogen gider læse fejlene igennem. Han tilføjer at leverandørportalen ikke er hans; den byggede Aleks Rytter færdig i februar 2025, og Aleks svarer ikke på LinkedIn.

Sofie har siddet tre uger med leverandøroversigten. Fjordhus Retail Group har skrevet to gange at listen "dør" når deres kvalitetsafdeling filtrerer i den, og deres kvalitetschef har eskaleret det til Mette. Sofie siger at tabellen har 4.130 rækker, at det selvfølgelig er for mange at rendere, og at hun er begyndt på en gren der virtualiserer den. Hun spørger om hun skal fortsætte.

I frontend-repoet ligger der en `apiClient.ts` fra 2019 på axios, en NSwag-genereret klient der bruges fire steder, elleve filer der kalder `fetch` direkte, og auditmodulet, som bruger TanStack Query. Server-state ligger i Redux-slices navngivet efter endpoints, i Zustand-stores som Sofie har indført, og i query-cachen i auditmodulet. Der er en Opdater-knap på leverandøroversigten. Den har været der siden 2021.

Helle Bang, kontraktansvarlig hos IFM, nævnte på kick-off at en af deres kategoriindkøbere, Karina Lund, bruger skærmlæser og bliver daglig bruger fra 1. december. Ingen hos os har åbnet leverandørportalen med en skærmlæser.

Jens stak hovedet ind i går eftermiddags. Han sagde til Helle Bang den 2. september at "det er på plads, vi bruger et standardkomponentbibliotek". Han har møde med hende **tirsdag den 22. september kl. 10.00**, og han er i dårligt humør om penge efter augustregningen fra Azure. Til dig sagde han: "Sig til hvis der er noget der ikke holder. Jeg skal bare vide om jeg kan sige ja til de tre andre."

Der findes ingen telemetri fra browseren. Den blev slået fra i 2023.

Du har seks timer.

## Det du skal aflevere

| # | Artefakt | Format | Krav der ikke kan forhandles |
|---|---|---|---|
| 1 | **Kravsspørgsmål** | 1 side, tidsstemplet pr. spørgsmål | Skrevet **før** første biblioteksnavn, første komponentnavn og ordet virtualisering. Hver linje har en note om hvad svaret ville ændre |
| 2 | **Målt baseline** | Regneark + 0,5 side | Mindst fire performancetal og ét defekttal, hver med antal kørsler/målinger og et spænd. Tiden i leverandøroversigten skal være **attribueret**: hvor mange af sekunderne ligger hvor, i procentpoint med spænd. Gættede tal mærkes som gæt i regnearket |
| 3 | **Skillelinjen** | Maks. 1,5 side, tabel | To adskilte lister: hvad der er en salgsblokering med kontraktdato og kronebeløb, og hvad der er teknisk gæld med en konsekvens. Poster der står i begge lister skal stå i begge, med begrundelsen. Plus hvad der **ikke** bliver rørt i vinduet, og prisen for at lade det ligge |
| 4 | **Udkast til tilgængelighedsredegørelse** | Maks. 2 sider | Skrives til IFM's udbudsjurist, ikke til en udvikler. Skal angive overholdelsesniveau, kendte afvigelser med afhjælpningsdato, hvad der er testet og hvordan, hvad der **ikke** er testet, og hvem der skriver under. Ingen lovtitel du ikke har slået op |
| 5 | **Grænsenotat** | 1 side | De nej'er der skal skrives ned, hvert med hvor det håndhæves, hvem der ejer det, og **betingelsen der vender svaret** |
| 6 | **ADR: eje eller leje tilgængelighedslaget** | Maks. 1,5 side, MADR-minimal | Prissat i **vedligeholdelsestimer over tre år**, ikke implementeringstimer, med spænd i procent. Afsnittet "Dette ville få os til at vælge om" med mindst tre betingelser, hver med tærskel og enhed |
| 7 | **Fravalgsnotat** | 1 side i alt | To forkastede alternativer, hvert afvist på **én navngiven, målbar akse med et tal** — ikke to akser, ikke en holdning |
| 8 | **Seksugersplan** | 0,5 side + én simpel tidslinje | Navne, timer pr. uge, og hvad der bliver fortrængt hos hvem. Summen skal svare til kapacitet der findes. Mindst én milepæl der ligger uden for vores kontrol, med hvad vi gør hvis den skrider |
| 9 | **Notat til Jens og Katrine** | Præcis 1 side | Nul jargon. To muligheder med pris, én anbefaling, hvad vi lover IFM den 14. oktober, hvad vi ikke lover, og hvad Jens kan sige til Helle Bang den 22. Læsbart på fire minutter |
| 10 | **Selvvurdering** | 0,5 side | Hvilke af dine egne kravsspørgsmål endte du med at besvare med et gæt, og hvilket gæt bærer mest af redegørelsen |

**Artefakt 2 og 6** er dem der har tal med angivet usikkerhed. **Artefakt 4 og 9** skrives til ikke-tekniske læsere, og artefakt 4 er det eneste af de ti der forlader huset og bliver til et kontraktdokument. **Mindst én post i artefakt 3 skal koste over 20.000 kr. eller over otte udviklerdage**, og den pris skal også stå i artefakt 9. En liste hvor alt er billigt er ikke en liste, det er en ønskeseddel.

## Skjulte oplysninger

Du må kun læse svaret på et spørgsmål, du **faktisk har skrevet ned** på artefakt 1, før du begyndte at designe. Skriver du fem spørgsmål og læser fjorten svar, har du ikke lavet casen — du har læst en løsning, og du kan ikke score over 1 på K1 og K2.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Hvad står der **ordret** i bilag 4 om tilgængelighed? | Punkt 3.2: *"Leverandøren fremsender senest 6 uger efter kontraktunderskrift en tilgængelighedsredegørelse efter EN 301 549 for de dele af løsningen, der anvendes af Ordregivers medarbejdere og af tilbudsgivere og leverandører. Redegørelsen angiver kendte afvigelser og en tidsplan for afhjælpning."* Punkt 3.4: *"Væsentlige afvigelser i de i bilag 2 angivne kernearbejdsgange, som ikke er afhjulpet senest 6 måneder efter driftsstart, udgør væsentlig misligholdelse."* Der står ikke ét sted at løsningen skal overholde WCAG 2.2 AA den 14. oktober. Der står at der skal ligge en sandfærdig redegørelse den 14. oktober, og at kernearbejdsgangene skal være i orden **1. juni 2027** |
| 2 | Hvilke arbejdsgange står i bilag 2 som kernearbejdsgange? | Tre: (a) en leverandør opretter sig selv og gennemfører prækvalificering, (b) en leverandør uploader et certifikat og besvarer et spørgeskema, (c) en indkøber godkender eller afviser en leverandør og ser begrundelsen igen bagefter. To af de tre ligger helt i leverandørportalen. Ingen af de tre er leverandøroversigten |
| 3 | Hvad svarede Katrine præcis i tilbuddet den 19. juni, og er det en del af kontrakten? | Ja. Tilbuddet er bilag 1 og har forrang efter kontraktens § 2 for alt der ikke er reguleret andetsteds. Svaret lyder: *"Ja. RELATIONS overholder WCAG 2.2 niveau AA."* Uden forbehold, uden dokumentation, med en Lighthouse-rapport vedhæftet. Rapporten er kørt den 17. juni på `leanlinking.com/login` — marketingsitets loginside, ikke applikationen. Jens har skrevet under på tilbuddet. Katrine har givet samme svar i sikkerhedsspørgeskemaer til tre private kunder i 2025 |
| 4 | Har nogen kørt en tilgængelighedsgennemgang på selve applikationen? | Sofie kørte axe DevTools på ni skærme den 26. august: **148 fund**, hvoraf 96 kommer fra fire regeltyper — kontrast på statusbadges (grøn/gul/rød på hvid), formularfelter uden programmatisk label, `aria-required-children` i datagriddet, og links uden tilgængeligt navn. Hun noterede i samme fil at "værktøjet fanger vist kun 30-40 % af kriterierne" med kilde til leverandørens eget markedsføringsmateriale. Tallet er ikke efterprøvet, og hun har ikke kørt på leverandørportalen |
| 5 | Hvad sker der i login-flowet for en ekstern leverandørbruger? | To ting. Leverandøren får en sekscifret kode på mail og skal skrive den i et felt der **blokerer indsætning** (tilføjet i 2022 efter en phishing-hændelse hos en kunde). Og efter tre fejlede forsøg vises en billedgåde fra en ekstern bot-beskyttelse indkøbt i 2023. Begge dele ligger foran alle tre kernearbejdsgange. Bot-beskyttelsen kan ikke konfigureres væk uden leverandørens medvirken: 4-6 ugers leveringstid og 18.000 kr. for et alternativt flow. Kontrakten med dem løber til 31. marts 2027 |
| 6 | Hvor ligger de 6,2 sekunder i leverandøroversigten? | Målt på Fjordhus' tenant, 4.130 rækker, 4x throttlet CPU, fem kørsler: **6,2 s til interaktiv, spænd 5,4-7,1 s**. Fire kald udføres sekventielt: `/suppliers` (server-p95 2,84 s, App Insights, 30 dage, n=4.812), `/certificates/summary` 0,91 s, `/scorecards/latest` 1,12 s, `/permissions` 0,28 s. Klientrendering af de 4.130 rækker: **1,4 s, tre kørsler, 1,2-1,6 s**. Tastetryk i filterfeltet: p50 480 ms, p95 1.240 ms, fordi hvert tastetryk henter forfra uden debounce og uden cache |
| 7 | Hvilke hjælpemidler bruger leverandørbrugerne, og hvor mange er de? | **Det ved vi ikke.** Browsertelemetrien blev slået fra i marts 2023 efter en GDPR-gennemgang og aldrig tændt igen. Vi kan tælle sessioner i backend-logs, men ikke browser, ikke skærmlæser, ikke zoomniveau, ikke inputmetode. Der er 11.400 eksterne leverandørbrugere på tværs af 34 tenants. Vi ved om Karina Lund fordi Helle Bang nævnte det, ikke fordi vi kan se det. Det er ikke en manglende oplysning der kan hentes; det er et arkitekturvilkår du skal skrive ind i redegørelsen |
| 8 | Hvilke skærme bruger hvilket komponentbibliotek? | 28 skærme i alt: 22 køberside, 6 leverandørside. MUI v5 (indført 2021, aldrig opgraderet) på 17 køberskærme. Håndrullede komponenter på de 6 leverandørskærme — Aleks byggede egne modal-, tabel-, kombinationsfelt- og filuploadkomponenter, uden tests, med tre forskellige fokusmønstre. Et kommercielt datagrid fra 2019 på 5 skærme, licens 1.450 EUR/år for tre udviklere; leverandørens tilgængelighedsrettelser ligger i en major der ændrer kolonne-API'et på alle fem skærme, anslået 5-8 udviklerdage |
| 9 | Hvad koster en ekstern audit, og hvor lang er leveringstiden? | Adgang & Co ApS, Aarhus: fuld gennemgang af 14 flows, 62.000 kr. ekskl. moms, opstart om 4-5 uger, rapport 6 arbejdsdage senere. Den lander **efter** den 14. oktober. Afgrænset gennemgang af 4 flows: 24.000 kr., opstart om 8 arbejdsdage, rapport 6 arbejdsdage senere. Brugertest med to skærmlæserbrugere, to timer: 14.000 kr., kan bookes med tre ugers varsel. De vil have en stabil testkonto og et testmiljø med realistiske data |
| 10 | Hvad har vi af faktisk kapacitet frem til 14. oktober? | Sofie: 3 dage/uge til og med 30. september bundet på IFM-onboarding sammen med Mette, derefter 4 dage/uge. Thomas: ca. 1 dag/uge, og han vil helst ikke røre leverandørportalen. Rasmus: booket på drift til 15. oktober. Mette: kører tre onboardings. Dig: det du kan tage uden at noget andet skrider. Belastet kostpris 3.100 kr./dag; den timepris salg fakturerer kundetilpasninger til er 8.400 kr./dag |
| 11 | Hvad siger IFM's egen tilgængelighedsansvarlige? | Dorthe Vestergaard, digitaliseringskonsulent: *"En redegørelse med afvigelser og datoer er fuldt acceptabel. En redegørelse uden afvigelser er ikke troværdig, og så beder vi om at se testgrundlaget."* Hun er mest optaget af om Karina kan gennemføre en godkendelse selv, og om en leverandør kan uploade et certifikat uden at ringe. Hun har ikke læst tilbuddets bilag 4 og ved ikke at der står "ja" i det |
| 12 | Hvad koster det os hvis IFM hæver, og hvad står der i pipelinen? | IFM: 520.000 kr./år i fire år, driftsstart 1. december, første fakturering 1. januar. Bruttofortjenesten i huset er 4,2 mio. kr., så aftalen er ca. 12 % af den. Katrines pipeline for 2027 rummer tre offentlige indkøbsorganisationer, samlet anslået 1,1 mio. kr./år, og alle tre har spurgt om den samme rammeaftale. Hun har ikke sat sandsynligheder på. En hævelse i utide ville i praksis også fjerne de tre |
| 13 | Er der noget i produktet der allerede afhænger af den langsomme oversigt? | Ja, og det er ikke pænt. Leverandøroversigten er den eneste skærm hvor en køber kan se OTIF, PPM og claims-tal side om side, og Fjordhus bruger den i deres kvartalsvise business reviews. Deres kvalitetschef har skrevet at hun eksporterer til Excel og arbejder videre der, fordi listen er for langsom. Der findes ingen eksportknap; hun markerer og kopierer. To andre kunder gør formentlig det samme, men det er ikke undersøgt |
| 14 | Hvad ved vi om hukommelsesforbruget over en arbejdsdag? | Én måling, én maskine, én bruger: Sofie lod en fane stå åben i seks timer på Fjordhus' tenant og gik fra 210 MB til 1,6 GB uden genindlæsning. To brugere hos Fjordhus har over sommeren skrevet at fanen "dør" cirka en gang om ugen, typisk sidst på eftermiddagen. Der er ingen målinger fra kundemaskiner, og der kan ikke laves nogen uden telemetri. Ingen har koblet de to ting sammen før nu |

## Præmisskiftet

**Åbnes først når 3 timer og 36 minutter af timeboxen er gået (60 %). Ikke før. Sæt en timer.**

Torsdag den 10. september kl. 14.05 videresender Katrine en mail fra Dorthe Vestergaard. Ændringen er ét faktum: **IFM er selv omfattet af det offentlige tilsyn med tilgængelighed, og IFM's leverandørportal — altså vores produkt — er udtrukket til den dybdegående kontrol i tilsynsrunden januar til marts 2027.** Det er lovligt, det er varslet, og IFM kan ikke fravælge det. Fire ting følger:

1. **Redegørelsen bliver offentlig.** Den indgår i IFM's egen tilgængelighedserklæring på deres hjemmeside, med produktnavnet i. Hver afvigelse du skriver ned, kan læses af de tre andre offentlige indkøbsorganisationer i Katrines pipeline, af konkurrenter og af enhver leverandør der overvejer at klage.
2. **Kontrollen rammer leverandørsiden.** Den dybdegående kontrol følger den arbejdsgang en ekstern leverandør går igennem: opret konto, prækvalificér, upload certifikat, besvar spørgeskema. Det er de seks skærme Aleks byggede, som ingen ejer, som ingen har testet, og som ikke bruger komponentbiblioteket.
3. **IFM kræver en feedbackmekanisme i produktet** fra driftsstart: en navngiven kontaktperson, en kanal en bruger med hjælpemiddel kan skrive i, og svar inden for 30 dage. Det er en produktfunktion med en supportproces bagved, og den står ikke i noget estimat.
4. **Jens skærer auditbudgettet.** Efter augustregningen fra Azure er loftet 25.000 kr., ikke 62.000. Han siger: "Find en billigere måde. Og jeg skal stadig kunne sige ja til de tre andre."

**Hvad skiftet er en test af**

- Om du **skifter scope** frem for at forsvare det du allerede har skrevet. Halvdelen af dit arbejde de første 3,5 timer handlede sandsynligvis om leverandøroversigten og køberskærmene. Kontrollen rammer et andet sted. En omregnet plan inden for 45 minutter er beviset; en velformuleret forklaring på hvorfor det du lavede stadig er relevant, er det ikke.
- Om du kan sige højt hvad der **ikke** ændrer sig. Mindst to af dine beslutninger er fuldstændig upåvirkede af de fire linjer. Kan du udpege dem, har du forstået dit eget design.
- Om din **faldsbetingelse fra ADR'en faktisk udløses** af linje 2 eller linje 4 — og om du så følger den, eller finder en grund til at lade være. Det er casens skarpeste enkeltmålepunkt.
- Om offentligheden i linje 1 får dig til at skrive **mere** præcist eller **mindre** præcist. Begge reaktioner er menneskelige; kun den ene holder i marts 2027.
- Om linje 3 behandles som et **spørgsmål til Katrine og Mette** — hvem svarer, inden for hvilken frist, i hvilken kanal — eller som en knap du selv skal have bygget inden den 14. oktober.
- Om linje 4 ændrer **hvad du køber**, ikke bare hvor meget. 25.000 kr. rækker til én af de tre ting hos Adgang & Co, og valget mellem dem er hele afvejningen.

## Rubrik

Tolv kriterier, hvert scoret 0-3, med vægt. Maksimum er **99 point**. Ankrene er tællelige med vilje: en bedømmer skal kunne sætte scoren uden at kende kandidaten og uden at bruge ordet "god".

| # | Kriterium | Vægt | Maks. |
|---|---|---|---|
| K1 | Kravsspørgsmål før første biblioteksnavn | 3 | 9 |
| K2 | Spørgsmålene rammer de akser der vælter designet | 2 | 6 |
| K3 | Salgsblokering skilt fra teknisk gæld, i kroner og datoer | 3 | 9 |
| K4 | Redegørelsens ordlyd: hvad den lover, og hvad den ikke lover | 3 | 9 |
| K5 | Egne målte tal med spænd, ikke Googles | 3 | 9 |
| K6 | Hvad målingen ikke fanger | 2 | 6 |
| K7 | Eje eller leje tilgængelighedslaget, prissat over tre år | 2 | 6 |
| K8 | Grænserne der stopper rådnen, håndhævet ét sted | 3 | 9 |
| K9 | Fravalgene afvist på én navngiven, målbar akse | 3 | 9 |
| K10 | Faldsbetingelsen | 3 | 9 |
| K11 | Planen og nej'et en ikke-teknisk læser kan handle på | 3 | 9 |
| K12 | Iteration ved præmisskiftet | 3 | 9 |
| | **I alt** | **33** | **99** |

### K1 — Kravsspørgsmål før første biblioteksnavn (vægt 3)

*Findes fordi:* frontend er det emne hvor det er lettest at begynde med et bibliotek. Både Thomas og Sofie har allerede gjort det, hver sin vej, inden nogen har læst bilag 4.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen spørgsmålsliste, eller den er skrevet bagefter. Et biblioteksnavn, et komponentnavn eller ordet "virtualisering" optræder inden for de første 20 minutter |
| 1 | 3-7 spørgsmål, ikke tidsstemplede, og mindst ét er et løsningsforslag i spørgeform ("skal vi skifte til headless primitives?") |
| 2 | 8-11 tidsstemplede spørgsmål skrevet før første biblioteksnavn, ingen produktnavne, mindst fem rammer skjulte oplysninger, hver med en note om hvad svaret ville ændre |
| 3 | 12+ tidsstemplede spørgsmål, mindst otte rammer skjulte oplysninger, listen er gennemgået igen til sidst, og det står markeret hvilke der **stadig** er ubesvarede i den afleverede redegørelse og hvilken påstand i redegørelsen der derfor hviler på et gæt |

### K2 — Spørgsmålene rammer de akser der vælter designet (vægt 2)

*Findes fordi:* tolv spørgsmål om komponentbiblioteker er ét spørgsmål. De seks dyre akser her er: hvad bilag 4 kræver **ordret** og hvornår; hvilke arbejdsgange der er i scope; hvad der allerede er erklæret skriftligt og af hvem; hvor tiden i oversigten faktisk ligger; hvad der ligger **uden for** komponentlaget (login, bot-beskyttelse, tredjepartsgrid); og hvad vi overhovedet kan måle selv.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen af de seks akser berørt |
| 1 | 1-2 af de seks |
| 2 | 3-4 af de seks, og mindst ét spørgsmål indeholder selv et tal ("hvor mange af de 28 skærme er i bilag 2's arbejdsgange?") |
| 3 | Mindst fem af de seks, plus mindst ét spørgsmål der ville have afdækket at der allerede er afgivet et ubetinget "ja" i tilbuddet, og mindst ét der er formuleret som det skal stilles til IFM, ikke til en kollega |

### K3 — Salgsblokering skilt fra teknisk gæld, i kroner og datoer (vægt 3)

*Findes fordi:* casen indeholder to problemer der ligner ét. Blandes de, får du enten et frontend-oprydningsprojekt ingen godkender, eller en redegørelse skrevet oven på en kodebase ingen tør love noget om.

| Score | Sådan ser det ud |
|---|---|
| 0 | Én samlet liste. Ordet "refaktorering" står i en overskrift, eller state-mønstrene og WCAG-fejlene behandles som samme opgave |
| 1 | Skelner i ord, men uden datoer og uden kroner. "Vigtigt" og "kan vente" bruges som kategorier |
| 2 | To adskilte lister. Salgsblokeringen har kontraktdato (14. oktober, 1. december, 1. juni 2027) og kronebeløb (520.000 kr./år, plus hvad væsentlig misligholdelse betyder); gældsposterne har hver en konsekvens, mindst tre af dem med et tal |
| 3 | Ovenstående, plus mindst tre poster der **står i begge lister** med begrundelsen for hvorfor (datagrid-versionen, kaldsmønsteret der gør måling umulig, de tre state-mønstre der gør en fokusrettelse tre steder), plus en eksplicit liste over hvad der ikke bliver rørt i vinduet med prisen for at lade det ligge, plus mindst én post over 20.000 kr. eller otte udviklerdage |

### K4 — Redegørelsens ordlyd: hvad den lover, og hvad den ikke lover (vægt 3)

*Findes fordi:* det er det eneste artefakt der forlader huset og bliver til kontrakt. En redegørelse er ikke en tilstandsrapport, det er en erklæring nogen skriver under på.

| Score | Sådan ser det ud |
|---|---|
| 0 | Redegørelsen erklærer overholdelse uden dokumentation, **eller** citerer en dansk lovtitel kandidaten ikke har slået op, **eller** gentager Katrines "ja" fra 19. juni som om det var testet |
| 1 | Bruger EAA, EN 301 549 og WCAG 2.2 AA i flæng som om de var det samme. Ingen afvigelsesliste, eller en afvigelsesliste uden datoer |
| 2 | Trelagsmodellen står rigtigt (EAA → EN 301 549 → WCAG 2.2 AA), erklæringen er **delvis overholdelse**, kendte afvigelser er listet med afhjælpningsdato, og det står hvad der er testet, hvordan og hvornår |
| 3 | Ovenstående, plus mindst tre af disse fem: ordlyden holder når IFM's jurist læser den ved siden af tilbuddets "ja" fra 19. juni; der står eksplicit hvad vi **ikke** har testet og hvornår vi gør det, med dato; der står hvad vi ikke ved om brugernes hjælpemidler og hvad vi gør ved det; kriterienumre er enten verificerede eller udeladt, ikke gættet; og der står hvem der skriver under, med navn og rolle |

### K5 — Egne målte tal med spænd, ikke Googles (vægt 3)

*Findes fordi:* Lighthouse-rapporten fra marketingsitet er allerede vedhæftet et tilbud. Lånte metrikker er det modsatte af arkitektur, og her har de allerede kostet noget.

| Score | Sådan ser det ud |
|---|---|
| 0 | Citerer Core Web Vitals, en Lighthouse-score eller et LCP-tal for en applikation bag login som om det betød noget |
| 1 | Ét eller to tal uden antal kørsler, uden spænd og uden hvor de er målt |
| 2 | Mindst fire målte tal (kold indlæsning, serverens p95, tastetrykslatens, klientrendering), hver med antal kørsler og et spænd i millisekunder eller procent, plus én sætning om hvilken brugerkendsgerning et budget skal udledes af |
| 3 | Ovenstående, plus at tiden er **attribueret**: hvor mange af de 6,2 s ligger i sekventielle kald, i serverens forespørgsel og i klientrendering, i procentpoint med spænd; plus mindst ét budgettal med en navngiven brugerkendsgerning bag; plus at hukommelsesvæksten er taget med som en åben måling med den usikkerhed én måling på én maskine faktisk har — ikke som et faktum og ikke ignoreret |

### K6 — Hvad målingen ikke fanger (vægt 2)

*Findes fordi:* 148 automatiske fund ligner en facitliste og er det ikke. Den dyre halvdel af WCAG kan kun afgøres af et menneske, og casen er tabt hvis værktøjets output bliver til afhjælpningsplanen.

| Score | Sådan ser det ud |
|---|---|
| 0 | De 148 fund behandles som listen over hvad der skal rettes |
| 1 | Nævner at automatiserede værktøjer ikke fanger alt, uden et tal, uden kilde og uden konsekvens for planen |
| 2 | Skiller automatiske fund fra manuelt arbejde, angiver en dækningsandel **med kilde og med forbehold om at kilden er leverandørens eget tal**, og navngiver mindst tre ting der kun kan afgøres manuelt (fokusrækkefølge, fejlidentifikation, navn/rolle/værdi på håndrullede komponenter) |
| 3 | Ovenstående, plus at der er sat pris og dato på den test kun et menneske med hjælpemiddel kan lave, plus at det står hvad vi gør indtil den test findes, plus at de kriterier der er nye i 2.2 er behandlet særskilt fordi ingen gammel checkliste og intet gammelt værktøjssæt indeholder dem |

### K7 — Eje eller leje tilgængelighedslaget, prissat over tre år (vægt 2)

*Findes fordi:* det er den højeste løftestang i hele frontend-arkitekturen for et hus af denne størrelse, og den eneste beslutning her der stadig gælder om tre år.

| Score | Sådan ser det ud |
|---|---|
| 0 | Vælger bibliotek på popularitet, på hvad Sofie kender, eller på GitHub-stjerner |
| 1 | Nævner de tre optioner (egne primitiver, headless primitives, fuldt system) men prissætter dem i implementeringstimer |
| 2 | Tre optioner prissat i **vedligeholdelsestimer over tre år** med spænd i procent, og et eksplicit svar på hvad syv årsværk kan bære uden en tilgængelighedsspecialist |
| 3 | Ovenstående, plus at valget er koblet til hvilke skærme der faktisk er i scope (ikke alle 28), plus et navngivet afkald (designfrihed, migrationen på datagriddet i 5-8 udviklerdage, en licens der skal fornys), plus et tal for hvad det koster at udskyde beslutningen et år |

### K8 — Grænserne der stopper rådnen, håndhævet ét sted (vægt 3)

*Findes fordi:* tre state-mønstre og fire kaldsmåder er ikke dårlig kode. Det er fravær af en grænse, og en grænse uden håndhævelsespunkt er en aftale der holder til den næste travle uge.

| Score | Sådan ser det ud |
|---|---|
| 0 | Foreslår oprydning uden håndhævelse. Sætningen "vi bliver enige om at bruge X fremover" optræder i en eller anden form |
| 1 | 1-2 regler, uden at det står hvor de håndhæves eller hvem der ejer dem |
| 2 | Mindst tre af de fem rådnemekanismer adresseret, hver med ét håndhævelsespunkt (query-cache-laget, komponentlaget, en CI-gate der fejler builden, cache-headers og versionsstempel), hver med en navngiven ejer |
| 3 | Ovenstående, plus en **dokumenteret nødudgang** (gaten kan overrules med en ADR-reference), plus et tal for hvad grænsen koster den rigtige vej (sekunder pr. build eller minutter pr. PR), plus en dato hvor de fire kaldsmåder er skåret ned til én og hvad der sker hvis den dato skrider. Opdater-knappen er nævnt som diagnose, ikke som feature |

### K9 — Fravalgene afvist på én navngiven, målbar akse (vægt 3)

*Findes fordi:* et fravalg afvist på smag er en holdning med overskrift. Casen har mindst fem oplagte alternativer, og hvert af dem kan afvises på præcis ét tal.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen forkastede alternativer, eller de er afvist med "det er ikke bedste praksis" |
| 1 | To alternativer nævnt, afvist på flere akser samtidig eller på en akse uden tal |
| 2 | To navngivne alternativer, hvert afvist på **én** akse med et tal og en enhed (udviklerdage, kroner, kalenderuger, andel af skærme, procentpoint af de 6,2 s) |
| 3 | Ovenstående, plus at mindst ét af de forkastede alternativer er det kandidaten selv startede med, med en note om hvornår og hvorfor han skiftede, plus at mindst ét fravalg er formuleret så det også besvarer Sofies spørgsmål om hun skal fortsætte på sin gren — med et tal for hvad grenen ville have løst af de 6,2 sekunder |

### K10 — Faldsbetingelsen (vægt 3)

*Findes fordi:* et valg uden en betingelse der vender det, er en begrundelse, ikke en beslutning. Og i denne case findes der en betingelse der kan udløses inden for timeboxen.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen faldsbetingelser |
| 1 | 1-2 betingelser i prosa uden tærskel ("hvis det viser sig for dyrt") |
| 2 | Mindst tre betingelser, hver med en tærskel og en enhed (fx "hvis den afgrænsede audit finder over 12 afvigelser uden for komponentlaget", "hvis bot-beskyttelsens leverandør melder over 6 ugers leveringstid", "hvis auditbudgettet falder under 30.000 kr.") |
| 3 | Ovenstående, plus at mindst én betingelse er **knyttet til en dato og en ejer**, plus at mindst én af dem faktisk udløses af præmisskiftet og at kandidaten følger den i stedet for at omfortolke den. En faldsbetingelse der er formuleret så bredt at intet i casen kan udløse den, tæller som 1 |

### K11 — Planen og nej'et en ikke-teknisk læser kan handle på (vægt 3)

*Findes fordi:* Jens sidder over for Helle Bang den 22. september uanset hvad du skriver. Dokumentet der ikke ændrer en beslutning inden for to uger, var dekoration.

| Score | Sådan ser det ud |
|---|---|
| 0 | Notat med jargon (state, hydrering, primitiver, a11y), eller kun én mulighed, eller en plan uden navne |
| 1 | To muligheder uden anbefaling, eller en plan med opgaver men uden timer, eller en plan hvis timesum ikke findes i huset |
| 2 | Præcis 1 side, nul jargon, to muligheder med pris og én klar anbefaling; seksugersplan med navne og timer/uge der summer til kapacitet der faktisk findes, og med mindst én milepæl uden for vores kontrol |
| 3 | Ovenstående, plus at der står én sætning Jens kan sige til Helle Bang den 22., som hverken lyver eller trækker Katrines "ja" tilbage uden varsel; plus at det står hvad der bliver **fortrængt** og hos hvilken kunde; plus at det står hvad vi beder IFM om (testkonto, adgang til Karina, accept af afvigelsesformatet) |

### K12 — Iteration ved præmisskiftet (vægt 3)

*Findes fordi:* det er den ene observerbare adfærd der adskiller en arkitekt fra en dygtig udvikler, og den kan ikke fabrikeres bagefter.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forsvarer det oprindelige scope. Sætningen "mit arbejde er faktisk stadig relevant, hvis man ser det sådan her" optræder i en eller anden form |
| 1 | Erkender at noget skal laves om, men laver alt om — inklusive de dele skiftet ikke rører |
| 2 | Omskriver scope til leverandørsiden og opdaterer mindst to tal inden for 45 minutter, og siger hvad der **ikke** ændrer sig |
| 3 | Ovenstående, plus at valget mellem de tre ting hos Adgang & Co er truffet eksplicit på de 25.000 kr. med en begrundelse i en enhed; plus at feedbackmekanismen er sendt videre som et spørgsmål til Katrine og Mette med en frist, ikke optaget som egen opgave; plus at offentliggørelsen har ændret **ordlyden** i artefakt 4 på en måde der kan peges på, linje for linje |

### Bestået, og hvad "stærk" kræver

- **Bestået: 60 af 99 point**, og ingen af K1, K3, K4 og K12 under 2. En kandidat der scorer højt på performanceanalyse og lavt på K4 har lavet en teknisk rapport til et kontraktproblem.
- **Kompetent: 60-77 point.** Redegørelsen kan sendes, planen kan følges, og en anden udvikler kan arbejde efter grænserne.
- **Stærk: 78+ point**, med 3 på mindst fem kriterier, herunder **K9 og K10**. Stærk kræver desuden to ting der ikke kan spilles: at mindst ét af de fjorten skjulte svar har fået kandidaten til at rive noget op han allerede havde skrevet, og at det er dokumenteret hvad og hvornår.
- **Automatisk dumpet**, uanset pointsum: hvis den afleverede redegørelse erklærer overholdelse af WCAG 2.2 AA uden testgrundlag, eller citerer en dansk lovtitel eller et kriterienummer kandidaten ikke har verificeret. Det er ikke en formfejl. Det er en urigtig oplysning til en offentlig ordregiver, og ingen af de andre kriterier kan opveje den.

## Kalibrering: skriv dette ned FØR du går i gang

Fem forudsigelser. Skriv dem i en fil, gem den, rør den ikke før timeboxen er slut.

1. **Hvor mange af Sofies 148 automatiske fund bliver til reelle, distinkte WCAG 2.2 AA-afvigelser efter en manuel gennemgang?** Skriv ét tal nu, før du har læst ét eneste svar i tabellen over skjulte oplysninger.
2. **Hvor stor en andel af de 6,2 sekunder fjerner Sofies virtualiseringsgren?** Ét procenttal.
3. **Hvor mange af dine kravsspørgsmål bliver besvaret med noget der reelt ændrer det du afleverer?** Et tal mellem 0 og 14.
4. **Hvor mange af de seks timer går til redegørelsens ordlyd — artefakt 4 alene?** Ét tal med én decimal. De fleste skriver 0,5 og bruger 1,8, fordi det er den eneste del hvor hvert ord kan blive læst op i en tvist.
5. **Hvad bliver sværest?** Én sætning, maks. 15 ord.

**Hvad var jeg sikker på og tog fejl om** — udfyldes efter timeboxen, mindst tre linjer, hver af formen "jeg troede X, det var Y, årsagen var Z". Er feltet tomt, er kalibreringen dumpet, ikke perfekt. En kandidat der ikke tog fejl om noget på seks timer i et problem hvor fire af fjorten oplysninger vælter en oplagt løsning, har ikke undersøgt problemet.

## Modelbesvarelsens omrids

**LÆS FØRST EFTER FORSØG.** Ikke et facit. Et omrids af hvad en stærk besvarelse indeholder, og hvilke veje der er forsvarlige.

**Tre forsvarlige veje**

- **A. Lej tilgængelighedslaget, men kun i de skærme der er i scope.** Headless primitives indføres i de komponenter der optræder i bilag 2's tre kernearbejdsgange — modal, kombinationsfelt, tabel, filupload, fejlmeddelelse — og ingen andre steder i vinduet. De 22 køberskærme får en dateret afvigelsesliste i redegørelsen i stedet for en migration. Billigst i kalendertid, og den eneste der kan nå at flytte noget reelt før 1. juni 2027. Falder på ét punkt: den efterlader to komponentregimer i kodebasen, og hvis ingen dato binder det andet regime, har du købt tid med gæld du ikke har prissat.
- **B. Byg leverandørportalens seks skærme om på ét vurderet system.** Aleks' håndrullede komponenter er den del der bliver kontrolleret, den del der har tre fokusmønstre, og den del ingen ejer. Dyrest på forhånd, men det er også det eneste sted hvor en ombygning kan fjerne en hel kategori af afvigelser i stedet for at rette dem enkeltvis. Forsvarlig hvis du kan vise at den kan bygges i etaper og sige hvilken etape der er færdig 1. december, og hvilken der er færdig 1. juni.
- **C. Ingen migration i vinduet.** De 40-60 konkrete spærringer i de tre kernearbejdsgange rettes i hånden, grænserne fryses med håndhævelsespunkter (én kaldsmåde, ét query-cache-lag, en CI-gate på seks flows, en komponentregel), auditkronerne bruges på det ét menneske kan afgøre, og selve eje-eller-leje-beslutningen udskydes til en dateret ADR i første kvartal 2027 med en navngiven ejer. Den ærligste vej hvis kapaciteten er så lille som den er, og den letteste at score lavt på, fordi den kræver at faldsbetingelserne er skarpe nok til at nogen faktisk vender tilbage til beslutningen.

Alle tre er forsvarlige. Den urimelige er kun én: at love fuld overholdelse den 14. oktober, fordi Katrine allerede har lovet den.

**Hvad en stærk besvarelse desuden indeholder**

- Det står i første afsnit at bilag 4 kræver **en redegørelse** den 14. oktober og **afhjulpne kernearbejdsgange** 1. juni 2027, og at de to datoer stiller vidt forskellige krav. Hele resten af dokumentet følger af den skelnen.
- Leverandøroversigten er identificeret som teknisk gæld med en kunde bag den, ikke som salgsblokering — den står ikke i bilag 2 — og det er sagt uden at gøre Fjordhus' problem mindre end det er. Excel-eksporten er noteret som et produktfund: kunden har allerede fortalt os hvor produktet er ufuldstændigt, gratis.
- Login-flowet er behandlet som det det er: en spærring foran alle tre kernearbejdsgange, som ikke kan løses i komponentlaget, som afhænger af en tredjepart med 4-6 ugers leveringstid, og som derfor skal på afvigelseslisten med en dato og en ejer i dag, ikke i oktober.
- De 6,2 sekunder er attribueret, og det står at virtualisering rammer ca. 1,4 s af dem — og at et virtualiseret grid samtidig er en tilgængelighedsrisiko hvis rækkeantal og position ikke annonceres korrekt. At de to spor kolliderer præcis dér, er casens skjulte pointe, og en stærk besvarelse siger det højt.
- Der er sat en pris på Katrines "ja". Ikke moralsk, men praktisk: hvad koster det at lade det stå uimodsagt, hvad koster det at korrigere det, hvem korrigerer det, og hvornår. En stærk besvarelse skriver den sætning Jens kan sige den 22., og den sætning trækker ikke noget tilbage — den tilføjer.
- Manglen på browsertelemetri er skrevet ind i redegørelsen som et vilkår, ikke som en undskyldning, og der står hvad vi gør i stedet: en brugertest med to skærmlæserbrugere er data om produktet, ikke om markedet, og forskellen er noteret.
- Fund undervejs som en der læste systemet ville finde: at Opdater-knappen er cachebruddet gjort til feature, at tre state-mønstre betyder at én fokusrettelse skal laves tre steder, og at hukommelsesvæksten og de "døde" faner sandsynligvis er samme sag.

**Hvad der adskiller den stærke fra den kompetente**

| Den kompetente | Den stærke |
|---|---|
| Læser bilag 4 og refererer det | Ser at de to datoer stiller forskellige krav, og bygger hele planen på forskellen |
| Skriver en afvigelsesliste | Skriver en afvigelsesliste der stadig er sand når den er offentlig i marts 2027 |
| Vælger headless primitives | Vælger dem for navngivne skærme, siger hvad de 22 andre koster, og datosætter det andet regime |
| Måler de 6,2 sekunder | Attribuerer dem og siger hvor stor en del Sofies gren ville have løst, før hun har brugt en uge mere |
| Nævner at automatiske værktøjer ikke fanger alt | Sætter pris og dato på den test kun et menneske kan lave, og siger hvad vi gør indtil da |
| Nævner at Katrine har svaret ja | Skriver den sætning Jens kan sige, og siger hvad der sker hvis han ikke siger den |
| Laver planen om efter præmisskiftet | Siger også hvad der ikke ændrer sig, og bruger de 25.000 kr. med en begrundelse i en enhed |

## Sådan ser en dårlig besvarelse ud

Skrevet som du selv ville formulere det. Formålet er genkendelse, ikke skam.

1. *"Vi skifter til headless primitives, så er tilgængeligheden løst."* — Login-flowet, bot-beskyttelsen og datagriddet ligger alle uden for komponentlaget, og de spærrer alle tre kernearbejdsgange. Du har løst den del af problemet der var lettest at få øje på, og skrevet under på resten.
2. *"Lighthouse siger 94, så vi mangler vist ikke ret meget."* — Rapporten er kørt på marketingsitets loginside. Det du har målt, er ikke det du sælger, og tallet ligger allerede vedhæftet et tilbud du ikke selv skrev.
3. *"Vi virtualiserer tabellen, så er performance på plads."* — Det rammer ca. 1,4 af 6,2 sekunder. De fire sekventielle kald og serverens 2,84 s står stadig, filterfeltet henter stadig forfra ved hvert tastetryk, og et virtualiseret grid uden korrekt annoncering af rækkeantal gør tilgængeligheden dårligere end den var.
4. *"Vi skriver at vi overholder WCAG 2.2 AA, og retter det vi finder undervejs."* — Det er den ene fejl i casen der ikke kan opvejes af noget andet. Dorthe har selv sagt at en redegørelse uden afvigelser ikke er troværdig, og fra januar 2027 læser et tilsyn med.
5. *"Tilgængelighedsloven kræver jo..."* — Du citerer en lovtitel du ikke har slået op, i et dokument en udbudsjurist læser. Den der ikke tjekker før han udtaler sig, er farligere end den der intet ved, og her står det på skrift med en underskrift under.
6. *"Vi laver et design system, så konvergerer de tre state-mønstre også."* — Design systems fejler organisatorisk, du har syv årsværk og seks uger, og du har lige gjort en kontraktforpligtelse afhængig af et internt projekt ingen har bedt om.
7. *"Jeg foreslår en frontend-oprydning i fjerde kvartal."* — Uden kroner, uden dato og uden en kunde bag er det ordet refaktorering med en anden overskrift. Jens læser det som "udvikleren vil rydde op", og han har lige skåret i Azure-regningen.
8. *"Vi beder bare IFM om at udskyde fristen."* — Fristen står i en underskrevet kontrakt med en offentlig ordregiver, og de tre andre organisationer i pipelinen har spurgt til den samme rammeaftale. Det er ikke et design, det er et ønske sendt videre.
9. *"Præmissen ændrede sig, men egentlig havde jeg jo taget højde for det."* — Det er forsvar. Det er også præcis den sætning en interviewer lytter efter, og den eneste der ikke kan bortforklares bagefter.

## Hvor i materialet svaret står

Ubarmhjertig version. To kriterier er ikke dækket af noget modul, og det er et fund i materialet, ikke i casen.

| Kriterium | Modul | Præcis sektionsoverskrift | Hvad du henter der |
|---|---|---|---|
| **K1** Kravsspørgsmål før første biblioteksnavn | 01 | `### Øvelse 3: Trade-off-kata på tid` | Kravet om mindst otte kravsspørgsmål stillet før første diagram, den hårde timebox, og selvkontrollen til sidst: "besvarede du dit eget design uden at have svar på halvdelen, er det fundet". Suppl.: 01 `## Sådan ved du at du kan det`, første punkt, om otte kravsspørgsmål før du nævner en teknologi |
| **K2** Spørgsmålene rammer de dyre akser | 10 | `## Kvalitetsattribut-scenarier: din del af kravarbejdet` | Den seksdelte form (kilde, stimulus, artefakt, miljø, respons, responsmål) og reglen om at responsmålet altid er et tal. Suppl.: 01 `## Kompetencemodellen: ti akser`, rækken "Kravsfremdragelse og NFR med tal" — forskellen på at gætte tal og at kende usikkerheden |
| **K3** Salgsblokering skilt fra teknisk gæld | 05 | `## Tilgængelighed er en salgsblokering før den er en lovblokering` | At argumentere indkøb og tabt omsætning frem for paragraffer, og at offentlige kunder **skal** indkøbe efter EN 301 549. Suppl.: 10 `## Teknisk gæld vindes med to tal, aldrig med ordet "refaktorering"` for at argumentere mod variansen og for hotspot-tankegangen; og 05 `## Performance: dine egne tal, ikke Googles` for koblingen mellem performance og afbrudt leverandør-onboarding |
| **K4** Redegørelsens ordlyd | — | **IKKE DÆKKET** | Materialet giver trelagsmodellen EAA → EN 301 549 → WCAG 2.2 AA og advarslen mod at nævne en dansk lovtitel du ikke har slået op (05 `## Tilgængelighed er en salgsblokering før den er en lovblokering`), og kravet om at kunne svare på et tilgængelighedsspørgsmål fra et indkøbsspørgeskema uden at slå op (05 `## Sådan ved du at du kan det`). Der mangler **selve dokumentet**: hvad en tilgængelighedsredegørelse eller en ACR indeholder, forskellen på fuld og delvis overholdelse som erklæring, hvordan en afvigelse skrives så den holder i en tvist, hvem der skriver under, hvad et ubetinget "ja" i et tilbud juridisk gør ved en senere redegørelse, og hvad et offentligt tilsyn faktisk kontrollerer. Det er casens tungeste kriterium og materialets største hul på dette emne |
| **K5** Egne målte tal med spænd | 05 | `## Performance: dine egne tal, ikke Googles` | At CrUX kun indeholder offentligt tilgængelige sider, at LCP næsten intet betyder bag login, at INP-*konceptet* betyder alt, at budgetter udledes af brugerkendsgerninger (tid pr. tastetryk i en tabel med 5.000 rækker), og hukommelsesvækst over en 8-timers session uden reload. Suppl.: 02 `## Rækkefølgen der afgør alt: måling først, ikke sidst`, og 05 `## Faldgruber` punkt 5 om at citere Core Web Vitals for en app bag login |
| **K6** Hvad målingen ikke fanger | — | **IKKE DÆKKET** | Materialet har WCAG 2.2 Quick Reference filtreret til AA og Deque om EN 301 549 (05 `## Ressourcer`) samt advarslen mod at bygge governance oven på Lighthouse CI (samme tabel, rækken om Lighthouse CI, 0.x). Der mangler **testmetodens dækningsgrad**: at automatiserede værktøjer kun afgør en mindre del af kriterierne, hvilke kriterier der principielt kun kan afgøres manuelt, hvad en test med rigtige hjælpemiddelbrugere koster og giver, hvordan man vælger repræsentative flows i stedet for skærme, og hvordan man håndterer at de kriterier der er nye i WCAG 2.2 ikke findes i nogen ældre checkliste eller regelsæt. Uden det bliver værktøjets output til afhjælpningsplanen, og det er den fejl casen straffer hårdest |
| **K7** Eje eller leje tilgængelighedslaget | 05 | `## Tilgængelighed er en salgsblokering før den er en lovblokering` | Tabellen med de tre optioner (egne UI-primitiver, headless primitives, fuldt system), kolonnen "Realistisk for syv årsværk", og reglen: prissæt i **vedligeholdelsestimer over tre år**, ikke implementeringstimer. Suppl.: 05 `## Faldgruber` punkt 3 om ikke at bygge et design system som spike; og 10 `## Prioriteringsrammer løser et problem I ikke har` for kapacitetsregnskabet — hvad en indsats koster som andel af årets kapacitet |
| **K8** Grænserne der stopper rådnen | 05 | `## Frontend rådner af manglende grænser, ikke af dårlig kode` | Tabellen over de fem rådnemekanismer med "håndhæves ét sted", diagnosespørgsmålet om hvor mange kilder til sandhed et datum har, og Opdater-knappen som indrømmelse af brudt cache. Suppl.: 05 `## Kontrakten mellem .NET og React` for kontraktgrænsen og de fire kaldsmåder; og 05 `## Spikes med fysisk output`, spike F1, for CI-gaten der fejler builden og for kravet om en dokumenteret nødudgang med ADR-reference |
| **K9** Fravalg på én målbar akse | 05 | `## De tre nej'er du skal skrive ned` | Tabellen med mønster, hvorfor nej her, og betingelsen der vender svaret — inklusive de organisatoriske begrundelser (Node-runtime ved siden af .NET, PR-kø-tid, flere kilder til sandhed). Suppl.: 07 `### G5 — ADR-serie om lejerisolation i dokumentlageret (måned 3-4, 1 uge, parallelt)` for kravet om navngivne afviste alternativer i ADR-form; og 05 `## Faldgruber` punkt 7: ADR'er uden tal er meninger med overskrift |
| **K10** Faldsbetingelsen | 05 | `## De tre nej'er du skal skrive ned` | Kolonnen "Betingelsen der vender svaret", med tærskler der kan måles (målt PR-kø-tid, en offentlig indholdstung del der bliver forretningskritisk, data der reelt er client-state). Suppl.: 09 `## Sådan ved du at du kan det`, rækken "ADR-tællingen": mangler afsnittet om hvad der ville ændre beslutningen, er det en begrundelse og ikke en beslutning; og 05 `## Sådan ved du at du kan det`, punktet om skriftligt at have afvist et populært mønster og navngivet betingelsen der vender svaret |
| **K11** Planen og nej'et til en ikke-teknisk læser | 11 | `## Oversæt til kroner og risiko` | De fire enheder (kroner pr. måned, manuelle timer pr. måned, sandsynlighed for at tabe en handel, sandsynlighed for at fejle en kundes audit), forbuddet mod ordene teknisk gæld og kvalitet over for stifteren, kravet om to-tre muligheder med en klar anbefaling, og énsidesformen "Vi har X i dag. Problemet er Y...". Suppl.: 10 `## Shape Up, og aldrig et nej uden prisskilt` for tredelingen "det koster X" / "80 procent for Y" / "tillad genvejen og datosæt hvornår den bliver dyr"; og 11 `## Fem formater, og hvornår hvert bruges` for valget mellem ADR, design doc og narrativ |
| **K12** Iteration ved præmisskift | 01 | `## Sådan ved du at du kan det` | Andet punkt: "Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse." Suppl.: 01 `### Øvelse 3: Trade-off-kata på tid`, afsnittet om at en ekstern person ændrer en præmis efter fire timer og måler om du itererer eller forsvarer; og 11 `## Uenighed skrives, den tales ikke` for "tab pænt, skriftligt" — at skrive opdateringen selv når du tog fejl |

## Ekstern kalibrering

Din egen score er værdiløs alene, og en kollega i et ni-mandsfirma tæller halvt — særligt her, hvor Thomas allerede har sagt hvad han mener om MUI, og hvor Sofie har en gren hun har brugt tre uger på. Mindst to af disse skal have givet **skriftlig** kritik, før casen tælles som gennemført. Spørg hver om én ting, ikke om en helhedsvurdering.

| Hvem | Hvor du finder dem | Det konkrete spørgsmål |
|---|---|---|
| Tilgængelighedsauditor fra et dansk hus | De virksomheder der sælger WCAG-audits til offentlige ordregivere; ring og bed om 30 minutter mod at de må bruge samtalen som salgsmøde | "Her er min afvigelsesliste for tre arbejdsgange. Hvor mange afvigelser tror du I ville finde som ikke står på den, og hvilken type ville de være?" |
| En skærmlæserbruger med erfaring fra arbejdsmarkedet | Gennem handicaporganisationernes it-netværk eller et tilgængelighedsnetværk i branchen; betal for timen | "Her er tre trin i vores leverandør-onboarding. Hvor giver du op, og hvad ville du have gjort i stedet?" Dette er det spørgsmål ingen af de andre kan svare på |
| Udbudsjurist eller kontraktansvarlig hos en offentlig indkøbsorganisation | Gennem en eksisterende offentlig kunde, eller via netværk i indkøbsmiljøet | "Vores sælger har svaret ubetinget ja i tilbuddet, og redegørelsen bliver delvis. Hvordan læser I det, og hvad ville I helst have haft os til at gøre?" |
| Frontend-arkitekt fra et større dansk produkthus | ANUG eller GOTO-meetup i Aarhus; bed om 30 minutter efter oplægget | "Læs mine fem grænser og deres håndhævelsespunkter. Hvilken af dem holder ikke, når teamet får travlt i november?" |
| Betalt design-review-mentor | Den faste mentorordning fra modul 10, 1-2 t/md. | "Angrib min seksugersplan, ikke min analyse. Hvilket af mine fire tal er mest forkert, og hvad ville du selv have skåret væk?" |
| Code review-byttepartneren | Den udvikler i et andet firma du har fast kadence med fra måned 3 | "Læs mine to fravalg. Kan du argumentere mig ned på ét af dem — på den akse jeg selv valgte?" |

Notér for hver: hvad de sagde, hvad du ændrede, og hvad du valgte at lade stå — plus hvorfor. Den tredje kolonne er den, en kommende arbejdsgiver spørger ind til.
