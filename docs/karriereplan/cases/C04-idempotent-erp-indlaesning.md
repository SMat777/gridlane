# C04 — Idempotent ERP-indlæsning fra tre kunder uden fælles nøgle

| | |
|---|---|
| **Type** | Integrationsdesign |
| **Primært modul** | 04 — Systemdesign, distribuerede systemer og integrationsmønstre |
| **Sekundære moduler** | 09 (Domæneekspertise SRM), 02 (Teknisk fundament) |
| **Timebox** | 8 timer, hård. Præmisskiftet lægges oveni og må koste maks. 45 minutter ekstra |
| **Sværhedsgrad** | 4 af 5. Svær på både teknik og dømmekraft, og den eneste case hvor et forkert svar kan ødelægge data der ikke kan genskabes. Giver mening i **måned 5-8**: før måned 5 har du ikke kørt spike A i modul 04 eller spike 8 i modul 02 og mangler egne tal for hvad et idempotenslag koster; efter måned 9 har spike 2 i modul 09 foræret dig halvdelen af svarene. Bedst i måned 6-7 |
| **Afleveringsformat** | Ni artefakter: kravsspørgsmålsliste (1 side, tidsstemplet), leveringssemantik- og idempotensnotat (maks. 3 sider), feltafbildning og kildepræcedens (regneark, min. 18 felter), match- og fletteregler (maks. 2 sider), genafspilningsplan (1 side med tal og spænd), omkostningsnotat for idempotenslaget (0,5 side), fravalgsnotat (1 side), ADR (maks. 1,5 side, MADR-minimal), notat til Mette og Katrine (præcis 1 side, ikke-teknisk), selvvurdering (0,5 side). I alt maks. 11 sider plus ét regneark |

> Alle personer, kunder og partnervirksomheder i denne case er opdigtede. Tallene er konstrueret, men i den størrelsesorden en dansk ni-mandsvirksomhed med tre-fire cifrede leverandørantal per kunde reelt ligger i. IDoc-typer, felter og adfærd er beskrevet som de opfører sig i praksis — men **slå dem ikke op midt i timeboxen**. Casen kan ikke løses ved at læse SAP-dokumentation, og hvis du bruger to timer på det, har du valgt den eneste del af opgaven der ikke kræver en afvejning.

## Situationen

Torsdag den 10. september 2026, kl. 09.10. Mette har booket en halv time i det lille mødelokale og har taget sin bærbar med.

Hun er implementeringskonsulent og kører tre onboardings samtidig. Nordhavn Fødevaregruppe A/S i Vejle går i luften med leverandørmodulet mandag den 5. oktober; deres SAP ECC-system lægger en flad IDoc-fil på vores SFTP hver nat mellem 02.00 og 02.40, sat op af deres partner Kvadrant IT A/S. Stjernholm Gruppen A/S har kørt pilot siden juli på Dynamics 365 Business Central; deres partner Fokus Business Solutions sender webhooks når en leverandør ændres. Vestjysk Komponentindustri A/S i Holstebro har hverken SAP eller Dynamics, men et system Ove byggede i 2011 oven på en SQL Server, som lægger en CSV på SFTP kl. 23.30. Birgitte, deres kvalitetschef, har surveillance audit den 12. november og skal kunne fremvise godkendelsesdokumentation på sine leverandører den dag.

Mette siger, at hun bruger omkring en dag om ugen på at rette leverandørdata i hånden, og at det er begyndt at tage tid fra det hun egentlig er ansat til. I Stjernholms tenant ligger der leverandører to gange. Lasse, deres IT-chef, har oprettet tre supportsager på det siden august. I VKI's fil er der rækker hvor CVR-feltet ikke er et CVR-nummer — Mette viser dig en hvor der står "afventer" og en hvor der står et DK-momsnummer med mellemrum imellem cifrene.

Thomas kigger op fra sin skærm og siger, at det er tre filformater og en parser, at importeren allerede kan to af dem, og at CVR er nøglen — den har vi altid brugt. Han mener det er en uges arbejde, hvis bare nogen vil lave mapping-tabellerne.

Katrines onboarding-oversigt i Teams siger "ca. 12.000 leverandører fordelt på tre kunder". Ingen har åbnet en fil og talt.

Der er en ting mere. På et møde hos Nordhavn den 2. september sagde Jens til deres projektleder Anne-Mette, at vi kører de tre foregående måneders IDoc-filer igennem igen ved go-live, så de nye indkøbskategorier kommer med. Det står i Katrines referat som punkt 4. Jens sagde også noget om at det ikke rører deres eget arbejde inde i systemet. Det står ikke i referatet.

Jens har møde med Anne-Mette tirsdag den 15. september kl. 13.00. Han stak hovedet ind i går eftermiddags og sagde: "Sig til hvis der er noget der ikke holder. Jeg skal bare vide om jeg kan bekræfte datoen."

Den 3. juli skiftede VKI's eksport separator fra komma til semikolon, sandsynligvis fordi Ove opgraderede noget hos sig selv. Alle 2.180 rækker blev indlæst med firmanavnet stående i CVR-feltet. Sådan stod det i seks dage, indtil Birgitte ringede. Ingen har skrevet ned hvad der blev gjort ved det bagefter.

Rasmus har kørt et script hen over webhook-loggen i går eftermiddags og har sendt dig et regneark. Han skriver at han ikke er sikker på om han har læst etag-feltet rigtigt.

Du har otte timer. Ove går på pension den 31. december.

## Det du skal aflevere

