# C06 — Observability fra nul

| | |
|---|---|
| **Type** | Måleapparat og SLI-design |
| **Primært modul** | 06 — Observability: at kunne se hvad systemet faktisk gør |
| **Sekundære moduler** | 02 (Teknisk fundament) · 03 (Azure-arkitektur) · 08 (Compliance og risiko) |
| **Timebox** | 8 timer, hård. Præmisskiftet lægges oveni og må koste maks. 45 minutter ekstra |
| **Sværhedsgrad** | 4 af 5. Let på værktøj, hård på at vælge fra og på at sige hvad du **ikke** kan svare på. Giver mening i **måned 5-8**: før måned 5 har du hverken målte MB pr. 1.000 requests fra O-1/O-2 eller egne `_BilledSize`-tal, og så bliver både SLI'erne og kroneposten citater fra blogs. Efter måned 9 er den for nem, fordi O-3 og O-5 har foræret dig svarene. Kør den igen i måned 11 med samme rubrik og sammenlign |
| **Afleveringsformat** | Ti artefakter: spørgsmålsliste (1 side, tidsstemplet), telemetri-datakort (ét diagram + 0,5 side), SLI-katalog (2 sider), SLO og error budget (1 side), alarmkatalog (1 side, tabel), byte-budget og omkostningsmodel (regneark + 0,5 side), tabsliste (0,5 side), telemetri-datapolitik (præcis 1 side), brev til kundens sikkerhedschef + notat til stifteren (hver præcis 1 side, ikke-teknisk), ADR (maks. 1,5 side, MADR-minimal) plus selvvurdering (0,5 side). I alt maks. 9 sider brødtekst, ét regneark, ét diagram |

> Personerne er de samme opdigtede som i C01 og C03: Jens (stifter), Katrine (salg), Thomas (har bygget det meste), Rasmus (drift og produktionsadgang), Lone (bogholderi). Kunden Fjordhus og dens medarbejdere er opdigtede. **Kronebeløbene i denne case er konstrueret til denne case alene og skal ikke stemme med C03's tal** — casen er en selvstændig øvelse, ikke en fortsættelse. Azures listepriser er ikke oplyst; dem henter du selv via Retail Prices API, og gætter du, mærker du gættet som gæt i regnearket.

## Situationen

Mandag den 14. september 2026, kl. 08.05.

Mette Sandholt er kvalitetschef hos Fjordhus Retail Group A/S — 340 byggemarkeder i Danmark, Sverige og Norge, husets største kunde siden go-live den 2. juni. Fredag eftermiddag skrev hun til Katrine: enogfyrre af deres leverandører har ikke fået 30-dages påmindelsen om udløbende certifikater. To af dem står nu med et udløbet ISO 9001 midt i et surveillance audit-forløb, og en tredje har fået en major nonconformity som Fjordhus skal forklare deres egen kunde. Mettes spørgsmål fylder én linje: *"Kørte jeres natkørsel natten til torsdag den 10.?"*

Rasmus svarede lørdag: "Der er ingen fejl i loggen." Mette har ikke svaret tilbage.

Natkørslen er en Azure Function der starter 02.15. Den henter leverandørdelta fra kundernes ERP — Fjordhus lægger en IDoc-eksport på SFTP, to andre kunder kalder I via API — genberegner certifikatstatus og sender påmindelser til leverandørernes kontaktpersoner ved 90, 60 og 30 dage. Den rapporterer Success. Den rapporterede også Success natten til torsdag.

Jens ringede til Mette den 2. september og lovede noget der nu står i en opfølgende mail: fra 1. oktober får Fjordhus en månedlig driftsrapport med oppetid, svartider og status på natkørslen. Han har ikke sagt hvilke tal der skal stå i den. Katrine har siden fortalt to potentielle kunder at "vi rapporterer månedligt på oppetid".

Der er en anden ting. Den 4. september bad Fjordhus' informationssikkerhedschef Poul Ebbesen om dokumentation for hvordan fejl håndteres, og Katrine sendte et skærmbillede fra Application Insights som eksempel på at der bliver kigget. På billedet står en URL med `?email=b.kowalska%40...&contactName=Birgitte%20Kowalska`, og under den en exception-tekst med samme persons telefonnummer i klartekst. Poul har svaret skriftligt med ét spørgsmål: *"Indeholder jeres driftslogning personoplysninger? Bilag 3 til databehandleraftalen siger nej."* Fjordhus' årlige databehandleraudit ligger torsdag den 8. oktober kl. 10.00-14.00, remote, med deres eksterne revisor på.

I har Application Insights på alt. I har 14 alarmer. Elleve af dem fyrer hver uge til `drift@leanlinking.dk`, og ingen åbner dem længere — Thomas lavede en Outlook-regel i maj. Ingen har defineret en SLI. Availability-fanen viser **99,97 %** for august, og det er det tal Katrine skriver i kundespørgeskemaer. Log Analytics og Application Insights kostede i august **14.850 kr.** af en Azure-regning på 61.340 ekskl. moms — næststørste post efter Azure SQL, og den er vokset hver måned siden maj.

Jens' besked i morges var kort: "Fiks alarmerne, og find ud af hvad der skete natten til torsdag. Du har tre udviklerdage før den 8., og de skal ikke tages fra Fjordhus-integrationen. Og vi skal ikke ind i noget der koster mere om måneden end det gør nu."

Du har otte timer til at beslutte hvad der skal måles. Rasmus er 60 % booket til den 15. oktober. Thomas har en dag om ugen og rører nødigt infrastruktur. Der findes ikke en kopi af produktionsdata du kan arbejde på, og du har i dag læseadgang til portalen, ikke andet.

## Det du skal aflevere

| # | Artefakt | Format | Krav der ikke kan forhandles |
|---|---|---|---|
| 1 | **Spørgsmålsliste** | 1 side, tidsstemplet | Skrevet **før** du vælger det første signal. Hver linje: spørgsmålet, hvem det stilles til, og hvad svaret ville ændre i designet |
| 2 | **Telemetri-datakort** | Ét diagram + 0,5 side | Vejen fra et klik i leverandørportalen **og** fra natkørslens start til en gemt række i Log Analytics. Markér hvor context propageres, hvor den tabes, hvor sampling besluttes, hvor der bruges penge, og hvert sted personoplysninger kan slippe med |
| 3 | **SLI-katalog** | 2 sider | 3-5 SLI'er. Hver skrevet i én sætning **i ord** før den er skrevet i KQL, derefter tæller, nævner, målepunkt, vindue, mindst én eksklusion, og feltet "kan måles i dag: ja / nej / delvist — og hvad der mangler" |
| 4 | **SLO og error budget** | 1 side | Mål pr. SLI med begrundelse for tallet. For mindst én SLI regnes error budget **både** request-based og window-based, og de to tal skal være forskellige og forklarede. Plus: hvad der sker ved brud, og hvem der beslutter det |
| 5 | **Alarmkatalog** | 1 side, tabel | Alle 14 eksisterende alarmer med behold / omskriv / slet og begrundelse. For hver overlevende: hvem vågner, hvad gør de, og hvad sker der hvis ingen reagerer i to timer. Mindst én sletning og mindst én alarm du **nægter** at bygge |
| 6 | **Byte-budget og omkostningsmodel** | Regneark + 0,5 side | MB pr. 1.000 requests og MB pr. natkørsel, før og efter dit forslag. Kr./md. for måleapparatet ved nuværende volumen og ved den volumen præmisskiftet giver. **Usikkerheden angives i procentpoint**, ikke som forbehold i prosa |
| 7 | **Tabslisten** | 0,5 side | De spørgsmål du **ikke længere kan besvare** efter dit forslag. Mindst fem, hver med hvem der ville stille det og i hvilken situation |
| 8 | **Telemetri-datapolitik** | Præcis 1 side | Hvilke felter må logges, hvilke aldrig, hvem har læseadgang, hvor længe, og hvad der sker ved en sletteanmodning når der samtidig ligger et legal hold |
| 9 | **Brev til Poul Ebbesen + notat til Jens** | Hver præcis 1 side, ikke-teknisk | Brevet skal svare sandt på Pouls spørgsmål, sige hvad der rettes hvor, og hvad der ikke kan rettes bagud. Notatet skal indeholde: hvad der kan siges om natten til den 10., hvad den månedlige rapport kommer til at indeholde, hvad det koster, og hvad Jens har lovet som du ikke kan levere |
| 10 | **ADR + selvvurdering** | Maks. 1,5 side MADR-minimal + 0,5 side | Mindst to navngivne afviste alternativer, hvert afvist på **én målbar akse med et tal**. Afsnittet "Dette ville få os til at vælge om" med mindst tre betingelser, hver med tærskel og enhed. Selvvurderingen: hvilke tal er målte, hvilke hentede, hvilke gættede |

