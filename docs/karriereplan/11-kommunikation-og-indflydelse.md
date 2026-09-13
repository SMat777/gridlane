# 11. Kommunikation og indflydelse: færdigheden der afgør alt

> Du har ingen arkitekt på kontoret, intet review board og ingen titel at læne dig op ad. Til gengæld er afstanden fra dit tastatur til stifterens skærm nul: et godt dokument bliver læst samme dag. Skriftlighed er den eneste arkitektkompetence du kan træne uden tilladelse, uden budget og uden mandat — og den eneste kanal der kan hente det modspil ingen af dine otte kolleger kan give dig. Uden det modspil kan du øve dig forkert i tolv måneder uden at opdage det.

## Beslutningen er kommunikationen

Arkitektur er ikke teknik med et kommunikationsvedhæng ovenpå. En beslutning som ingen forstod, ingen kan finde igen om 18 måneder, og ingen kunne argumentere imod, er ikke arkitektur — det er en tilfældighed der overlevede. Måleenheden er artefakter, ikke timer.

Én regel binder resten sammen: **hvert artefakt får en navngiven modtager, et konkret spørgsmål og en dato, før du skriver.** Ikke "jeg lægger det i repoet". Uden det bygger du et ekkokammer med versionsstyring, og det ligner succes indtil måned 12.

## Den ugentlige skrivepraksis — start mandag

Cirka fire timer om ugen af loftet på 10-15; resten går til kode, spikes og certificeringer.

| Kadence | Artefakt | Tid | Navngiven modtager |
|---|---|---|---|
| Efter hvert teknisk møde | Referat: beslutninger, åbne spørgsmål, hvem gør hvad hvornår, sendt inden for en time | 3 x 15 min | Alle deltagere |
| Mandag, fast blok | Én side i SCQA-form om ugens vigtigste tekniske spørgsmål | 60 min | Stifteren |
| Hver anden uge | Ét diagram, timeboxet og blindtestet | 60 min | Førstegangslæser |
| 1-2 gange månedligt | ADR skrevet før beslutningen | 60-90 min | Den mest erfarne udvikler |
| Månedligt, kalenderaftale | Ét dokument til eksternt review | 90 min | Mentor eller en kundes IT-arkitekt |
| Kvartalsvis | Ét design doc, ét indlæg, én faciliteret session | ca. 22 t | Skiftende, altid navngivet |

Mandagsblokken er mekanikken: en time, ingens tilladelse, og efter otte uger tredive siders skriftlig tænkning om platformen som ingen anden i firmaet har.

## Fem formater, og hvornår hvert bruges

| Format | Bruges når | Længde | Afgørende detalje |
|---|---|---|---|
| **ADR** (MADR minimal) | Beslutningen er dyr at rulle tilbage: tenant-isolation, revisionssporets datamodel, retention | 1-1,5 side | Skrives før beslutningen, med Decision tom |
| **Design doc** (Google) | Et arbejde over en uge skal defineres, ikke planlægges | 3-5 sider | Non-Goals og Alternatives Considered før Actual Design |
| **RFC** (Oxide-stil) | Der findes ingen rigtig løsning, kun forskellige tab — fx GDPR-sletning under legal hold | 2-3 sider | "Open questions" skrives først og gøres lang |
| **Narrativ / seks-sider** | Beslutningen tilhører stifteren og handler om penge | Maks 6 sider | Nul bullets i brødteksten, tal i appendix |
| **Architecture Haiku** | Du skal destillere platformen | Én side | Rangordnede quality attributes — noget skal stå sidst |

Tærsklen betyder mere end skabelonen. Under 20 ADR'er på et år i et firma på ni er sundt; 60 er et symptom. Skriver du dem for hvert bibliotekvalg, orker ingen at læse dem.

## Diagrammer: brug C4 halvt

Level 1 (System Context) og Level 2 (Container) bærer 90 procent af værdien. Level 3 rådner hurtigst, fordi koden ændrer sig under det, og Level 4 tegner du aldrig i hånden. Værktøjsvalget er afgjort, og du bruger ikke mere tid på det:

- **Structurizr Lite i Docker** med `workspace.dsl` i git ved siden af koden: `docker run -it --rm -p 8080:8080 -v /sti/til/mappe:/usr/local/structurizr structurizr/lite`. **Opret ikke en cloud-konto** — den tjeneste lukker 30. september 2026 og har været read-only siden 1. juli 2026. Enhver guide der siger "opret en konto på structurizr.com" er forældet.
- **Mermaid `sequenceDiagram`** i pull requests, fordi den renderes direkte i GitHub uden byggetrin. Over cirka et dusin noder bliver layoutet rodet; der skifter du til Structurizr DSL.
- **PlantUML** kun ved konkret behov for rigtig UML, typisk en state machine for en kvalificerings-livscyklus (draft, under review, godkendt, udløbet, spærret). Ellers ikke.

Den hårdeste test er gratis: giv diagrammet til en der aldrig har set systemet, sig intet, og bed dem forklare hvad de ser. Alt de misforstår er en fejl i diagrammet.

## Oversæt til kroner og risiko

Over for en stifter med ansvar for runway har "teknisk gæld", "kvalitet" og "ikke skalerbart" ingen plads; de læses som "udvikleren vil rydde op". Fire enheder virker, og enhver teknisk påstand oversættes til én af dem før den siges højt: kroner per måned; timer per måned brugt manuelt; sandsynlighed for at tabe en konkret handel; sandsynlighed for at fejle en kundes audit eller sikkerhedsgennemgang.

Enhed fire er din stærkeste, fordi den er markedet. NIS2 har været i kraft i dansk ret siden 1. juli 2025, artikel 21 stiller krav til leverandørkædesikkerhed, og tilsynet skalerer op i 2026. Byg aldrig argumentet på CSDDD i år: Omnibus I (Direktiv (EU) 2026/470) indsnævrede omfanget til over 5.000 ansatte og 1,5 mia. EUR og flyttede anvendelsen til 26. juli 2029.

Præsentér aldrig én løsning. En stifter der kun får ét forslag, kan kun sige ja eller nej, og så handler samtalen om tillid til dig i stedet for om sagen. To-tre muligheder med pris, tid og risiko, plus en klar anbefaling. Formen til en side: "Vi har X i dag. Problemet er Y. Spørgsmålet er hvordan vi Z. Mit svar er A, det koster B, alternativet C koster D."

## Uenighed skrives, den tales ikke

Mundtligt vinder den mest selvsikre stemme og den med flest års anciennitet. Skriftligt og asynkront vinder det bedste argument oftere, fordi læseren kan tænke uden at skulle svare med det samme. Standardtrækket: "Jeg skriver en halv side med de to muligheder og hvad jeg tror vi risikerer ved hver — kan du rette hvor jeg tager fejl?" Det er taktisk, ikke konfliktsky, og der bliver et artefakt uanset udfaldet.

**Steelman før dit eget argument:** skriv modpartens position så stærkt du kan, før du skriver din egen. Og **tab pænt, skriftligt:** når du tager fejl, skriver du selv opdateringen med hvad der overbeviste dig. Efter tredje gang giver folk dig ærlig feedback i stedet for høflig, og dét er forskellen på at øve rigtigt og forkert.

## Facilitering i miniature

| Format | Varighed | Mekanikken der ikke må springes over |
|---|---|---|
| Risk storming | 90 min | Individuel, tavs skrivning af risici før nogen siger noget |
| Design review | 45 min | Dokument rundsendt 48 t før, første 10 min stille læsning, resten kun spørgsmål |
| Blameless postmortem | 60 min | Faktatidslinje først, ingen navne i årsagsbeskrivelsen, handlinger med ejer og dato |