| # | Artefakt | Format | Krav der ikke kan forhandles |
|---|---|---|---|
| 1 | **Kravsspørgsmål** | 1 side, tidsstemplet pr. spørgsmål | Skrevet **før** første diagram, første feltnavn og første produktnavn. Hver linje har en note om hvad svaret ville ændre i designet |
| 2 | **Leveringssemantik og idempotens** | Maks. 3 sider | Pr. kilde: leveringsgaranti, hvem der ejer fejlen, idempotensnøgle **felt for felt med kildefeltets navn**, ordensregel, og hvad der sker når et felt i nøglen ændrer værdi hos kunden |
| 3 | **Feltafbildning og kildepræcedens** | Regneark, min. 18 felter | Kolonner: kanonisk felt, SAP-kilde, Dynamics-kilde, CSV-kilde, præcedens ved uenighed, adfærd når feltet mangler, adfærd når feltet er tomt mod fraværende |
| 4 | **Match- og fletteregler** | Maks. 2 sider | Tærskler i tal, ikke i ord. Hvad der auto-flettes, hvad der auto-afvises, hvad der går til et menneske — og **hvem** det menneske er, med forventet sagsmængde pr. uge og et spænd |
| 5 | **Genafspilningsplan** | 1 side | For de 92 filer: antal læste poster, antal faktisk skrevne rækker, kørselstid, antal menneskeeskaleringer. Hvert tal med et spænd i procent. Plus én afbrydelsesbetingelse med en tærskel |
| 6 | **Omkostningsnotat for idempotenslaget** | 0,5 side | Millisekunder pr. post, ekstra database-writes pr. post, lagerforbrug i GB, og DKK/md ekskl. moms. Med spænd |
| 7 | **Fravalgsnotat** | 1 side i alt | To forkastede alternativer, hver afvist på **én navngiven, målbar akse med et tal** — ikke to akser, ikke en holdning |
| 8 | **ADR** | Maks. 1,5 side, MADR-minimal | Afsnittet "Dette ville få os til at vælge om" med mindst tre betingelser, hver med en tærskel og en enhed |
| 9 | **Notat til Mette og Katrine** | Præcis 1 side | Nul teknisk jargon. Hvad vi kan love kunderne, hvad vi ikke kan, hvad der lander på et menneskes bord og hvor tit, og hvad de tre kunder skal levere til os. Skal kunne læses på fire minutter og bruges uden at spørge dig |
| 10 | **Selvvurdering** | 0,5 side | Hvilke af dine egne kravsspørgsmål endte du med at besvare med et gæt, og hvilket af de gæt bærer mest af designet |

Artefakt 5 og 6 er dem der har **tal med en usikkerhed**. Artefakt 9 er det der skal kunne læses af en ikke-teknisk læser — og det er det eneste af de ti, der reelt bliver brugt til noget tirsdag den 15.

## Skjulte oplysninger

Du må kun læse svaret på et spørgsmål, du **faktisk har skrevet ned** på artefakt 1, før du begyndte at designe. Skriver du seks spørgsmål og læser fjorten svar, har du ikke lavet casen — du har læst en løsning.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Er de ca. 12.000 leverandører rækker eller juridiske enheder, og hvor mange er aktive? | 11.680 rækker i alt. Nordhavn 6.100, Stjernholm 3.400, VKI 2.180. Dedupliceret pr. tenant på CVR/VAT: 8.910. Med mindst én transaktion inden for 12 måneder: **4.140**. Nordhavns 6.100 er 4.700 distinkte LIFNR fordelt på fire company codes, og 1.180 af dem er samme juridiske enhed oprettet flere gange med hver sit vendornummer |
| 2 | Hvad er den faktiske ændringsrate pr. nat pr. kilde? | SAP: gennemsnitligt **34 ændrede leverandører pr. nat** målt over 14 dage, min. 0, max. 611 den nat de masseopdaterede betalingsbetingelser. Men filen indeholder **alle 6.100 hver nat** — det er et fuldt udtræk, ikke en delta. Ingen har fortalt det, og ingen har spurgt. Dynamics: ca. 180 notifikationer i løbet af dagen plus en burst på ca. 3.400 kl. 02.15 hver nat, når deres egen periodisering rører alle leverandørposter. VKI: fuld fil, 2.180 rækker, ca. 9 reelle ændringer pr. dag |
| 3 | Hvad står der i IDoc'ens kontrolrecord, og er DOCNUM stabil ved genafspilning? | CREMAS05 til leverandøren, ADRMAS03 til adressen. DOCNUM er unikt pr. **afsendelse**, ikke pr. faktum. Kvadrant IT genererer nye IDocs ved en genafspilning: nyt DOCNUM, ny CREDAT/CRETIM. Adressen kommer i en separat ADRMAS-IDoc med sit eget ADRNR, og de to IDocs ligger ikke nødvendigvis i samme fil samme nat — i 3 ud af 14 målte nætter kom adressen først natten efter |
| 4 | Har SAP-udtrækket et ændringstidsstempel pr. leverandør? | **Nej.** Kvadrants mapping tager ikke AEDAT/AEZET med fra LFA1. Det eneste tidsstempel er IDoc'ens CREDAT/CRETIM, som er identisk for alle IDocs i samme kørsel og har sekundopløsning. Der er intet i filen der fortæller hvornår leverandøren sidst blev rørt i SAP |
| 5 | Hvordan markerer SAP en spærret eller slettet leverandør? | Spærrede sendes med SPERM/SPERQ = 'X'. Slettemarkerede (LOEVM = 'X') sendes med i det fulde nattelige udtræk, men forsvandt tidligere helt fra det delta-udtræk Kvadrant kørte frem til maj. Der ligger derfor 40-70 leverandører i Nordhavns SAP, der er slettemarkeret uden at nogen har fortalt os det. Fravær har aldrig betydet sletning, og har heller aldrig betydet uændret |
| 6 | Hvad indeholder Dynamics-webhookens payload, og hvor pålidelig er kanalen? | Fokus Business Solutions sender en egen payload med 22 felter plus `@odata.etag` — en base64-kodet rowversion. Rowversion er monoton **pr. company**, og de har tre companies (DK, SE, NO) i samme miljø. Abonnementet udløber efter 3 døgn og fornyes af et scheduled job hos dem, som fejlede fire gange i august; det største hul var **19 timer den 11.-12. august**. De genudsender ikke det de missede, og der findes ingen catch-up-endpoint. Fokus tager 1.150 kr./time for ændringer og har 4-6 ugers leveringstid |
| 7 | Hvad er duplikat- og ude-af-orden-raten på webhooks, målt? | Rasmus' regneark, 14 dage: **8,1 % duplikater** (samme entitet, samme etag, inden for 90 sekunder). Ude-af-orden: **41 par ud af ca. 2.500 opdateringer, altså 1,6 %**, alle inden for 12 sekunder af hinanden. Rasmus har selv skrevet i mailen at han er usikker på sin etag-parsing, og har ikke valideret mod kilden. Tallet er det bedste vi har og det er ikke efterprøvet |
| 8 | Hvor mange rækker har et ubrugeligt CVR-felt hos VKI, og hvad står der? | 2.180 rækker: 1.998 gyldige 8-cifrede CVR (modulus-11 ok), 61 med "DK" + 8 cifre eller mellemrum (momsnummer), 34 fritekst ("se mail", "afventer", "udgået", "SAMME SOM 21445508"), 12 tomme, 9 udenlandske organisationsnumre (NO, DE, SE), 3 telefonnumre. Og **63 rækker hvor CVR'et er syntaktisk gyldigt og tilhører moderselskabet, mens navn og adresse er en produktionsenhed**. Den sidste kategori fanger ingen validering, og den er den dyre |
| 9 | Er CVR unik pr. leverandør i vores egen model i dag? | **Nej.** Der er fire tilfælde i produktionen i dag hvor to leverandørrækker i samme tenant deler CVR — bevidst oprettet, fordi kunden kvalificerer produktionsenheder hver for sig og fører separate auditrapporter og CAPA'er på dem. Thomas ved det ikke. En unik constraint på (tenant, cvr) fejler på fire rækker i dag og på anslået 170-220 efter indlæsningen. Estimatet er ikke målt, det er talt op i hånden på 100 stikprøverækker |
| 10 | Hvor mange felter i RELATIONS er manuelt rettet, og kan vi se hvilke? | **Det ved vi ikke.** Der er ingen feltniveau-proveniens. `ModifiedBy` og `ModifiedAt` ligger på rækken, og importservicekontoen står som ModifiedBy på 96 % af rækkerne. En stikprøve på 50 rækker i Stjernholms tenant viste 11 med mindst ét manuelt rettet felt — typisk kontaktperson, kategorikode eller en note om en lukket nonconformity. De kan ikke skelnes fra importdata uden at læse auditloggen række for række, og auditloggen har 90 dages retention. Det er ikke en manglende oplysning, det er et arkitekturvilkår |
| 11 | Må vi bygge ét leverandørindeks på tværs af de tre kunder? | **Nej.** Databehandleraftalerne med alle tre er skrevet på samme skabelon, og § 5.2 forbyder behandling til andet formål end den enkelte kundes. Jens har nævnt et "benchmarkprodukt på tværs af kunder" to gange på ledermøder, senest i august. Der er ikke spurgt, der er ikke indhentet samtykke, og der er ikke skrevet noget ned. Hydra-Tech Sealing ApS optræder både hos Nordhavn (som "HYDRATECH SEALING APS") og hos VKI (som "Hydratech Sealing A/S, Vejle"), og det er to leverandører, ikke én |
| 12 | Hvad har Jens præcis lovet Nordhavn om genafspilningen? | Referatet af 2. september, sendt af Katrine den 3. september kl. 16.42, punkt 4: *"LeanLinking genindlæser leverandørdata for perioden 1. juni – 31. august, så de nye indkøbskategorier er tilgængelige ved go-live 5. oktober."* Mundtligt sagde Jens også "det rører ikke jeres eget arbejde i systemet". Anne-Mette husker det og har gentaget det til to af sine indkøbere. Det står ikke i referatet, og der er ikke andre der kan bekræfte det |
| 13 | Hvad koster den nuværende manuelle håndtering, og hvad er infrastrukturloftet? | Mettes eget skøn er "en dag om ugen"; hun har ikke målt det, og der findes ingen sagsliste — arbejdet ligger i hendes indbakke. Belastet timepris 420 kr. Otte timer/uge giver ca. 14.500 kr./md, men skønnet kan lige så godt være fem timer. Kontrakterne: Nordhavn 340.000 kr./år, Stjernholm 265.000 kr./år, VKI 118.000 kr./år. Jens' loft for merforbrug i Azure er **900 kr./md ekskl. moms for alle tre kunder tilsammen**, og han vil have tallet med i tilbuddet til VKI's koncern |
| 14 | Hvad kører importen på i dag, og hvordan opdager vi at den fejler? | En Azure WebJob i den eksisterende App Service Plan. Ét enkelttrådet loop, ca. 40 rækker/sekund målt på VKI-filen, ingen kø, ingen parallelitet. Der er et try/catch der logger til Application Insights og fortsætter til næste række. Der er ingen alarm, ingen dead letter og intet sted hvor en fejlet række lander. Service Bus findes ikke i abonnementet i dag. Den samlede platform koster 11.400 kr./md ekskl. moms for 34 tenants |