**Artefakt 6 og 7** er dem der bærer tal med angivet usikkerhed. **Artefakt 9** er det ikke-tekniske, og de to eneste dokumenter der forlader huset. **Mindst én af dine 3-5 SLI'er skal handle om arbejde udført** — påmindelser sendt, dokumenter valideret, rækker indlæst — og ikke kun om svartid. Et SLI-katalog der udelukkende måler latens på HTTP-endpoints er ikke et katalog over hvad kunden mærker; det er et katalog over hvad der var let at måle.

## Skjulte oplysninger

Du må kun læse svaret på et spørgsmål du **faktisk har skrevet ned** før du begyndte at designe. Læser du hele tabellen først, har du ikke lavet casen — du har læst en løsning, og du kan ikke score over 1 på K1 og K2.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Hvad ville Fjordhus' kvalitetsafdeling opdage først, hvis noget holdt op med at virke? | Mette svarer på ti minutter, og ingen har spurgt før. Tre ting, i den rækkefølge hun siger dem: (1) at påmindelsen om et udløbende certifikat ikke kommer — *"vi opdager det når leverandøren står med et udløbet papir i en surveillance audit, og så er det tre uger for sent"*; (2) at afvisningslisten fra natkørslen ikke ligger i indbakken kl. 06.30 på en hverdag; (3) at en leverandørs dokument-upload fejler uden at leverandøren får besked, så leverandøren ringer til **Fjordhus** i stedet. Ingen af de tre er den login-tid eller den side-svartid nogen i huset ville have målt først |
| 2 | Hvad viser de 14 alarmer i dag, og hvem modtager dem? | Alle 14 går til `drift@leanlinking.dk` (Rasmus, Thomas og `info@`). **Elleve fyrer ugentligt:** 4× CPU > 80 % på tre app service plans, 2× "Failed requests > 0" (fyrer på hver 401 fra leverandørportalen), 1× "Availability test failed" (fyrer når den syntetiske test rammer deployvinduet), 2× "SQL DTU > 90 %" (fyrer under scorecard-genberegningen, som er forventet), 1× "Exception count > 10 på 5 min" (fyrer når en ERP-fil er malformet, hvilket sker ugentligt og håndteres i hånden), 1× "Daily cap 80 % nået" (fyrer siden 3. august). **Tre fyrer aldrig** — og det er ikke fordi alt er godt: "Service Bus dead letter > 0" har været brudt siden februar fordi køen blev omdøbt; "Key Vault certifikat udløber" peger på en slettet vault; "Function app failures" står på en metric som natkørslen aldrig sætter, fordi den rapporterer Success |
| 3 | Er nogen af alarmerne nævnt i en kundeaftale eller et spørgeskema? | Ja. Katrines besvarelse af Fjordhus' sikkerhedsspørgeskema, vedhæftet kontrakten som bilag 6, punkt 5.3, sendt 2. juli: *"Automated alerting is configured for integration failures and for authentication anomalies; alerts are monitored during business hours (08:00-16:00 CET)."* Bemærk hvad der ikke står: intet om nætter, intet om responstid. Bemærk også at alarmen på integrationsfejl er en af de tre der er brudt |
| 4 | Kørte natkørslen natten til torsdag den 10., og hvad lavede den? | **Det ved vi ikke med sikkerhed.** Funktionen rapporterer Success kl. 02.41. Den behandler leverandører i et `foreach` med try/catch der kalder `LogWarning` og fortsætter. Der findes **ingen tælling** af behandlede, sprunget over eller notificerede rækker noget sted. Mailen sendes via SendGrid, hvis aktivitetsfeed kun gemmer 30 dage; den viser 1.184 sendte mails den nat mod typisk 1.400-1.600. Ingen ved hvad det korrekte tal burde have været. Det kan ikke rekonstrueres til revisorstandard for netop den nat. Det kan gøres målbart fremad |
| 5 | Hvad ligger bag availability-tallet på 99,97 %? | Én URL-ping mod `/health` fra West Europe hvert 5. minut. `/health` returnerer 200 så længe processen svarer; den rører hverken Azure SQL, Blob, Service Bus eller SendGrid. Den 1. september var databasen utilgængelig i 22 minutter, og availability-testen forblev grøn hele vejen igennem. Tallet står i tre besvarede kundespørgeskemaer |
| 6 | Hvad koster telemetrien, og hvad består den af? | Augustregningen: Azure SQL 19.700, **Log Analytics + App Insights 14.850**, App Service Plans 9.400, Blob + transaktioner 5.200, backup 3.900, Service Bus + Functions 2.600, egress 2.100, øvrigt 3.590. I alt 61.340 kr. ekskl. moms. Faktureret ingest i august: **812 GB**. Fordeling: `AppTraces` 58 %, `AppDependencies` 21 %, `AppRequests` 11 %, `AppExceptions` 5 %, resten 5 %. Retention er 90 dage, sat på hele workspacet, ikke pr. tabel |
| 7 | Er sampling slået til, og hvor meget beholdes? | **Det ved vi ikke.** Ingen har kørt verifikationsqueryen. Ingen kan svare på om distroen sampler som default i den version I kører, og der står intet om det i nogen ADR — der findes ingen ADR. Du kan få Monitoring Reader samme dag hvis du beder Jens om det; det er et lille ja at give |
| 8 | Hvor kommer personoplysninger ind i telemetrien, og hvem kan læse dem? | Tre veje fundet på tyve minutters grep: (a) leverandørportalen kalder `GET /api/suppliers/contacts?email=…&name=…`, så query-strengen lander i `AppRequests.Url`; (b) IDoc-parserens `FormatException` indeholder den fældende feltværdi, som ofte er et kontaktpersonnavn eller telefonnummer; (c) natkørslen logger `LogInformation("Sender påmindelse til {Recipient}", contact.Email)` — message template, så e-mailen ender som struktureret property. Der er ikke søgt systematisk, så antallet af veje er et **minimum**, ikke et tal. Adgang: alle fem udviklere plus Katrine har Contributor på abonnementet fordi det var nemmest, to supportmedarbejdere har fået portaladgang for selv at kunne slå fejl op, og adgangen for to medarbejdere der stoppede i 2025 er aldrig fjernet |
| 9 | Hvad står der i databehandleraftalen om telemetri? | Bilag 3, "Kategorier af personoplysninger", nævner *"navn, e-mail og telefonnummer på leverandørers kontaktpersoner samt brugere hos kunden"* — så data**typen** er dækket. Men samme bilag slutter med en sætning Katrine skrev i 2024: *"Personoplysninger behandles alene i produktionsdatabasen og i dokumentarkivet."* Den sætning er usand, og den er underskrevet. Bilag 2 lister Microsoft Azure (West Europe) og **Twilio SendGrid (USA)** som underdatabehandlere, tilføjet under SCC'er i 2023 og aldrig genbesøgt siden |
| 10 | Er der legal hold på noget lige nu? | Ja. Fjordhus har en claims-sag mod en polsk emballageleverandør, og deres advokat bad den 21. august skriftligt om at alt materiale vedrørende den leverandør bevares indtil sagen er afsluttet. Der findes ingen legal hold-mekanisme i produktet. Anmodningen er en mail i Rasmus' indbakke, og ingen har afgrænset hvilke data den omfatter. **Mindst to af de kontaktpersoner hvis navne optræder i telemetrien, hører til netop den leverandør** |
| 11 | Hvad siger Fjordhus-kontrakten om oppetid og hændelser? | 99,5 % månedlig oppetid på webapplikationen. Servicekredit på 4 % af månedsbetalingen pr. påbegyndt 0,5 procentpoint derunder, maks. 25 %. Notifikation om drifts- og sikkerhedshændelser inden for 24 timer efter **opdagelse**. Der findes ingen definition af "oppetid" i kontrakten, ingen ekstern måling, og ingen aftale om hvem der måler. Fjordhus betaler 32.778 kr./md |
| 12 | Hvor mange udviklerdage kan jeg få, og af hvem? | Jens siger maks. tre dage før den 8. oktober, og de må ikke tages fra Fjordhus-integrationen. Rasmus er 60 % booket til 15. oktober, Thomas har én dag om ugen og rører nødigt infrastruktur. Fuldt belastet kostpris pr. udviklerdag: **3.100 kr.** Dine egne otte timer tæller ikke med i de tre dage |
| 13 | Hvad kan vi ikke måle i dag, uanset hvor gerne vi vil? | `tenant_id` blev fjernet som metric-dimension i februar efter at en metric lydløst løb over kardinalitetsgrænsen og tallene holdt op med at passe. Ingen skrev det ned. Attributten findes stadig på spans — men spans kan være samplede (se punkt 7). Konsekvens: fejlrate pr. tenant kan **ikke** hentes fra metrics overhovedet, og fra traces er den et `itemCount`-vægtet estimat hvis fejlmargin ingen har regnet på |
| 14 | Er der en daily cap, og er den nogensinde ramt? | Ja. 3 GB/dag blev sat på workspacet den 3. august efter en regning ingen kunne forklare. Nulstillingstidspunktet står på 06.00 UTC. Cap'en er ramt **6 af de sidste 30 dage**, spredt fra sidst på eftermiddagen til hen på aftenen. Ingen har bemærket det, fordi alarmen på 80 % er en af de elleve der fyrer ugentligt og ignoreres. På de dage mangler telemetrien fra cap'en rammes til nulstillingen — og for et job der kører 02.15 betyder det den **foregående** eftermiddags cap |