Alle tre kan du foreslå i morgen uden mandat. Måleenheden kan ikke snydes: **taletid.** Taler du over 30 procent i en session du faciliterer, holdt du foredrag. Lad en kollega tælle, eller optag og mål; første gang bliver det over 60 procent, og det er data. Øv én omformuleringssætning på forhånd: "lad os holde det ved hvad systemet gjorde muligt".

## Offentlig skrivning er ikke branding

Formålet er kvalificeret modspil fra fremmede: et indlæg skrevet for at få likes lukker af for kritik, mens et der siger "her er hvad jeg tror er svagest ved min egen løsning" åbner for den.

Fire indlæg på tolv måneder, ikke fyrre, hvert på 1.200-2.000 ord på engelsk. Rytme: uge 1 udkast, uge 2 hvile, uge 3 skær 30 procent og udgiv. Distribution er obligatorisk: post i Virtual DDD Discord med et konkret spørgsmål, foreslå det til Architecture Weekly, og send det direkte til to-tre navngivne fagfolk. Én direkte henvendelse giver mere kritik end tusind visninger.

Emnerne kommer fra det du sidder i: NIS2 artikel 21 oversat til datakrav i et SaaS-produkt; sletning under GDPR når et revisionsspor er i legal hold; idempotent stamdataindlæsning fra ERP uden stabile id'er; hvad multi-tenant isolation koster når hver tenant har sit eget compliance-regime. Sikkerhedsregler: ingen kundenavne, ingen produktionsskærmbilleder, ingen rigtige datamængder, og alt der nævner arbejdspladsen ses af stifteren først. Skriv om **problemklassen**, aldrig om kunden.

## Ressourcer