## Præmisskiftet

**Åbnes først når 4 timer og 48 minutter af timeboxen er gået (60 %). Ikke før. Sæt en timer.**

Fredag den 11. september kl. 15.20 sender Kvadrant IT en mail til Anne-Mette med dig og Jens i kopi. Ændringen er ét faktum: **Kvadrant har change freeze på Nordhavns SAP fra 1. oktober til 15. januar på grund af årsafslutning.** Den er lovlig, den er varslet i deres rammeaftale, og den er ikke til forhandling. Fire ting følger af den:

1. **Go-live rykkes frem til mandag den 28. september.** Nordhavn vil ikke vente til februar. Anne-Mette har allerede booket sine indkøbere til oplæring den 24. og 25.
2. **Genafspilningen kan ikke komme fra SAP.** Nordhavn arkiverer IDocs efter 30 dage, og Kvadrant kan ikke køre en ny historisk udsendelse inden freeze. De tre måneders filer findes kun som de flade filer på **vores egen** SFTP-landingszone — og filerne fra 1. til 19. juni er væk, fordi Rasmus satte en 90-dages retention-regel på containeren i juli. Genafspilningen kan dække 20. juni til 31. august. Jens lovede 1. juni.
3. **Ingen ændring i IDoc-mappingen før 1. februar 2027.** Alt hvad du havde tænkt dig at bede kunden om — et ændringstidsstempel, et stabilt nøglefelt, en slettemarkering, en delta i stedet for et fuldt udtræk — er ude af verden i denne omgang.
4. **Thomas har tre dage, ikke ti.** Jens flytter ham til Stjernholm-piloten den 21., fordi Lasse har eskaleret sine tre supportsager til en fjerde.

**Hvad skiftet er en test af**

- Om du **regner om** frem for at argumentere for at dit design stadig holder. En opdateret genafspilningsplan og et opdateret tal for skrevne rækker inden for 45 minutter er beviset; en velformuleret forklaring er det ikke.
- Om du kan sige højt hvilke af dine beslutninger der **ikke** er berørt, og hvorfor. Én af de fire linjer rører ikke ved din idempotensnøgle overhovedet. Kan du udpege den, har du forstået dit eget design.
- Om din faldsbetingelse fra ADR'en faktisk **udløses** af linje 3 — og om du så følger den, eller finder på en grund til at lade være. Det er casens skarpeste enkeltmålepunkt.
- Om du behandler linje 2 som et **spørgsmål til Jens** frem for som et teknisk problem du selv skal løse i stilhed. Nogen skal ringe til Anne-Mette og sige at nitten dage mangler. Skriver du sætningen han kan sige, eller lader du den ligge?
- Om linje 4 får dig til at ændre **hvad du leverer den 28.**, ikke bare hvor hurtigt du skriver. Tre dage tvinger dig til at rangordne dit eget design, og rangordningen er artefaktet.

## Rubrik

Tolv kriterier, hvert scoret 0-3, med vægt. Maksimum er **99 point**. Ankrene er tællelige med vilje: en bedømmer skal kunne sætte scoren uden at kende kandidaten og uden at bruge ordet "god".