## Præmisskiftet

**Åbnes først når 4 timer og 48 minutter af timeboxen er gået (60 %). Ikke før. Sæt en timer.**

Onsdag den 16. september kl. 07.40 sender Rasmus tre linjer i Teams.

1. **Auditten er rykket frem.** Fjordhus' revisor kan ikke den 8. Databehandlerauditten ligger nu **fredag den 25. september kl. 09.00**, og de vil have telemetri-datakortet og et opdateret bilag 3 som pre-read **onsdag den 23. kl. 12.00**. Der er tretten dage færre, og ingen af dem er en hel faktureringsmåned.
2. **En antagelse er forkert.** Rasmus fik Monitoring Reader og kørte verifikationsqueryen. Beholdt andel over de sidste 30 dage: `AppTraces` **23 %**, `AppDependencies` **31 %**, `AppRequests` 100 %, `AppExceptions` 100 %, metrics 100 %. Adaptive sampling har været slået til siden distroen blev sat op i marts, og ingen besluttede det. To af de alarmer du regnede med at beholde, står på `AppTraces`. Og daily cap'en blev ramt **kl. 22.40 den 9. september** — cap-dagen nulstilles 06.00 UTC, så der er hul i telemetrien fra 22.40 til 06.00, hvilket dækker hele natkørslen den 10.
3. **Volumen er på vej op.** Katrine underskrev fredag en hensigtserklæring med Fjordhus Sverige AB: 2.900 leverandører, planlagt go-live 1. februar 2027, forventet **+140 % dokumentvolumen og +90 % natkørselsarbejde**. Jens skriver: *"Måleapparatet må ikke koste mere end det gør i dag, når begge kører."*

**Hvad skiftet er en test af**

- Om du **regner om** frem for at forklare at designet stadig holder. Et opdateret SLI-katalog, et opdateret alarmkatalog og et opdateret kronetal inden for 45 minutter er beviset. En velformuleret redegørelse er det ikke.
- Om du siger højt hvilke af dine **allerede skrevne påstande der nu er usande**. Skrev du i notatet at natkørslen kan bekræftes fra loggen, er den sætning død, og den skal trækkes tilbage med navn og dato — ikke blødes op.
- Om linje 2 flytter din SLI-arkitektur fra logs til metrics, eller om du forsøger at redde de log-baserede alarmer med et argument. Det er hele modul 06's samplingafsnit stillet som en regning der skal betales.
- Om linje 3 ændrer **hvad du tilbyder**, ikke bare hvad du bygger. Et loft på nuværende kroner ved 2,4 gange volumen er et krav om bytes pr. arbejdsenhed, og det er et andet dokument end en spareplan.
- Om din egen faldsbetingelse fra ADR'en faktisk **udløses** af linje 2 — og om du så følger den, eller finder en grund til at lade være. Det er casens skarpeste enkeltmålepunkt.

## Rubrik

Tolv kriterier, hvert scoret 0-3, med vægt. Maksimum er **102 point**. Ankrene er tællelige med vilje: en bedømmer skal kunne sætte scoren uden at kende kandidaten og uden at bruge ordet "god".