| Ressource | Prioritet | Tid | Hvorfor |
|---|---|---|---|
| Simon Brown, *The C4 Model* (O'Reilly 2026, 177 sider) | P0, uge 1-2 | 5-6 t | Kanonisk kilde. Læs den før du tegner noget |
| Diagram review checklist, c4model.com/diagrams/checklist | P0, uge 1 | 20 min + 3 min/diagram | Skiller "imponerer" fra "forklarer" |
| Structurizr Lite (Docker) | P0, uge 2 | 3 t | Model som kode i git. Kun Lite |
| Google Technical Writing One + Two (gratis) | P0, uge 3-5 | 6-8 t | Billigste målbare løft i planen |
| Malte Ubl, *Design Docs at Google* | P0, uge 3 | 40 min | Strukturen du stjæler direkte |
| MADR, minimal-varianten | P0, uge 2 | 30 min | Tvinger afvejningen frem |
| Virtual DDD + deres Discord | P0, fra måned 2 | 30 min/post | Post inden for to uger; passiv læsning giver nul feedback |
| Risk storming + Google SRE Book kap. 15 | P0/P1, måned 3-5 | 3 t | Din første facilitering, og postmortem-mekanikken |
| Jacqui Read, *Communication Patterns* | P1, måned 2-3 | 6-8 t | Patterns og antipatterns i arkitektkommunikation |
| Oxide RFD 1 + fire rigtige RFD'er | P1, måned 2 | 3 t | Sådan ser et rigtigt beslutningsdokument ud |
| Amazons seks-sider og PR/FAQ | P1, måned 3 | 45 min | Formatet, ikke litteraturen |
| Keeling, *Design It*, kun aktivitetskataloget | P1, efter behov | 15 min/aktivitet | Faciliteringsopskrifter til tre-fem personer |
| Architectural Katas (+ nealford.com/katas) | P1, fra måned 3 | 90 min hver 2. uge | Reps under tidspres, kritik fra fremmede |
| Meetups i Aarhus, som **taler** | P1, fra måned 3 | 6-8 t | Værdien ligger i spørgsmålstiden |
| Architecture Weekly | P2, løbende | 20 min/uge | Kalibrering og et falsificerbart publiceringsmål |

**Spring over i år:** Hohpes *Software Architect Elevator* (elevatoren har én etage her; tag idéerne fra hans gratis essay på en time), TOGAF, ArchiMate, stakeholder-matricer, RACI, ADR-CLI'er, IcePanel, Miro-licenser og betalte EventStorming-kurser. GOTO Copenhagen (28. sept. - 2. okt. 2026) kun hvis firmaet betaler — spørg stifteren, det er ét spørgsmål.

## Fire spikes med fysisk output

**A. ADR'en der blev skrevet før beslutningen: certifikatudløb og varslingsvinduer.** Hvor hører varslingslogikken hjemme, og hvordan er den tidsstyret — natlig batch, en kalkuleret `next_notification_at` med index, eller planlagte beskeder i en kø ved oprettelse? Alle tre virker på 100 certifikater. Ved en million, med flere tidszoner, bagudrettede regelændringer (30 til 60 dages varsel) og krav om at kunne bevise at varslingen blev sendt, opfører de sig vidt forskelligt. **Output:** én ADR på maks 1,5 side i `/docs/adr` med tre Considered Options med konkrete pros og cons, ét Mermaid sequenceDiagram for den bagudrettede regelændring, og en git-log der viser commit før implementeringsstart. Ændrede feedback dit valg, skriver du det eksplicit: "Oprindeligt foreslog jeg X; efter kommentar fra N valgte vi Y fordi Z." **Tid:** 4-5 t, heraf mindst 24 timers ventetid hvor du ikke forsvarer noget.

**B. Seks-sideren til stifteren: hvad et append-only revisionsspor koster og hvad det køber.** Kunderne skal kunne bevise hvem der godkendte hvilken leverandør på hvilket grundlag hvornår, og at posten ikke er rørt bagefter. Beslutningen tilhører stifteren; din opgave er at gøre den mulig at træffe på 35 minutter. **Output:** maks seks sider ren prosa, nul bullets i brødteksten, konklusion i første afsnit, tre navngivne muligheder med udviklingstid i uger, driftsomkostning i kroner per måned per kunde, og effekten på risikoen for at fejle en kundes sikkerhedsgennemgang. Én anbefaling, tal i en appendix-tabel, plus en énsiders FAQ. **Fremgangsmåde:** hent de faktiske tal først; skriv første udkast med bullets og omskriv hvert til hele sætninger, for alt der ikke overlever omskrivningen var ikke et argument; bed om 40 minutter og foreslå at de første 15 er stille læsning. **Tid:** 10-12 t over tre uger.

**C. Den kundevendte arkitekturbriefing: "hvordan er vores data adskilt fra andres?"** En større kunde er ved at købe, og deres sikkerhedsansvarlige spørger om isolationsmodel, kryptering, intern adgang, geografi og hvad der sker ved opsigelse. **Output:** ét C4 Container-diagram tegnet fra bunden til en ekstern, sikkerhedsorienteret læser — ikke ved at slette bokse fra det interne. Én side prosa. De ti spørgsmål du forventer, med svar du kan stå inde for, heraf mindst ét "det gør vi ikke i dag, og her er hvorfor". En 10-minutters mundtlig version prøvet på en kollega der skal afbryde. Efter mødet: listen over de spørgsmål du **ikke** forudså. Tre udbytter på samme timer: portefølje, salgsmateriale og adgang til en kundes arkitekt — den seniorprofil der ikke findes i Skejby. **Tid:** 6-8 t.

**D. Diagram-kata: tyve gentagelser.** Ét diagram hver anden uge, timeboxet til 60 minutter — halvdelen over de faktiske systemer (dokumentlagring, kvalificeringsflow, integrationer mod kunders ERP, tenant-isolation), halvdelen fra katas. Protokol: angiv hvem læseren er, kør checklisten selv, blindtest og notér hver misforståelse ordret, ret **diagrammet** og ikke personen. **Output:** ét repo med tyve daterede mapper med målgruppe, blindtestnoter og rettet version. Progressionen fra rodet til klart er stærkere dokumentation end ét pænt diagram. **Tid:** ca. 30 t.

## Faldgruber

- At oprette en Structurizr cloud-konto (den lukker 30. september 2026), eller at tegne alle fire C4-niveauer for alt. Komplette hierarkier er prokrastination fra at træffe beslutninger.
- ADR'er skrevet efter beslutningen: det er ikke arkitektur, det er referat. Og ADR-spam på hvert bibliotekvalg dræber praksissen.
- At forvente at et dokument bliver læst fordi det er godt. "Kan du kigge på det?" giver nul; "jeg er mest usikker på afsnit 3, kan du svare inden torsdag?" giver svar.
- At præsentere én løsning, eller tre uden en anbefaling.
- Enterprise-indflydelseslitteratur: sponsorer, review boards, stakeholder-matricer, architect elevator. Mandat får du ved at spørge stifteren i køkkenet.
- "Strong opinions, loosely held" som selvbillede: det belønner den mest selvsikre stemme. Brug steelman.
- At forveksle rækkevidde med feedback. Fyrre likes er nul modspil; én fremmed der skriver "det holder ikke når X, fordi Y" er udbyttet.
- Ordene "teknisk gæld", "kvalitet" og "ikke skalerbart" over for stifteren.
- Faktafejl i nichen, fx at CSDDD stiller krav fra 2027. Skriv om NIS2 i år. Og læk aldrig kundenavne, produktionsskærmbilleder eller datamængder.
- At tale over 30 procent i en session du faciliterer, eller at springe det tavse trin over fordi det føles akavet.
- Værktøjsjagt: IcePanel, D2, LikeC4, plugins. Ingen af dem løser dit problem, som er at du ikke har skrevet noget endnu.
- At vente på tilladelse til at skrive. Ingen giver den, og det er den fælde der koster flest måneder.

## Sådan ved du at du kan det

- [ ] **Modstandstesten:** tre ADR'er hvor git-historikken viser commit før implementeringsstart, og mindst én hvor Decision blev ændret af feedback, med en sætning om hvem der ændrede din mening.
- [ ] **Genfortællingstesten:** to ikke-tekniske personer læser dit vigtigste design doc i 15 minutter, får det taget fra sig og gengiver problemet, de tre muligheder og prisen på hver.
- [ ] **Blinddiagramtesten:** tyve daterede diagrammer med noterede misforståelser og rettede versioner, og færre misforståelser på de sidste fem end på de første fem.
- [ ] **Forslagstesten:** mindst ét forslag du selv rejste, som ingen bad om, blev accepteret og implementeret, og du kan pege på dokumentet og koden.
- [ ] **Seks-sider-testen:** ét narrativ på maks seks sider uden et eneste bullet, om en reel beslutning med reelle tal, læst i stilhed af beslutningstageren — og det førte til en beslutning. Ja og nej tæller begge.
- [ ] **Taletidstesten:** tre faciliterede sessioner med målt taletid, under 30 procent i to af dem.
- [ ] **Kritiktesten:** fire indlæg udgivet, mindst to indvendinger fra fremmede der peger på et konkret sted hvor løsningen knækker, og ét tilfælde hvor du offentligt ændrede position.
- [ ] **Ekstern-arkitekt-testen:** mindst ét dokument er kommenteret af en med reel arkitekterfaring uden for LeanLinking, og du kan pege på hvad de ændrede i det.
- [ ] **Kundetesten:** du har forklaret en arkitekturbeslutning mundtligt for en rigtig kunde og har listen over de spørgsmål du ikke forudså.
- [ ] **Tabertesten:** to journalposter hvor du tabte, selv skrev opdateringen i dokumentet, og i dag mener det var rigtigt. Har du ikke tabt en eneste uenighed på tolv måneder, har du ikke rejst nogen reelle — eller ingen tør sige dig imod.
- [ ] **Vedligeholdelsestesten:** systemoversigten fra måned 1 er stadig sand i måned 10. Et forældet oversigtsdokument er en negativ score, ikke en neutral.