| # | Kriterium | Vægt | Maks. |
|---|---|---|---|
| K1 | Kravsspørgsmål før første feltnavn | 3 | 9 |
| K2 | Spørgsmålene rammer de akser der vælter designet | 2 | 6 |
| K3 | Leveringssemantik og fejlejerskab pr. kilde | 3 | 9 |
| K4 | Idempotensnøglen felt for felt, og hvad der sker når nøglen skifter | 3 | 9 |
| K5 | Anti-corruption layer og kildepræcedens pr. felt | 2 | 6 |
| K6 | Match, flet og menneskelig eskalering med tærskler i tal | 3 | 9 |
| K7 | Genafspilningen regnet igennem med spænd | 3 | 9 |
| K8 | Prisen på dit eget idempotenslag | 2 | 6 |
| K9 | Manuelle rettelser: hvad du kan bevise, og hvad du ikke kan | 3 | 9 |
| K10 | Fravalgene afvist på én navngiven, målbar akse | 3 | 9 |
| K11 | Faldsbetingelsen | 3 | 9 |
| K12 | Iteration ved præmisskiftet | 3 | 9 |
| | **I alt** | **33** | **99** |

### K1 — Kravsspørgsmål før første feltnavn (vægt 3)

*Findes fordi:* integrationsdesign er den disciplin hvor det er lettest at begynde at mappe felter inden nogen har spurgt hvad filen egentlig indeholder. Thomas har allerede gjort det.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen spørgsmålsliste, eller den er skrevet bagefter. Første feltnavn eller produktnavn nævnt inden for de første 20 minutter |
| 1 | 3-7 spørgsmål, ikke tidsstemplede, og mindst ét er et løsningsforslag i spørgeform ("skal vi bruge Service Bus duplicate detection?") |
| 2 | 8-11 tidsstemplede spørgsmål skrevet før første feltnavn, ingen produktnavne, mindst fem rammer skjulte oplysninger, hver med en note om hvad svaret ville ændre |
| 3 | 12+ tidsstemplede spørgsmål, mindst otte rammer skjulte oplysninger, listen er gennemgået igen til sidst, og det står markeret hvilke der **stadig** er ubesvarede i det afleverede design og hvilken del af designet der hviler på et gæt |

### K2 — Spørgsmålene rammer de akser der vælter designet (vægt 2)

*Findes fordi:* tolv spørgsmål om samme akse er ét spørgsmål. De seks dyre akser her er: fuldt udtræk mod delta, stabiliteten af kildens nøgle ved genafspilning, hvad fravær af en post betyder, hvor pålidelig webhook-kanalen er over tid, hvad der allerede er lovet, og om der findes proveniens på manuelle rettelser.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen af de seks akser berørt |
| 1 | 1-2 af de seks |
| 2 | 3-4 af de seks, og mindst ét spørgsmål indeholder selv et tal ("er de 12.000 rækker eller juridiske enheder?") |
| 3 | Mindst fem af de seks, plus mindst ét spørgsmål der ville have afdækket at Thomas' påstand om CVR er forkert, og mindst ét der er formuleret som det skal stilles til kunden, ikke til en kollega |

### K3 — Leveringssemantik og fejlejerskab pr. kilde (vægt 3)

*Findes fordi:* du vælger ikke transport, du vælger hvem der ejer fejlen. Tre kilder giver tre forskellige ejere, og de tre må ikke behandles ens.

| Score | Sådan ser det ud |
|---|---|
| 0 | Én fælles beskrivelse af "importen". Ordet exactly-once bruges om en netværksgrænse |
| 1 | Skelner mellem fil og webhook, men angiver ikke garanti pr. kilde og navngiver ikke hvem der ejer fejlen |
| 2 | Alle tre kilder har navngivet leveringsgaranti, ejerskab af fejlen og en ordensregel. At-least-once plus idempotens hos modtageren er formuleret eksplicit som svaret på webhook-kanalen |
| 3 | Ovenstående, plus at mindst tre af følgende fem er navngivet med konsekvens: at det fulde SAP-udtræk gør hver nat til en implicit genafspilning; at fravær hverken betyder sletning eller uændret; at ADRMAS og CREMAS er to beskeder om ét faktum og kræver en samle- eller ventestrategi; at Dynamics' 19-timers hul kræver en reconciliation-kilde webhooken ikke selv kan levere; at duplicate detection på MessageId i et 10-minutters vindue ikke løser noget her, og hvorfor |

### K4 — Idempotensnøglen felt for felt, og hvad der sker når nøglen skifter (vægt 3)

*Findes fordi:* det er casens kerne, og det er også det ene spørgsmål der oftest afgør en arkitektsamtale. En nøgle uden en plan for hvad der sker når kunden ændrer et felt i den, er en nøgle der ikke er tænkt færdig.

| Score | Sådan ser det ud |
|---|---|
| 0 | Nøglen er CVR, eller et message-id, eller "vi bruger en hash af hele rækken" uden videre |
| 1 | Nøglen er en business key, men beskrevet i ord uden kildefeltnavne, og der står intet om nøgleskift |
| 2 | Nøglen er angivet felt for felt med kildens egne feltnavne pr. kilde (fx tenant + kildesystem + LIFNR + BUKRS for SAP), og der er en beskrevet adfærd for nøgleskift |
| 3 | Ovenstående, plus at det er skrevet ned **hvorfor CVR ikke kan være nøglen** med de fire eksisterende produktionsrækker som bevis; plus at der skelnes mellem idempotensnøgle (hvad er samme faktum) og matchnøgle (hvad er samme leverandør), og at forskellen forklares i én sætning; plus at nøgleskift har et navngivet svar der ikke er "det sker ikke" — typisk tombstone plus ny nøgle plus en eskalering, med det forventede antal tilfælde pr. år |

### K5 — Anti-corruption layer og kildepræcedens pr. felt (vægt 2)

*Findes fordi:* to kilder er uenige, og et system uden en skreven præcedensregel afgør det tilfældigt — i praksis efter hvilken import der kørte sidst.

| Score | Sådan ser det ud |
|---|---|
| 0 | Kildens model læses direkte ind i domænemodellen. Ingen kanonisk model |
| 1 | Kanonisk model findes, men præcedens er ikke angivet, eller er angivet som "nyeste vinder" uden at der findes et pålideligt tidsstempel |
| 2 | Regneark med mindst 18 felter, præcedens pr. felt, og eksplicit skelnen mellem tomt felt og fraværende felt |
| 3 | Ovenstående, plus at præcedensen er begrundet i kildetillid og ikke i rækkefølge; plus at mindst tre felter har **forskellig** præcedens fra resten med en navngiven grund (fx at et manuelt sat kategorifelt slår enhver ERP-kilde, mens adressen altid kommer fra ERP); plus at der findes en regel for hvad der sker når den præcedensgivende kilde har været tavs i mere end N døgn, med N sat |