| # | Kriterium | Vægt | Maks. |
|---|---|---|---|
| K1 | Spørgsmål før første signal vælges | 3 | 9 |
| K2 | Spørgsmålene rammer det kunden mærker og det ingen har målt | 2 | 6 |
| K3 | SLI'erne: i ord før i KQL, og de matcher en kundeoplevet hændelse | 3 | 9 |
| K4 | Signalvalg og kardinalitet: metric, span, log — og hvad der aldrig sendes | 3 | 9 |
| K5 | Telemetri som løfte og bevis: natkørslen og afstanden til kontraktens tal | 3 | 9 |
| K6 | Alarmkataloget: to-timers-testen, burn-rate og sletningen | 3 | 9 |
| K7 | Persondata i telemetri: lagene, rækkefølgen og det der ikke kan rulles tilbage | 3 | 9 |
| K8 | Måleapparatets pris i kroner, med spænd | 2 | 6 |
| K9 | Samplingens pris i diagnostisk evne | 3 | 9 |
| K10 | Fravalgene, afvist på en målbar akse | 3 | 9 |
| K11 | Faldsbetingelsen | 3 | 9 |
| K12 | Iteration ved præmisskiftet | 3 | 9 |
| | **I alt** | **34** | **102** |

### K1 — Spørgsmål før første signal vælges (vægt 3)

*Findes fordi:* et måleapparat bygget uden at spørge måler det der var let at instrumentere. Den fejl er usynlig i tre måneder og koster derefter en ombygning.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen liste, eller skrevet bagefter. Første konkrete signalvalg ("vi måler p95 på `/api/documents`") inden for de første 20 minutter |
| 1 | 3-6 spørgsmål, ikke tidsstemplede, og mindst ét er et forslag i spørgeform ("skal vi ikke slå sampling til?") |
| 2 | 8-11 tidsstemplede spørgsmål skrevet før første signalvalg, ingen løsninger forklædt som spørgsmål, mindst fem rammer skjulte oplysninger, og mindst ét er stillet til en person uden for udvikling |
| 3 | 12+ tidsstemplede spørgsmål, mindst otte rammer skjulte oplysninger, mindst tre er stillet uden for udvikling (Mette, Poul, Katrine, Lone), hver linje har en note om hvad svaret ville ændre i signalvalget, og listen gennemgås til sidst med markering af hvilke der **stadig** er ubesvarede i det afleverede SLI-katalog |

### K2 — Spørgsmålene rammer det kunden mærker og det ingen har målt (vægt 2)

*Findes fordi:* femten spørgsmål om Application Insights er ét spørgsmål. De fem bærende usikkerheder er: hvad kunden opdager først; hvad natkørslen faktisk gjorde; om måleapparatet allerede er samplet eller cappet; hvad der allerede er lovet skriftligt; og hvad der ikke kan måles med den instrumentering der findes.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen af de fem, eller udelukkende værktøjsspørgsmål |
| 1 | 1-2 af de fem |
| 2 | 4 af de fem, og mindst ét spørgsmål indeholder selv et tal ("hvor mange påmindelser burde der være sendt natten til torsdag?") |
| 3 | Alle fem, plus mindst ét spørgsmål der ville afdække en **modsigelse mellem to ting huset selv har skrevet** — fx mellem bilag 3's sætning om hvor personoplysninger behandles og det skærmbillede Katrine selv sendte, eller mellem bilag 6 punkt 5.3 og de tre alarmer der er brudt |

### K3 — SLI'erne: i ord før i KQL (vægt 3)

*Findes fordi:* en SLI der er skrevet i KQL først, er en beskrivelse af hvad instrumenteringen tilfældigvis kan. En SLI skrevet i ord først afslører at den ikke kan måles endnu — og det er pointen.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen SLI, eller kun "oppetid" og "svartid" uden definition. Eller: signalerne er valgt efter hvad der er let at hente |
| 1 | 3-5 SLI'er nævnt, men mindst én er en ressourcemetrik (CPU, DTU, kølængde) forklædt som SLI, og ingen har eksplicit nævner |
| 2 | 3-5 SLI'er, hver skrevet i én sætning i ord før den skrives i KQL, hver med tæller, nævner, målepunkt (server, klient, syntetisk), vindue og mindst én eksplicit eksklusion. Mindst to svarer til noget kunden selv har nævnt |
| 3 | Ovenstående, plus at hver SLI har feltet "kan måles i dag: ja / nej / delvist — og hvad der mangler"; plus at mindst én SLI måler **arbejde udført** (påmindelser sendt mod påmindelser der burde være sendt) og ikke kun latens; plus at error budget er regnet på mindst én SLI **både** request-based og window-based med to forskellige tal og én sætning om hvorfor det samme løfte giver to tal |

### K4 — Signalvalg og kardinalitet (vægt 3)

*Findes fordi:* `tenant_id` som metric-dimension vælter ikke systemet. Det ødelægger tallene lydløst fra kunde nummer 2001 — og i dette hus er det allerede sket én gang uden at nogen skrev det ned.

| Score | Sådan ser det ud |
|---|---|
| 0 | Alt bliver logs, eller alt bliver metrics. `tenant_id` foreslås som metric-dimension uden forbehold |
| 1 | Skellet metric/span/log nævnes, men uden regel, og uden at et eneste felt er placeret konkret |
| 2 | Der findes en tabel med mindst 12 navngivne felter placeret som metric-dimension, span-attribut eller log, plus mindst tre felter under "sendes aldrig". Kardinalitetsgrænsen nævnes med et tal |
| 3 | Ovenstående, plus at kardinalitetsbudgettet er **regnet**: antal serier pr. metric som produktet af de valgte dimensioners værdimængder, holdt op mod grænsen, med et tal for ved hvilket tenant- og dokumenttypeantal grænsen rammes. Plus en note om hvad overflow-bucketen gør ved tallene og hvordan man opdager det. Plus at valget mellem ét bredt event pr. arbejdsenhed og tre adskilte signaler er truffet eksplicit |

### K5 — Telemetri som løfte og bevis (vægt 3)

*Findes fordi:* "Success" er ikke bevis for at der blev gjort noget, og 99,97 % er ikke oppetid hvis ingen har defineret ordet. Begge dele er allerede sendt til en kunde.

| Score | Sådan ser det ud |
|---|---|
| 0 | "Natkørslen kørte, der står Success." Eller: SLO sat til 99,9 % uden reference til kontraktens 99,5 % |
| 1 | Erkender at Success ikke er bevis, men foreslår kun "mere logning" |
| 2 | Der er designet et positivt bevis: forventet mod faktisk antal (behandlede rækker, sendte påmindelser, sprunget over med årsag), en alarm der fyrer på **udeblevet** kørsel og ikke kun på fejl, og et tal der kan stå i den månedlige rapport. Den interne SLO er sat i forhold til kontraktens tal med en angivet margin |
| 3 | Ovenstående, plus alle fire: (a) et eksplicit, skriftligt svar på hvad der kan og ikke kan siges om natten til den 10., med den usikkerhed sampling og daily cap påfører; (b) en definition af "oppetid" som kunde og leverandør kan læse ens, med målepunkt og hvem der måler; (c) servicekredit-eksponeringen regnet i kroner for ét konkret brud; (d) sætningen om at det tal virksomheden fakturerer imod, kommer fra et instrument virksomheden selv ejer, selv konfigurerer og selv kan slukke |

### K6 — Alarmkataloget (vægt 3)

*Findes fordi:* elleve ignorerede alarmer er ikke elleve problemer. Det er ét: ingen har nogensinde skullet svare på hvem der vågner.

| Score | Sådan ser det ud |
|---|---|
| 0 | Alarmerne beholdes som de er, eller de elleve støjende slettes uden analyse af hvorfor de fyrer |
| 1 | Alarmerne grupperet i behold/slet, men uden hvem der vågner og uden to-timers-testen |
| 2 | Alle 14 gennemgået med behold / omskriv / slet og begrundelse pr. linje. For hver overlevende: hvem vågner, hvad gør de, hvad sker der hvis ingen reagerer i to timer. Mindst én sletning, og slutantallet er lavere end 14 |
| 3 | Ovenstående, plus alle tre: mindst én alarm kandidaten **nægter at bygge** selvom nogen vil bede om den, med begrundelse; mindst én burn-rate-alarm med både vindue og tærskel angivet og én sætning om hvorfor den står på en metric og ikke på en log; og en eksplicit beslutning om hvad der sker mellem 16.00 og 08.00 — inklusive den mulighed at intet vækker nogen, hvad det så koster kunden i detektionstid, og at det står i den månedlige rapport frem for i en fodnote |

### K7 — Persondata i telemetri (vægt 3)

*Findes fordi:* oprydningen fjerner ikke regningen, og et underskrevet bilag der siger noget usandt, er en anden slags problem end en logline.

| Score | Sådan ser det ud |
|---|---|
| 0 | "Vi fjerner e-mail fra URL'en." Eller: problemet noteres og udskydes til efter auditten |
| 1 | Redaction foreslås ét sted, typisk i koden, uden rækkefølge og uden at de tre kendte indgangsveje er talt |
| 2 | Alle tre kendte veje adresseret (query string, exception-besked, message template-property), med et lag pr. vej og en rækkefølge der sætter filtrering **før** lagring. Der er planlagt en systematisk søgning efter flere veje. Datapolitikken på én side er skrevet og indeholder læseadgang og retention |
| 3 | Ovenstående, plus alle fire: (a) eksplicit skel mellem fremadrettet standsning og bagudrettet oprydning, inkl. at sletning og purge ikke påvirker regningen; (b) et svar til Poul der er sandt, herunder at bilag 3's sidste sætning ikke passer, hvad der rettes hvor, og hvem der underskriver rettelsen; (c) legal hold behandlet som en navngiven konflikt frem for en løsning — hvilke data, hvem beslutter, hvad der sker indtil da; (d) et tal for hvor stor en del af de 90 dages retention der indeholder personoplysninger, **med angivet usikkerhed** |

### K8 — Måleapparatets pris i kroner, med spænd (vægt 2)

*Findes fordi:* det er den vinkel ledelsen forstår uden oversættelse, og fordi et byte-budget er den eneste måde at holde et loft når volumen fordobles.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen tal, eller kun den samlede Azure-regning |
| 1 | Kr./md. nævnt, men uden GB, uden kilde og uden spænd |
| 2 | MB pr. 1.000 requests og MB pr. natkørsel med angivet metode; kr./md. for måleapparatet før og efter forslaget; spændet angivet i **procentpoint**; mindst ét tal mærket som hentet fra en prisliste med dato og mindst ét mærket som gæt |
| 3 | Ovenstående ved to volumener (i dag og efter præmisskiftet), opdelt på table plan, plus en eksplicit vurdering af hvad Auxiliary ville koste i evne (alarmer virker ikke) og at plan-skift kun kan ske én gang pr. tabel pr. uge. Plus: det dyreste **enkeltfelt** i telemetrien udpeget med kr./md. |

### K9 — Samplingens pris i diagnostisk evne (vægt 3)

*Findes fordi:* det er casens ene irreversible valg. Bytes du ikke sender, kan du ikke hente igen, og listen over spørgsmål du har opgivet, er det artefakt der adskiller en arkitekt fra en der har skruet ned.

| Score | Sådan ser det ud |
|---|---|
| 0 | Sampling foreslået eller afvist uden at nævne hvad der tabes. Eller: sampling behandlet som en indstilling frem for et valg |
| 1 | "Vi mister noget detaljegrad" uden liste og uden tal |
| 2 | En navngiven liste på mindst fem spørgsmål der ikke længere kan besvares efter forslaget, hver med hvem der ville stille det og i hvilken situation. Plus: det står skrevet at metrics ikke samples, og at alarmerne derfor står på metrics |
| 3 | Ovenstående, plus alle fire: (a) at trace-based sampling for logs dropper logs der hører til usamplede traces, og at en alarm på en logline derfor forsvinder stille; (b) et tal for fejlen på `itemCount`-vægtede tællinger, med angivet usikkerhed; (c) verifikationen kørt eller planlagt som en query der kan gentages og datostemples; (d) mindst ét sted hvor kandidaten vælger **ikke** at sample, begrundet i kroner mod evne — typisk natkørslen, hvor volumen er lav og bevisværdien høj |

### K10 — Fravalgene, afvist på en målbar akse (vægt 3)

*Findes fordi:* et observability-forslag uden fravalg bliver til en platform. En arkitekt kendes på dybden af sine beslutninger, ikke på bredden af sit stillads.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen fravalg, eller fravalg begrundet med smag ("det er overkill her") |
| 1 | 1-2 alternativer nævnt, afvist i prosa uden tal |
| 2 | Mindst tre navngivne alternativer afvist, hvert på **én målbar akse med et tal og en enhed** — kr./md., MB pr. 1.000 requests, udviklerdage, procentpoint, minutter til detektion |
| 3 | Ovenstående, plus at mindst ét fravalg er noget kandidaten selv havde lyst til; plus at mindst ét fravalg rammer noget populært (browser-OTel, Prometheus/Grafana ved siden af, et nyt dashboard-lag, egen Collector-build, daily cap som besparelse) med en **genovervejelsesbetingelse knyttet til en version, et tal eller en dato**; plus at aksen er den samme som den anbefalingen selv måles på |

### K11 — Faldsbetingelsen (vægt 3)

*Findes fordi:* uden den er ADR'en en begrundelse, ikke en beslutning. Og fordi denne case indeholder præcis den situation hvor faldsbetingelsen bliver ubelejlig.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen. Eller "vi tager det op igen om et halvt år" |
| 1 | Én betingelse, uden tærskel og uden enhed |
| 2 | Mindst tre betingelser, hver med tærskel, enhed og hvem eller hvad der ville opdage den |
| 3 | Ovenstående, plus alle tre: mindst én betingelse er knyttet til et tal der **allerede måles af det apparat kandidaten selv har foreslået**, så den kan udløses uden at nogen husker den; mindst én betingelse er ubehagelig og ville vælte kandidatens egen anbefaling; og der står hvad man **gør** når den udløses — hvem beslutter, inden for hvor mange dage, og hvad det koster |

### K12 — Iteration ved præmisskiftet (vægt 3)

*Findes fordi:* det er det ene punkt hvor materialets kompetencemodel er direkte observerbar. Når præmissen ændres midtvejs, itererer du i stedet for at forsvare.

| Score | Sådan ser det ud |
|---|---|
| 0 | Præmisskiftet ignoreret, eller besvaret med en forklaring på hvorfor forslaget stadig holder |
| 1 | Enkelte tal justeret, konklusionen uændret, ingen ny rangering, intet trukket tilbage |
| 2 | Inden for 45 minutter: opdateret SLI-katalog, opdateret alarmkatalog og opdateret kronetal, plus en eksplicit sætning om hvad der **ikke** ændrer sig og hvorfor |
| 3 | Ovenstående, plus alle tre: mindst ét valg trukket tilbage med navn og begrundelse; en eksplicit optælling af hvilke allerede skrevne påstande der nu er usande — herunder hvad der kan siges om natten til den 10.; og kandidatens egen faldsbetingelse tjekket mod skiftet, udløst eller ikke udløst, sagt højt frem for stiltiende forbigået |