### K6 — Match, flet og menneskelig eskalering med tærskler i tal (vægt 3)

*Findes fordi:* automatisk sammenfletning af leverandørstamdata er den eneste del af casen der kan lave skade som ikke kan rulles tilbage. Og fordi et eskaleringsdesign uden en dimensioneret kø er en kø der lander i Mettes indbakke igen.

| Score | Sådan ser det ud |
|---|---|
| 0 | Alt matches automatisk, eller matchning nævnes ikke. Fuzzy navnematch foreslået uden tærskel |
| 1 | Tre-fire matchregler beskrevet i ord ("hvis navn og adresse ligner hinanden"), ingen tal, ingen eskaleringssti |
| 2 | Regler med **tal**: mindst tre kandidatregler med en tærskel hver, en auto-flet-zone, en auto-afvis-zone og en gråzone der går til et menneske. Det er navngivet hvem mennesket er, og hvad de ser |
| 3 | Ovenstående, plus et **forventet sagsantal med spænd** for både førstegangsindlæsningen og steady state (fx "190-260 sager ved initial load, ±40 %; 3-8 sager/uge derefter"), plus at flet er defineret som reversibelt — hvad der gemmes for at kunne skille to poster ad igen; plus at eskaleringsnotatet er skrevet så Mette kan bruge det uden at spørge dig; plus at de 63 moderselskabs-CVR'er hos VKI er behandlet eksplicit som en egen kategori |

### K7 — Genafspilningen regnet igennem med spænd (vægt 3)

*Findes fordi:* Jens har lovet den, den er den eneste del af casen med en dato, og den er casens største enkeltrisiko. En genafspilningsplan uden tal er et løfte, ikke en plan.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen tal. "Vi kører filerne igennem igen" |
| 1 | Ét tal, typisk antal filer, uden spænd og uden at antal skrevne rækker adskilles fra antal læste poster |
| 2 | Fire tal med spænd: læste poster, faktisk skrevne rækker, kørselstid, eskaleringer. Forholdet mellem læste og skrevne er regnet ud og kommenteret |
| 3 | Ovenstående, plus at det er sagt højt at over 99 % af genafspilningen skal være no-ops og **hvad det tal beviser hvis det ikke passer** — en afvigelse over en sat tærskel er en afbrydelsesbetingelse, ikke en observation; plus at der er en dry-run-tilstand der producerer tallene uden at skrive; plus at forskellen mellem hvad Jens lovede (1. juni) og hvad der kan leveres, er regnet i antal leverandører og skrevet ned til ham |

### K8 — Prisen på dit eget idempotenslag (vægt 2)

*Findes fordi:* modul 02's niveau 3 stiller præcis dette spørgsmål, og fordi Jens' loft er 900 kr./md. Et lag du ikke kan prissætte, kan du ikke forsvare mod "kan vi ikke bare".

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen omkostningsbetragtning |
| 1 | Kvalitativt: "det koster lidt ekstra i database-kald" |
| 2 | Millisekunder pr. post og ekstra writes pr. post er angivet som tal med spænd, og lagerforbruget for landingszonen er regnet i GB |
| 3 | Ovenstående, plus DKK/md ekskl. moms holdt op mod de 900 kr., plus at der er sagt hvilken post der driver spændet, plus at der er en note om hvad tallet bygger på — et gæt, en analogi fra en tidligere spike, eller en måling — og at gæt er mærket som gæt |

### K9 — Manuelle rettelser: hvad du kan bevise, og hvad du ikke kan (vægt 3)

*Findes fordi:* "det rører ikke jeres eget arbejde i systemet" er allerede sagt til en kunde, og systemet kan i dag ikke holde det løfte. Det er casens ubehagelige midte.

| Score | Sådan ser det ud |
|---|---|
| 0 | Antager at manuelle rettelser kan genkendes, eller nævner dem ikke |
| 1 | Nævner at manuelle rettelser skal beskyttes, men foreslår en løsning der forudsætter data der ikke findes |
| 2 | Konstaterer at feltniveau-proveniens ikke findes i dag, og adskiller klart to spørgsmål: hvordan vi beskytter rettelser **fremad**, og hvad vi kan gøre ved de rettelser der allerede ligger der uden spor |
| 3 | Ovenstående, plus en konkret model for proveniens fremad (kilde og aktør pr. felt, ikke pr. række) med en note om hvad den koster i skema og skrivetid; plus mindst ét forslag til at redde det bagudrettede der ikke er "vi kan ikke" — fx en frysning af de felter der oftest rettes i hånden, eller et før-billede taget inden genafspilningen; plus at auditloggens 90 dages retention er nævnt som det der afgør hvor langt tilbage vi overhovedet kan se |

### K10 — Fravalgene afvist på én navngiven, målbar akse (vægt 3)

*Findes fordi:* forskellen på dig og en arkitekt er ikke at han kender flere mønstre. Det er at han kan sige hvad han fravalgte og hvad fravalget kostede.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen alternativer nævnt, eller de er nævnt og afvist uden begrundelse |
| 1 | To alternativer nævnt, afvist med adjektiver ("for komplekst", "overkill") |
| 2 | To alternativer afvist, hver på én navngiven akse med et tal på |
| 3 | Ovenstående, plus at mindst ét af de afviste er et alternativ kandidaten **selv ville have valgt** under en anden præmis, og at præmissen er navngivet; plus at ingen af de to er afvist på to akser samtidig, fordi to akser betyder at man ikke har valgt hvilken der bar beslutningen |

### K11 — Faldsbetingelsen (vægt 3)

*Findes fordi:* et dokument uden et afsnit om hvad der ville få os til at ændre beslutningen, er en begrundelse, ikke en beslutning.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen faldsbetingelse |
| 1 | Én betingelse, formuleret uden tærskel ("hvis volumen bliver meget større") |
| 2 | Tre betingelser, hver med en tærskel og en enhed (rækker/nat, procent eskaleringer, kroner/md, antal kilder) |
| 3 | Ovenstående, plus at mindst én betingelse er formuleret så den kan **måles automatisk** af noget der allerede findes eller er billigt at bygge; plus en navngiven ejer pr. betingelse; plus at kandidaten efter præmisskiftet selv konstaterer om en af dem er udløst — og handler på det |

### K12 — Iteration ved præmisskiftet (vægt 3)