**Beståelsesgrænse:** mindst **64 af 102 point (63 %)**, **og** mindst 2 på hver af K1, K3, K4, K6, K9, K10, K11 og K12, **og** intet 0 på noget kriterium. Falder ét af de tre led, er casen dumpet uanset totalen. En besvarelse med 70 point og et 0 på K9 er ikke en god besvarelse med en svaghed — det er et måleapparat hvis pris i indsigt ingen har opgjort, og det er præcis den fejl der først opdages under en hændelse.

**"Stærk" kræver:** mindst **83 af 102 (81 %)**, **og** 3 på mindst tre af K3, K6, K9, K10, K11 og K12, **og** mindst 2 på alle tolv, **og** at timeboxen er holdt (maks. 8 timer 45 minutter inklusive præmisskiftet). Det svarer til kompetencemodellen i modul 01: kompetent på alle akser og stærk på ingen er en dumpet port, fordi rollen bæres af trade-off-analyse og driftbarhed. Er du over 83 point men over tid, er scoren ikke gyldig — evnen der testes er at levere et forsvarligt måleapparat **inden for** otte timer, ikke at levere et godt et.

## Kalibrering: skriv dette ned FØR du går i gang

Fem forudsigelser. Skriv dem i en fil, gem den, rør den ikke før timeboxen er slut.

1. **Hvor stor en andel af de 812 GB kommer fra én enkelt logger-kategori?** Ét procenttal og et spænd, fx "40 % ± 20". Skriv det før du har set fordelingen.
2. **Hvor mange af de 14 alarmer overlever din gennemgang?** Ét tal mellem 0 og 14. Skriv det før du har set hvad de fyrer på.
3. **Hvor mange af dine 3-5 SLI'er kan måles med den instrumentering der findes i dag?** Ét tal. De fleste skriver for mange.
4. **Hvor mange MB bruger måleapparatet pr. 1.000 requests i dag, og hvor mange efter dit forslag?** To tal, plus faktoren imellem. Ram inden for en faktor 10, og du er på niveau 3 i modul 02's selvvurdering.
5. **Hvad bliver sværest?** Én sætning, maks. 15 ord.

**Hvad var jeg sikker på og tog fejl om** — udfyldes efter timeboxen, mindst tre linjer, hver af formen "jeg troede X, det var Y, årsagen var Z". Er feltet tomt eller siger "ingenting", er kalibreringen dumpet, ikke perfekt. En kandidat der ikke tog fejl om noget i et hus hvor ingen har målt noget, har ikke målt noget.

## Modelbesvarelsens omrids

**LÆS FØRST EFTER FORSØG.** Ikke et facit. Et omrids af hvad en stærk besvarelse indeholder, og hvilke veje der er forsvarlige.

**Tre forsvarlige veje**

- **A. Kundeoplevelsen først, billigt.** Udled tre til fire SLI'er direkte af Mettes tre ting plus én platform-SLI, og instrumentér **kun** det de kræver: tre til fire altid-tændte metrics med lav kardinalitet, ét bredt span pr. dokument og pr. natkørsels-leverandør med 12-20 attributter, og logs kun ved afvisning og fejl. Alarmer flyttes til metrics. Hurtigst til noget der virker, og rammer præcis det kunden faktisk opdager. Falder på ét punkt: den siger ikke noget om auditten den 8. oktober, og den skal derfor bæres af et parallelt spor på datapolitikken.
- **B. Bevisførelse først, auditdrevet.** Den hårde dato er kundens audit, ikke Jens' rapport. Byg telemetri-datakortet, datapolitikken, redaction i tre lag og rettelsen af bilag 3 først; læg SLI-arbejdet ovenpå bagefter, med natkørslens tælling som første SLI fordi den både er bevis og målepunkt. Langsommere til kroner, men den eneste vej der er forsvarlig hvis du tror auditten kan rykke — og den kan, hvilket den gør.
- **C. Volumen først.** Fjern den dominerende logger-kategori og daily cap'en, mål hvad der er tilbage, og designer SLI'erne mod det instrument du har renset. Hurtigst på penge. Forsvarlig kun hvis du kan sige hvilke spørgsmål der forsvandt før du havde skrevet ned at du ville stille dem — og det kan de færreste, hvilket er grunden til at vejen oftest fejler.

Alle tre er forsvarlige. Den urimelige er kun én: at slette de elleve støjende alarmer, beholde de tre stille, og kalde det alarmoprydning.

**Hvad en stærk besvarelse desuden indeholder**

- SLI'erne er skrevet i ord først, og mindst én af dem kan **ikke** måles i dag. Det står som en linje i kataloget, ikke som en undskyldning i teksten. Modul 06 siger det direkte: det er pointen.
- Natkørslen har fået en positiv succesdefinition — behandlede rækker, sendte påmindelser, sprunget over med årsag, og en forventet-mod-faktisk sammenligning — plus en alarm på udeblevet kørsel. Den alarm findes ikke i dag, og den ville have fanget den 10.
- Availability-tallet på 99,97 % er kaldt hvad det er: en måling af at processen svarer. Det står i notatet til Jens, høfligt, med konsekvensen at tre besvarede spørgeskemaer indeholder et tal virksomheden ikke kan forsvare i et auditrum.
- De tre stille alarmer er identificeret som brudte, ikke som sunde. Mindst én af dem er nævnt i bilag 6 punkt 5.3, og den kobling står skrevet.
- Persondata er standset fremadrettet i tre lag med filtrering før lagring, og oprydningen bagud er behandlet særskilt — inklusive at sletning ikke påvirker regningen, og at to af de berørte kontaktpersoner ligger under et legal hold ingen har afgrænset. Konflikten navngives; den løses ikke på otte timer, og en besvarelse der påstår andet er svagere, ikke stærkere.
- Bilag 3's sidste sætning er identificeret som usand og som noget der skal rettes af nogen med underskriftsret. Det er ikke en udviklerbeslutning, og det siges.
- Tabslisten findes, den er navngiven, og mindst ét punkt på den gør ondt.
- Fund undervejs der ikke stod i opgaven: at seks personer og to fratrådte medarbejdere kan læse telemetrien; at daily cap'ens nulstillingstidspunkt gør et natjob systematisk sårbart; at `tenant_id` blev fjernet i februar uden en ADR, så husets næste kardinalitetsproblem er en gentagelse.

**Hvad der adskiller den stærke fra den kompetente**

| Den kompetente | Den stærke |
|---|---|
| Definerer fire SLI'er | Definerer fire, og markerer den ene der ikke kan måles endnu |
| Måler svartid | Måler også arbejde udført, fordi det var det kunden nævnte først |
| Rydder op i alarmerne | Sletter, nægter at bygge én, og siger hvad der sker om natten når svaret er "ingenting" |
| Foreslår redaction | Skelner fremadrettet standsning fra bagudrettet oprydning, og ved at den ene er gratis og den anden ikke er |
| Angiver en usikkerhed | Angiver den i procentpoint og siger hvilket enkelt gæt der bærer mest af anbefalingen |
| Nævner at sampling koster indsigt | Afleverer listen over de spørgsmål der er opgivet, med hvem der ville stille dem |
| Opdaterer designet efter præmisskiftet | Siger også hvilke sætninger han allerede har skrevet der nu er usande |
| Svarer kunden pænt | Svarer kunden sandt, og siger hvad der skal rettes i et underskrevet bilag |
| Holder budgettet i dag | Holder bytes pr. arbejdsenhed, så budgettet også holder ved 2,4 gange volumen |