*Findes fordi:* det er det eneste kriterium der måler adfærd i stedet for artefakt, og det er det en interviewer lytter efter.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forsvarer det oprindelige design. Sætningen "mit design holder faktisk stadig, hvis man ser på det sådan her" optræder i en eller anden form |
| 1 | Erkender at noget skal laves om, men laver alt om — inklusive de dele skiftet ikke rører |
| 2 | Opdaterer genafspilningsplanen og mindst ét andet tal inden for 45 minutter, og siger hvad der **ikke** ændrer sig |
| 3 | Ovenstående, plus at rangordningen er ændret eksplicit på grund af Thomas' tre dage — hvad der bygges før den 28. og hvad der udskydes, med konsekvensen af udskydelsen skrevet ned; plus at der er formuleret én sætning Jens kan sige til Anne-Mette om de manglende nitten dage, som hverken lyver eller trækker noget tilbage |

### Bestået, og hvad "stærk" kræver

- **Bestået: 60 af 99 point**, og ingen af K1, K4, K7 og K12 under 2. En kandidat der scorer højt på mapping og lavt på K7 har lavet et pænt designdokument til et problem der har en dato.
- **Kompetent: 60-77 point.** Designet er forsvarligt, tallene findes, og en anden udvikler kan bygge efter det.
- **Stærk: 78+ point**, med 3 på mindst fem kriterier, herunder **K10 og K11**. Stærk kræver desuden to ting der ikke kan spilles: at mindst ét af de fjorten skjulte svar har fået kandidaten til at rive noget op han allerede havde skrevet, og at det er dokumenteret hvad og hvornår.
- **Automatisk dumpet**, uanset pointsum: hvis designet fletter leverandørdata på tværs af de tre tenants. Det er ikke en teknisk fejl, det er et brud på databehandleraftalen, og det er den ene fejl i casen som ingen af de andre kriterier kan opveje.

## Kalibrering: skriv dette ned FØR du går i gang

Fem forudsigelser. Skriv dem i en fil, gem den, rør den ikke før timeboxen er slut.

1. **Hvor stor en andel af de 92 genafspillede filers poster ender som faktiske skrivninger?** Skriv ét procenttal nu, før du har læst ét eneste svar i tabellen over skjulte oplysninger.
2. **Hvor mange af dine kravsspørgsmål bliver besvaret med noget der reelt ændrer designet?** Skriv et tal mellem 0 og 14.
3. **Hvor mange menneskeeskaleringer giver førstegangsindlæsningen af VKI's 2.180 rækker?** Skriv ét tal og ét spænd, fx "150 sager, ±50 %". Efterprøves mod din egen matchregel til sidst.
4. **Hvor mange af de otte timer går til match- og fletteregler?** Skriv et tal med én decimal. De fleste skriver 1,0 og bruger 2,5, fordi det er den eneste del uden et facit.
5. **Hvad bliver sværest?** Én sætning, maks. 15 ord.

**Hvad var jeg sikker på og tog fejl om** — udfyldes efter timeboxen, mindst tre linjer, hver af formen "jeg troede X, det var Y, årsagen var Z". Er feltet tomt, er kalibreringen dumpet — ikke perfekt. En kandidat der ikke tog fejl om noget på otte timer i et problem hvor fire af fjorten oplysninger vælter en oplagt løsning, har ikke undersøgt problemet.

## Modelbesvarelsens omrids

**LÆS FØRST EFTER FORSØG.** Ikke et facit. Et omrids af hvad en stærk besvarelse indeholder, og hvilke veje der er forsvarlige.

**Tre forsvarlige veje**

- **A. Landingszone plus indholds-hash som ændringsdetektor.** Alt der ankommer gemmes uændret med hash og tidsstempel. Pr. kilde beregnes en hash over de felter der indgår i det kanoniske billede; er hashen uændret, er posten et no-op og koster ét opslag. Idempotensnøgle (tenant, kildesystem, kildenøgle), hvor kildenøglen er LIFNR+BUKRS for SAP, entitets-id for Dynamics, og en syntetisk nøgle for VKI fordi deres eksport ikke har en. Løser det fulde nattelige udtræk og genafspilningen med det samme, uden at kunden skal ændre noget. Falder på ét punkt: hashen fortæller at noget ændrede sig, ikke hvornår det ændrede sig hos kunden — så ude-af-orden fra Dynamics kræver et separat svar.
- **B. Monoton versionsstempling pr. kilde plus feltniveau-merge.** Hver kilde får sit eget versionsbegreb: rowversion pr. company for Dynamics, filens sekvensnummer plus linjenummer for SAP og VKI. En ældre version overskriver aldrig en nyere for samme felt. Dyrere i skema og i skrivetid, men det eneste der løser Dynamics' 1,6 % ude-af-orden korrekt uden at hælde alt gennem en ordnet kø. Kræver at man skriver ned hvad "nyere" betyder, når to kilder har hver sit versionsbegreb — og det er svaret der adskiller.
- **C. Kilden som sandhed, med manuelle rettelser som et separat lag ovenpå.** ERP-data skrives til en kildetro tabel pr. kilde og ændres aldrig af mennesker; det kanoniske leverandørbillede beregnes som kilde plus et lag af menneskeskrevne overrides med egen proveniens. Dyrest i skema og i frontend, men den eneste af de tre hvor Jens' mundtlige løfte til Anne-Mette bliver sandt af konstruktion, og hvor en genafspilning per definition ikke kan ødelægge noget. Forsvarlig, hvis du kan vise at den kan bygges i etaper og sige hvilken etape der når den 28.

Alle tre er forsvarlige. Den urimelige er kun én: at bruge CVR som idempotensnøgle fordi Thomas sagde det.

**Hvad en stærk besvarelse desuden indeholder**

- Volumentallet er 4.140 aktive eller 8.910 juridiske enheder — ikke 12.000 — og der står hvorfor, i én linje.
- Det er sagt eksplicit at det nattelige SAP-udtræk er et fuldt udtræk, og at hver nat derfor allerede **er** en genafspilning. Den erkendelse gør Jens' løfte teknisk billigere og fagligt vanskeligere på samme tid.
- Idempotensnøgle og matchnøgle er to forskellige ting med to forskellige formål, og forskellen er forklaret uden jargon.
- Kravet om et globalt leverandørindeks er afvist med henvisning til § 5.2, og Hydra-Tech-eksemplet er brugt til at vise at samme firma i to tenants er to leverandører — plus én sætning om hvad Jens' benchmarkidé ville kræve før den kan bygges.
- Mindst to krav er besvaret med et nej og et prisskilt: ændringstidsstempel fra SAP (kræver Kvadrant og kalendertid, ikke arkitektur) og catch-up efter Dynamics' 19-timers hul (kræver enten en pull-kilde eller 4-6 ugers leveringstid hos Fokus til 1.150 kr./time).
- Fravær er behandlet som tre forskellige ting, ikke én: fravær i en fuld fil, fravær i en delta, og fravær i en webhook-strøm. Kun det første kan betyde noget.
- Fund undervejs der ikke stod i opgaven, men som en der læste systemet ville finde — for eksempel at der ikke findes en dead letter overhovedet i dag, at try/catch-loopet betyder at en fejlet række aldrig kommer igen, og at 3. juli-hændelsen derfor ikke var et uheld men den forventede adfærd.

**Hvad der adskiller den stærke fra den kompetente**

| Den kompetente | Den stærke |
|---|---|
| Vælger en idempotensnøgle | Vælger en nøgle **og** skriver hvad der sker den dag Nordhavn omnummererer en company code, med et antal berørte leverandører |
| Skriver at manuelle rettelser skal bevares | Konstaterer at systemet i dag ikke kan se forskel, og leverer både en model fremad og et før-billede bagud |
| Prissætter idempotenslaget | Prissætter det, siger hvilken post der bærer spændet, og mærker sine gæt som gæt |
| Beskriver matchregler | Dimensionerer den menneskelige kø i sager pr. uge og spørger om Mette har tid til den |
| Nævner at Jens har lovet noget | Skriver den sætning Jens kan sige tirsdag, og siger hvad der sker hvis han ikke siger den |
| Laver designet om efter præmisskiftet | Siger også hvad der **ikke** ændrer sig, og rangordner hvad der når den 28. |

## Sådan ser en dårlig besvarelse ud

Skrevet som du selv ville formulere det. Formålet er genkendelse, ikke skam.

1. *"Vi bruger CVR som nøgle, det er jo den entydige identifikation af et dansk firma."* — Du har lige lagt fire produktionsleverandører sammen med deres moderselskaber, og efter indlæsningen 170-220 til. Ingen opdager det med det samme, fordi de sammenlagte rækker ser rigtige ud. Det opdages den dag en auditrapport hænger på den forkerte enhed.
2. *"Vi slår duplicate detection til på Service Bus, så er dubletterne løst."* — Den virker på MessageId i et 10-minutters vindue. Dit problem er forretningsniveau over tre måneder, og du har i øvrigt ikke Service Bus i abonnementet. Du har genkendt et navn, ikke løst et problem.
3. *"Jeg tager det nyeste tidsstempel og lader det vinde."* — SAP sender ikke et ændringstidsstempel, og det tidsstempel der er, er ens for alle poster i samme kørsel. Du har bygget en konfliktløsning på et felt der ikke findes, og den vil se ud som om den virker indtil to kilder er uenige.
4. *"Vi beder bare kunden om at rette CVR-feltet i eksporten."* — Ove er halvtids og går på pension den 31. december, Mette har allerede lovet dem at de ikke skal ændre noget, og efter præmisskiftet kan Kvadrant heller ikke røre SAP før februar. Det er ikke et design, det er et ønske sendt videre.
5. *"Vi laver ét globalt leverandørindeks, så kan vi også lave benchmarking senere."* — Du har brudt § 5.2 i tre databehandleraftaler for at spare et join, og du har gjort det i den fase hvor det er lettest og hvor ingen siger fra. Casen dumper her uanset resten.
6. *"Genafspilningen kører bare filerne igennem igen, idempotenslaget klarer resten."* — Måske. Men du har ikke skrevet hvor mange rækker der forventes skrevet, så du kan ikke se forskel på at det virkede og at det overskrev alt. Og du har ikke opdaget at nitten dage af de tre måneder ikke findes.
7. *"Match-scoren skal være høj nok, ellers går den til manuel gennemgang."* — "Høj nok" er ikke et tal, "manuel gennemgang" er ikke en person, og du har ikke spurgt hvor mange sager Mette kan tage om ugen ved siden af tre onboardings. Køen findes allerede — den hedder hendes indbakke.
8. *"Præmissen ændrede sig, men egentlig havde jeg jo taget højde for det."* — Det er forsvar. Det er også præcis den sætning en interviewer lytter efter, og den eneste der ikke kan bortforklares bagefter.

## Hvor i materialet svaret står

Ubarmhjertig version. To kriterier er ikke dækket af noget modul, og det er et fund i materialet, ikke i casen.