## Sådan ser en dårlig besvarelse ud

Skrevet som du selv ville formulere det. Formålet er genkendelse, ikke skam.

1. *"Jeg slettede de elleve alarmer der fyrer hver uge, og beholdt de tre der ikke gør. Nu er der ro."* — Du har slettet støj og beholdt tre alarmer der ikke virker, hvoraf den ene er lovet skriftligt til kunden. Roen er ægte. Dækningen er nul, og du har gjort den værre uden at kunne se det.
2. *"Vi sætter SLO'en til 99,9 %, det er standard."* — Kontrakten siger 99,5 med servicekredit, ingen har defineret oppetid, og det eneste instrument der måler den, pinger et endpoint som var grønt mens databasen var nede i 22 minutter. Du har sat et pænt tal oven på en måling der ikke måler noget.
3. *"Natkørslen kørte fint — der står Success, og der er ingen exceptions i loggen."* — Fraværet af fejl er ikke bevis for arbejde. Jobbet fanger og sluger fejl pr. leverandør, der findes ingen tælling af noget som helst, og telemetrien for netop den nat er væk på grund af en daily cap ingen læste alarmen på. Du har sendt et svar til en kunde du ikke kan holde.
4. *"Jeg slog sampling til 10 % — det halverer log-regningen."* — Måske. Men du har ikke skrevet ned hvilke spørgsmål du dermed opgav, du har ikke tjekket at to alarmer stod på en log-tabel, og du har ikke opdaget at der allerede blev samplet før du rørte noget. Besparelsen er ægte. Prisen er ubetalt og ukendt.
5. *"Persondata i logs er noteret som et opfølgningspunkt efter auditten."* — Kundens sikkerhedschef har stillet et skriftligt spørgsmål med henvisning til et bilag der er underskrevet. At udskyde svaret er selv et svar, og det er det svar der ender i auditrapporten.
6. *"Jeg lavede et dashboard med de vigtigste metrikker, så alle kan følge med."* — Et dashboard besvarer spørgsmål du kendte i forvejen. Ingen af Mettes tre ting står på det, det bliver ikke set efter uge tre, og det føltes mest produktivt af alt hvad du lavede.
7. *"Præmissen ændrede sig, men mine SLI'er holder faktisk stadig, hvis man ser på det på den her måde."* — Det er forsvar. To af dine alarmer stod på en tabel der beholder 23 %, og din udtalelse om natten til den 10. er nu usand. Det er den ene sætning en bedømmer lytter efter, og den kan ikke bortforklares bagefter.
8. *"Jeg satte daily cap ned til 2 GB for at holde budgettet."* — Du har gjort casens årsag til casens løsning. Cap'en er grunden til at du ikke kan svare kunden, og Microsofts egen formulering er at du derefter er blind for den aktuelle tilstand i det miljø du overvåger.

## Hvor i materialet svaret står

Ubarmhjertig version. Ét kriterium er ikke dækket af noget modul, og det er et fund i materialet, ikke i casen.

| Kriterium | Modul | Præcis sektionsoverskrift | Hvad du henter der |
|---|---|---|---|
| **K1** Spørgsmål før første signal | 01 | `### Øvelse 3: Trade-off-kata på tid` | "Mindst otte kravsspørgsmål stillet **før** første diagram", timeboxen, og selvkontrollen til sidst: besvarede du dit eget design uden svar på halvdelen, er det fundet. Suppl.: 06 `## Faldgruber` punkt 1 — "definér først de fem spørgsmål telemetrien skal besvare, instrumentér derefter kun det" |
| **K2** Spørgsmålene rammer det kunden mærker | 06 | `## På jobbet, uden at spørge om lov` | Spørgsmålsloggen: hver gang nogen stiller et spørgsmål om produktionsadfærd som ingen kan besvare på 10 minutter — dato, hvem spurgte, hvor lang tid det tog. Suppl.: 09 `## 90-dages plan: bliv husets mest domænekyndige person` for "hvad gør I stadig i Excel ved siden af vores system", planens mest værdifulde spørgsmål; og 10 `## Kvalitetsattribut-scenarier: din del af kravarbejdet` for den seksdelte form hvor responsmålet altid er et tal |
| **K3** SLI'erne i ord før i KQL | 06 | `## Spikes: hvad du bygger, og hvad der ligger på disken bagefter` (række **O-3** og afsnittet under tabellen) | O-3's output: SLO-dokument pr. SLI, KQL der beregner error budget i hånden, request-based mod window-based. Og sætningen der er hele kriteriet: "i O-3 skriver du tilsvarende SLI'en i ord først … og opdager at du ikke kan måle den med din nuværende instrumentering. Det er pointen." Suppl.: 06 `## Sådan ved du at du kan det` — "hvorfor den samme 99,9%-SLO giver to forskellige tal målt request-based mod window-based" |
| **K4** Signalvalg og kardinalitet | 06 | `## Signalvalg: den ene tabel du skal kunne udenad` | Tabellen alert/undersøg/læs-forløbet mod metric/span/log, reglen om lav kardinalitet på metrics, og kardinalitetsfælden med tallet: default 2000 pr. metric, overflow-bucket siden 1.10.0, tallene ødelægges lydløst fra kunde nummer 2001. Suppl.: 06 `## Den mentale model: wide events, ikke tre signaler` for span-design som beslutningen om hvilke spørgsmål du kan stille om tre måneder |
| **K5** Telemetri som løfte og bevis | — | **IKKE DÆKKET** | Delvist berørt tre steder, ingen af dem dækkende: 06 `## Spikes…` (O-5) har fejlmønstre der ligner — en afhængighed der bliver langsom men ikke fejler, en poison message der retryer — og kravet om at notere fejlens opståen, **din** opdagelse og mitigation separat; 06 `## Sådan ved du at du kan det` nævner at context tabes i baggrundsjobs og kø-consumers; 11 `## Fire spikes med fysisk output` (spike A om certifikatudløb og varslingsvinduer) nævner "krav om at kunne bevise at varslingen blev sendt". Der mangler to ting helt. **Ét:** batch- og jobobservability som egen disciplin — heartbeat og dead man's switch, forskellen på "kørte" og "gjorde noget", forventet mod faktisk output, og hvordan et planlagt job der rapporterer Success uden at have arbejdet, overhovedet opdages. **To:** afstanden mellem en intern SLO og et kontraktuelt løfte — hvilken margin man lægger ind, hvem der måler oppetiden når begge parter fakturerer på tallet, hvad servicekredit koster i kroner, og hvad man gør når det eneste måleinstrument ejes af den part der skylder pengene. Materialet lærer dig at bygge SLO'er indad, ikke at love dem udad |
| **K6** Alarmkataloget | 06 | `## Faldgruber` (punkt 3) | Testen ordret: "hvem vågner, hvad gør de, hvad sker der hvis ingen reagerer i to timer. Består den ikke, slettes alerten." Plus punkt 4 om SLO uden konsekvens. Suppl.: 06 `## Sådan ved du at du kan det` — "du har **slettet** mindst én alert du selv byggede. Sletningen er det egentlige målepunkt"; og 06 `## Ressourcer` for Google SRE Workbook kap. 2 og 5, burn-rate-matematikken bag Azures burn-felter. **Delvist hul:** alert-governance nævnes i `## Progressionen: fire niveauer` som niveau 4, men der står intet om ejerskab, udløbsdato eller revision af en alarm — kun at den skal slettes hvis den fejler testen |
| **K7** Persondata i telemetri | 06 | `## Persondata i telemetri: her mødes faget og domænet` | Microsofts prioriterede rækkefølge (DCR-transformationer "by far the best option", derefter interne id'er med lookup, derefter Delete/Purge), de tre redaktionslag, detaljen at sletning og purge ikke påvirker billing, og kravet om en telemetri-datapolitik på én side inkl. "hvad der sker ved en sletteanmodning med legal hold". Suppl.: 08 `### 2. Sletning og retention, inklusive backup-paradokset (20-25 t)` for kortlægningen af hvert sted et navn kan ende, inkl. Application Insights; 08 `## Fem krav du sporer hele vejen ned` for rækken GDPR art. 32(1)(a) med redaktionsprocessor i telemetripipelinen som kontrol; 09 `## Problemkataloget: hvad der faktisk er svært i domænet` for "Sletning under legal hold: tre indbyrdes modstridende krav, ingen løsning uden ulemper" |
| **K8** Kroner med spænd | 06 | `## Cost er et arkitekturproblem, ikke et driftsproblem` | Fakturamekanikken: per GB (10⁹ bytes) ingest, `_IsBillable`, faktureret størrelse ~25 % under rå JSON, table plans med deres fælder, ét plan-skift pr. tabel pr. uge, rækkefølgen af indgreb i den orden en arkitekt siger dem, og daily cap som forsikring frem for besparelse. Suppl.: 06 `## Spikes…` (O-4) for modellen på målte `_BilledSize` ved 1x/10x/100x; 03 `## Budgetloftet: 400 DKK/md, hård alert ved 600` for de 5 GB gratis og ~14,80 DKK/GB derefter — "det er derfor sampling ikke er akademisk"; 03 `## Ressourcerne` for Retail Prices API som kilde med dato |
| **K9** Samplingens pris i diagnostisk evne | 06 | `## Cost er et arkitekturproblem, ikke et driftsproblem` (afsnittet "To ting om sampling") | Metrics samples aldrig, derfor står alerts på metrics; trace-based sampling for logs dropper logs der hører til usamplede traces, så en alert på en log-linje forsvinder stille; og verifikations-KQL'en med `RetainedPercentage = 100/avg(itemCount)`. Suppl.: 06 `## Spikes…` (O-2) hvor outputkravet er **listen over spørgsmål du ikke længere kan besvare**, byte-budget pr. request, og de fem spørgsmål der stadig skal kunne besvares under et fast loft |
| **K10** Fravalg på en målbar akse | 01 | `## Kompetencemodellen: ti akser` (rækken "Trade-off-analyse og ADR'er") | Kolonnen *Stærk* er ordret dette kriterium: "Afviser på en akse han kan måle eller prissætte, og siger hvad der ville vende valget". Suppl.: 06 `## Modenhedsstatus 2026: det de fleste blogposts tager fejl af` for det konkrete nej med genovervejelsesbetingelse (ikke OTel til browser-RUM, fordi pakkerne er 0.x); og 06 `## Ressourcer` sidste afsnit, "Fravalgt bevidst, og du skal kunne begrunde det" — Prometheus/Grafana, Jaeger, ELK, eBPF, custom Collector-builds |
| **K11** Faldsbetingelsen | 06 | `## Sådan ved du at du kan det` | "Mindst én ADR hvor du siger nej til noget populært med en eksplicit genovervejelsesbetingelse … vi genovervejer når `auto-instrumentations-web` når 1.0." Suppl.: 09 `## Sådan ved du at du kan det` (rækken "ADR-tællingen"): "Hvert dokument har et afsnit om hvad der ville få os til at ændre beslutningen. Mangler det, er det en begrundelse, ikke en beslutning" |
| **K12** Iteration ved præmisskift | 01 | `## Sådan ved du at du kan det` (2. punkt) | "Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse." Suppl.: 01 `### Øvelse 3: Trade-off-kata på tid`, sidste afsnit om at en ekstern person ændrer en præmis efter fire timer og måler om du itererer eller forsvarer; og 01 `## Arkitektur er de dyre beslutninger` om at kandidater afvises fordi de forsvarer i stedet for at iterere |

## Ekstern kalibrering

Din egen score er værdiløs alene, og en kollega i et nimandsfirma tæller halvt. Mindst to af disse skal have givet **skriftlig** kritik, før casen tælles som gennemført. Spørg hver om én ting — ikke om en helhedsvurdering, for den får du en høflig udgave af.

| Hvem | Hvor du finder dem | Det konkrete spørgsmål |
|---|---|---|
| SRE eller driftsansvarlig i et større hus | LinkedIn, kold henvendelse til en der skriver om Azure Monitor, SLO'er eller on-call | "Her er mine fire SLI'er og min tabsliste. Hvilket spørgsmål kunne I ikke besvare bagefter, som I ikke vidste I ville få brug for?" |
| Praktiserende Azure-arkitekt med FinOps-berøring | Aarhus .NET User Group eller en GOTO-meetup; bed om 30 minutter efter oplægget, ikke under | "Angrib mit byte-budget. Hvilket felt har jeg beholdt som du ville have droppet, og hvad ville det have kostet mig?" |
| Code review-byttepartneren fra måned 3 | Fast kadence, 45 minutter, aftalt som en byttehandel og ikke som goodwill | "Læs mine tre fravalg. Kan du argumentere mig ned på ét af dem — på min egen akse?" |
| En DPO eller privacy-jurist, gerne den Fjordhus selv bruger | Datatilsynets netværk, en lokal advokat, eller kundens egen DPO via et audit-opkald hvor du sidder med som referent | "Er mit svar til kunden sandt nok til at stå i en auditrapport, og hvad ville du selv have spurgt om bagefter?" |
| Ikke-teknisk læser uden forberedelse — Lone, en controller, en sælger | Internt, 20 minutter | Giv dem notatet til Jens og sig intet. Bed dem bagefter gengive: hvad skete der natten til den 10., hvad kan vi rapportere fra 1. oktober, og hvad koster det. Alt de misforstår er en fejl i notatet, ikke i deres forståelse |
| Ekstern design-review-mentor (1-2 t/md., 15.000-25.000 kr./år, jf. modul 10) | ADPList eller en betalt aftale rammesat som ekstern review af arkitekturbeslutninger | "Min ADR siger nej til to ting. Er genovervejelsesbetingelserne skarpe nok til at nogen andre end mig kan udløse dem?" |
| Offentligheden | Publicér ADR'en og tabslisten, og bed eksplicit om modsigelse, jf. modul 06 `## Eksternt modspil` | "Her er de fem spørgsmål jeg ikke længere kan besvare, og hvorfor jeg valgte det. Hvilket af dem kommer til at gøre mest ondt?" Nul kritik er en dumpet test |

Notér for hver: hvad de sagde, hvad du ændrede, og hvad du valgte at lade stå — plus hvorfor. Den tredje kolonne er den en kommende arbejdsgiver spørger ind til.