| Kriterium | Modul | Præcis sektionsoverskrift | Hvad du henter der |
|---|---|---|---|
| **K1** Kravsspørgsmål før første feltnavn | 01 | `### Øvelse 3: Trade-off-kata på tid` | Kravet om mindst otte kravsspørgsmål stillet før første diagram, timeboxen, og selvkontrollen til sidst |
| **K2** Spørgsmålene rammer de dyre akser | 10 | `## Kvalitetsattribut-scenarier: din del af kravarbejdet` | Den seksdelte form og reglen om at responsmålet altid er et tal. Suppl.: 01 `## Kompetencemodellen: ti akser`, rækken om kravsfremdragelse og NFR med tal |
| **K3** Leveringssemantik og fejlejerskab pr. kilde | 04 | `## Det foerste reelle valg: hvordan data kommer ind` | Tabellen over de fem integrationsstile med latens, kobling og fejlejerskab, og sætningen "du vaelger ikke transport, du vaelger hvem der ejer fejlen". Suppl.: 04 `## Leveringssemantik: at-least-once er praksis` for exactly-once processing og de fire Service Bus-begrænsninger |
| **K4** Idempotensnøglen felt for felt | 04 | `## Leveringssemantik: at-least-once er praksis` | "Idempotensnoeglen skal vaere en business key, ikke et message-id", eksemplet med to kanaler og to message-id'er, og det svære spørgsmål: hvad sker der når kunden ændrer et felt der indgår i nøglen. Suppl.: 09 `### Spike 2: Idempotent indlæsning af leverandørstamdata fra N ERP-systemer (30-35 t)` for nøglen (tenant, kildesystem, kildenøgle) og for at SAP-vendornummeret er unikt pr. company code |
| **K5** Anti-corruption layer og kildepræcedens | 04 | `## Moenstervokabularet` | Rækkerne Anti-Corruption Layer, Raw landing zone og Canonical model, med domæneeksemplet SAP + Business Central + CSV-kunde til én leverandørrepræsentation. Suppl.: 09 `### Spike 1: Certifikatgyldighed som tilstandsmaskine (20-25 t)` for præcedensmodellen over tre kilder og `source_trust_level` |
| **K6** Match, flet og menneskelig eskalering | — | **IKKE DÆKKET** | Materialet har kildepræcedens (09, spike 1), menneskelige eskaleringspunkter i en saga (04 `## Fire spikes med fysisk output`, spike D) og en entitetsmodel med ejerskabshierarki (09 `## Ressourcetabel`, GLEIF- og OpenSanctions-rækkerne). Der mangler **entitetsopløsning som målt disciplin**: blocking, similaritetsmål, tærskler for auto-flet mod manuel gennemgang, hvordan man måler præcision og recall på sin egen matchregel, hvad reversibel flet kræver i datamodellen, og hvordan man dimensionerer den menneskelige kø i sager pr. uge. Det er casens sværeste kriterium og materialets største hul |
| **K7** Genafspilningen regnet igennem | 04 | `## Fire spikes med fysisk output` (spike A og spike C) | Spike A's krav: ingen dubletter, ingen tabte opdateringer, genstart fra vilkårligt punkt, bevisførelse for hvad du modtog hvornår — og outputkravet om målt dublet- og tabsrate før og efter idempotenslaget. Spike C giver replay-CLI med filter på tenant og tidsrum plus målt tid-til-diagnose. Suppl.: 09 `### Spike 2: Idempotent indlæsning af leverandørstamdata fra N ERP-systemer (30-35 t)` for kravet om at ti gentagne afspilninger giver identisk sluttilstand |
| **K8** Prisen på dit eget idempotenslag | 02 | `## Selvvurdering: tre niveauer med spørgsmål du ikke kan bluffe dig igennem` | Niveau 3, spørgsmålet "Kan du sige prisen på dit eget idempotenslag i millisekunder og i ekstra database-writes?". Suppl.: 03 `## Budgetloftet: 400 DKK/md, hård alert ved 600` for prissætningsdisciplinen, og 04 `## Priser` for Service Bus- og MassTransit-posterne |
| **K9** Manuelle rettelser og proveniens | — | **IKKE DÆKKET** | Materialet har feltniveau-**merge** (09 `### Spike 2: Idempotent indlæsning af leverandørstamdata fra N ERP-systemer (30-35 t)`), append-only revisionsspor og bitemporal modellering (09 `## Problemkataloget: hvad der faktisk er svært i domænet`) og persondata i telemetri (06 `## Persondata i telemetri: her mødes faget og domænet`). Der mangler **aktør-proveniens pr. felt**: at kunne se om et felt sidst blev sat af et menneske eller af en import, reglen for hvornår en automatisk kilde må overskrive et menneskeskrevet felt, og — vigtigst — hvad man gør når proveniensen ikke findes i det eksisterende skema og en genafspilning er lovet om fjorten dage |
| **K10** Fravalg på én målbar akse | 07 | `### G5 — ADR-serie om lejerisolation i dokumentlageret (måned 3-4, 1 uge, parallelt)` | Kravet om mindst to ADR'er med navngivne afviste alternativer. Suppl.: 04 `## Saadan ved du at du kan det`, punkt 9: fire ADR'er med navngivne fravalgte alternativer; og 02 `## Spikes: fysisk output, ellers talte det ikke` (spike 4's krav om at dokumentere de indeks du fravalgte) |
| **K11** Faldsbetingelsen | 09 | `## Sådan ved du at du kan det` (rækken "ADR-tællingen") | "Hvert dokument har et afsnit om hvad der ville få os til at ændre beslutningen. Mangler det, er det en begrundelse, ikke en beslutning." Suppl.: 04 `## Saadan ved du at du kan det`, punkt 9's eksplicitte ombestemmelsesbetingelse, og 04 `## Nedbrydning: modulaer monolit er defaulten` for formen "tærskelværdier, ikke fornemmelser" |
| **K12** Iteration ved præmisskift | 01 | `## Sådan ved du at du kan det` | Andet punkt: "Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse." Suppl.: 01 `### Øvelse 3: Trade-off-kata på tid`, afsnittet om den eksterne der ændrer en præmis efter fire timer, og 10 `## Shape Up, og aldrig et nej uden prisskilt` for tredelingen "det koster X" / "80 procent for Y" / "genvejen tillades og datosættes" |

## Ekstern kalibrering

Din egen score er værdiløs alene, og en kollega i et ni-mandsfirma tæller halvt — særligt her, hvor Thomas er den eneste der kender importeren og allerede har sagt hvad han mener. Mindst to af disse skal have givet **skriftlig** kritik, før casen tælles som gennemført. Spørg hver om én ting, ikke om en helhedsvurdering.

| Hvem | Hvor du finder dem | Det konkrete spørgsmål |
|---|---|---|
| SAP-integrationskonsulent (Kvadrant-typen: en fra et SAP-partnerhus eller en freelancer med ECC-baggrund) | LinkedIn, dansk SAP-brugerforening, eller den partner en af jeres egne kunder allerede bruger; 30 minutter | "Her er min idempotensnøgle for et CREMAS-flow uden ændringstidsstempel. Hvad går galt hos jeres kunder, som jeg ikke har taget højde for?" |
| Integrationsarkitekt fra et dansk konsulenthus (Netcompany, twoday, Trifork, Fellowmind, Devoteam) | ANUG- eller GOTO-meetup i Aarhus; bed om 30 minutter efter oplægget | "Læs mine tre leveringssemantikker. Hvilken af dem ville du sige jeg har taget for let på, og hvad koster det når det går galt?" |
| Data quality- eller MDM-specialist | Den eneste hvor du skal uden for dit eget netværk — en fra et MDM-produkthus eller en dataarkitekt i en større indkøbsorganisation | "Her er mine matchregler og mine tærskler. Hvor mange falske positive tror du de giver på 2.180 danske leverandørrækker, og hvordan ville du måle det?" Dette er spørgsmålet materialet ikke kan hjælpe dig med |
| Indkøbs- eller kvalitetschef hos en eksisterende kunde | Gennem en onboarding du alligevel sidder med; indramning: "jeg vil gerne vide om det her ville holde hos jer" | "Hvis vi flettede to af jeres leverandører sammen ved en fejl, hvornår ville I opdage det, og hvad ville det koste jer?" |
| Mentor med integrationstung SaaS-baggrund | ADPList, 30 minutter, book to i tilfælde af aflysning | "Angrib min genafspilningsplan, ikke mit diagram. Hvilket af mine fire tal er mest forkert?" |
| Code review-byttepartneren | Den udvikler i et andet firma du har fast kadence med fra måned 3 | "Læs mine to fravalg. Kan du argumentere mig ned på ét af dem?" |

Notér for hver: hvad de sagde, hvad du ændrede, og hvad du valgte at lade stå — plus hvorfor. Den tredje kolonne er den, en kommende arbejdsgiver spørger ind til.
