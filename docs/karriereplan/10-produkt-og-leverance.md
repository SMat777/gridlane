# 10. Produkt, prioritering og leverance

> Du bliver ikke Product Owner, og du skal ikke forsøge. Med ni ansatte og en stifter der har P&L-ansvaret, er produktbeslutningen ikke et vakuum der venter på proces — den er allerede truffet af én person. Din indgang er smallere og skarpere: at være den der oversætter et arkitekturvalg til en forretningskonsekvens i kroner, uger eller kontraktrisiko. Det er arkitektens produktbidrag. Backlog-administration er det ikke.

## Prioriteringsrammer løser et problem I ikke har

RICE, WSJF og MoSCoW er ikke opfundet for at træffe bedre beslutninger, men for at gøre beslutninger **læsbare** på tværs af mange teams og interessenter. Med tre til fem udviklere og én beslutningstager er læsbarhed ikke flaskehalsen. Hukommelse og konsistens er. Indfører du RICE, ligner du en der lige har læst en bog.

Lær dem alligevel godt nok til at forklare deres svagheder ved en jobsamtale. RICE ganger og dividerer fire usikre tal, så resultatet **ser** præcist ud mens præcisionen er arvet fra estimaterne — og Effort står i nævneren, det tal med kraftigst optimismebias. SAFe's WSJF er ringere: tre Fibonacci-gæt lagt sammen er ikke en kvantificeret cost of delay. Reinertsens pointe var det modsatte — kvantificerer du kun én ting, så kvantificér cost of delay i kroner pr. uge.

Du har brug for to andre ting. **En beslutningslog**, fordi spørgsmålet hos jer ikke er "hvorfor er dette først" men "hvorfor gjorde vi det sådan i 2024, og gælder begrundelsen stadig". Og **et kapacitetsregnskab**: tre til fem udviklere er tre til fem udviklerår om året, så en feature på seks uger er 2-4 procent af årets kapacitet. Spørgsmålet er derfor aldrig "er dette værdifuldt" — alt er værdifuldt — men "**er dette de 6 procent af årets kapacitet værd, sammenlignet med det bedste alternativ**".

## Fra estimat til forecast

Todd Little (IEEE Software, 2006) målte på Landmark Graphics' reelle projekter: estimatnøjagtigheden er **lognormalfordelt**, og usikkerhedsspændet var næsten uændret gennem hele projektet — i modstrid med den populære læsning af "the cone of uncertainty". Flyvbjergs database på 16.000+ projekter viser fat tails og cirka 73 procent gennemsnitlig omkostningsoverskridelse på IT (Flyvbjerg et al. 2022). Konsekvensen: **at kræve "mere analyse før estimatet" løser ingenting.** Kun historiske data gør.

Løsningen er ikke #NoEstimates. At nægte at give en stifter et tal når han skal prissætte en kontrakt er ubrugelighed, ikke raffinement. Skiftet går fra **estimat** (en mening) til **forecast** (en beregning):

| Trin | Handling | Hvornår |
|---|---|---|
| 1 | Kalibreringslog: notér et interval ("2-5 dage") **før** start, faktisk tid bagefter | Uge 1, løbende |
| 2 | Træk 12-24 mdr. leverede issues ud, klassificér i 4-6 domænekategorier: kundetilpasning, ERP-integration, dokument/certifikat, compliance-rapportering, bugfix | Måned 2-3 |
| 3 | Beregn cycle time-fordelingen pr. kategori. Forvent lognormal og lang hale | Måned 3 |
| 4 | Monte Carlo på ugentlig throughput, 10.000 kørsler, udtryk som percentiler | Måned 3-4 |
| 5 | Brug det i tre reelle situationer og **efterprøv** mod hvad der skete | Måned 4-9 |

Mål ikke præcision, mål **kalibrering**: rammer under 60 procent af dine intervaller, er du overmodig; over 90 procent, og de er informationsløst brede. Skriv eksplicit hvornår forudsætningen brækker: ny kunde, ny teknologi, en udvikler ud af tre der fratræder. Byg reference class på **jeres egne** leverancer — metoden er under faglig debat, især om hvad der tæller som "sammenlignelig".

## Teknisk gæld vindes med to tal, aldrig med ordet "refaktorering"

Med 4,2 mio. i bruttofortjeneste og syv årsværk er hver udviklerdag brugt på oprydning en dag der ikke går til en betalende kunde. Stifteren har **ret** i at være skeptisk. **Tal 1 giver dig retten til at stille spørgsmålet:** Tornhill & Borg, "Code Red" (arXiv:2203.04374), 39 produktionskodebaser, 30.737 filer — 15 gange flere defekter, 124 procent længere issue-løsningstid, op til 9 gange længere maksimale cycle times. Nævn selv at forfatterne står bag CodeScene. **Tal 2 vinder argumentet:** hotspot-analyse (churn gange kompleksitet pr. fil) finder de filer hvor pengene brænder, og så måler du forskellen i løsningstid dér kontra resten.

Nuancen der afgør sagen: **argumentér mod variansen, ikke mod gennemsnittet.** De 9 gange længere *maksimale* cycle times er argumentet. Én opgave der tager tre uger i stedet for tre dage, i ugen hvor en stor kunde skal onboardes, er en eksistentiel begivenhed hos jer og en afrundingsfejl i en 500-mands virksomhed.

## Roadmap mod regulatoriske vinduer

Dit domæne har eksterne, datosatte, offentligt verificerbare deadlines der driver kundernes købsadfærd. Et roadmap bygget på dem er hverken ønskeliste eller Gantt-graf — det er et **markedstimingsdokument** som stifteren kan bruge i salget.

| Regulering | Anvendelse | Rammer | Status |
|---|---|---|---|
| **EUDR** | 30. dec. 2026 (store/mellemstore), 30. juni 2027 (små/mikro) | Operatører i afskovningsrelaterede kæder; ny "downstream operator"-kategori | Nærmeste vindue. Udskudt igen dec. 2025 |
| **NIS2 (DK)** | I kraft 1. juli 2025; CFCS aktivt tilsyn 1. halvår 2026 | Ca. 6.000 danske organisationer, plus underleverandører via kontraktkaskade | Aktivt nu. Kaskaden udvider markedet |
| **CSDDD** | Anvendelse 26. juli 2029, implementering 26. juli 2028 | Indsnævret til 5.000+ ansatte **og** 1,5 mia. EUR+ omsætning | Omnibus I, direktiv (EU) 2026/470, i kraft 18. marts 2026 |

**Den mest værdifulde observation du kan bringe ind lige nu:** er salgsmateriale eller roadmap stadig bygget på CSDDD-hastværk, sælger firmaet 2029-omsætning. De nære vinduer er EUDR og de NIS2-leverandørkrav der kaskaderer kontraktuelt i dag. Afsnittet **"hvad vi derfor IKKE bygger nu"** skal fylde lige så meget som resten, og kortet opdateres kvartalsvis.

## Discovery uden discovery-budget

Torres' "product trio" med ugentlige kundeinterviews forudsætter en organisation du ikke er i. Men tre strømme af rå kundevirkelighed findes allerede, og ingen læser dem systematisk: **supporttickets, onboarding-samtaler og stifterens salgsmøder.** Instrumentér dem; bed ikke om nye kanaler. Adgangen er et spørgsmål ved kaffemaskinen, ikke en proces.

Kompetencetrækket er The Mom Test: spørg om specifikke ting i **fortiden**, ikke hypoteser om fremtiden, og tal mindre. De dårlige data du får serveret er komplimenter, hypotetisk fyld og ønskelister. I B2B-compliance er det skærpet: **den der køber er sjældent den der bruger.** Compliancechefen taler i risiko, onboarding-koordinatoren i irriterende arbejdsgange, og de lyver på hver sin måde. Registrér rollen i hver logpost.

## Kvalitetsattribut-scenarier: din del af kravarbejdet

Funktionelle krav skriver stifteren og kunderne. **Ikke-funktionelle krav skriver ingen** — og i et compliance-produkt er det dem der afgør om produktet overlever en kundeaudit. Skriv dem i den seksdelte form (kilde, stimulus, artefakt, miljø, respons, responsmål), hvor responsmålet **altid** er et tal: ikke "revisionssporet skal være pålideligt", men "et fuldt ændringsspor for én leverandør over 24 måneder leveres kronologisk inden for 30 sekunder, og enhver efterredigeret post kan detekteres maskinelt".

Omsæt så mindst to scenarier til **fitness functions der fejler bygget i CI**. En arkitekturtest der forsøger cross-tenant-læsning og forventer afvisning er 40 linjers kode og mere værd end 40 siders dokumentation.

## Shape Up, og aldrig et nej uden prisskilt

Vend rækkefølgen om: ikke "hvor lang tid tager det", men "**hvor meget er det værd at bruge**". Fast appetite i stedet for estimat, scope forhandles ned i stedet for at tiden forhandles op, navngivne rabbit holes og no-gos, circuit breaker der stopper frem for at forlænge.

Den største rollerisiko er ikke manglende prioriteringsevne, men at du bliver **Ham Der Siger Nej** — og en arkitekt der kun producerer begrænsninger bliver rutet udenom på uger, ikke år. Modtrækket er tredelt: "det du beder om koster X dage og denne konsekvens" — "vi kan få 80 procent af effekten for Y" — "vælger vi den billige nu, koster det Z at rette senere, og her er hvornår vi rammer det". Tredje led er det mest oversete: **tillad genvejen eksplicit og datosæt hvornår den bliver dyr.**

## Ressourcer

| Ressource | Prio | Tid | Springes over |
|---|---|---|---|
| **Shape Up** (Singer), gratis på basecamp.com/shapeup | P0 | 3-4 t (del 1-2) | Betting table, seks-ugers-cyklusser |
| **The Mom Test** (Fitzpatrick), momtestbook.com | P0 | 3 t | Intet; men du har to slags kunder |
| **Evidence-Based Management Guide** (Scrum.org, gratis) | P0 | 1 t + 1 t på egne mål | Organisationsafsnittene; PAL-EBM (ca. 975 USD, kursuspligtig) |
| **Code Red** (Tornhill & Borg, arXiv:2203.04374) | P0 | 1,5 t | Metodeafsnittet ved første læsning |
| **Fundamentals of Software Architecture**, 2. udg. (2025) | P0 | 8-10 t, udvalgte kapitler | Architecture styles; ledelse af arkitektteams |
| **riskstorming.com + c4model.com + adr.github.io** | P0 | 3 t samlet | Tung modelleringsformalisme. Start med adr-tools; Log4brains hvis loggen skal læses af ikke-udviklere |

Dertil Littles IEEE-artikel (1 t), Adzics *Impact Mapping* (3 t) og Torres' artikel om opportunity solution trees på producttalk.org (gratis; drop product trio og interviewkadencen). **Springes over nu:** Cagan og Hohpes *Architect Elevator* forudsætter en organisation med flere etager og teams at transformere, og Team Topologies kræver flere end tre teams.

## Certificeringer

Den strukturelle test er: **kan du dumpe prøven?** Kursuspligtige certificeringer dokumenterer fremmøde, ikke kompetence.

| Certificering | Pris | Struktur | Dom |
|---|---|---|---|
| **PSPO I** | 200 USD | Ingen kursuspligt, uafhængig prøve, livsvarig, gratis øvelsesprøve | Eneste der består testen — men certificerer ordforråd, ikke dømmekraft. **Kun hvis et slot er til overs** |
| CSPO | 349-599 USD + 100 USD hvert 2. år | **Ingen eksamen**; certificering ved fremmøde og instruktørens underskrift | Dårligste enkeltkøb på listen |
| SAFe POPM | 800-1.200 USD + **100 USD årligt** | Kursuspligtig; eksamen alene 395 USD | Du lejer badgen; SAFe forudsætter Agile Release Trains |
| PMP | 445 / 675 USD (hævet 6. aug. 2026) | Kræver **36 mdr.** dokumenteret projektledelse + 35 kontakttimer | **Lukket dør.** Du opfylder ikke kriteriet i år |
| PRINCE2 7 Practitioner | ca. 445 GBP; Foundation ca. 600 USD | Obligatorisk e-bog i voucheren | Irrelevant ved ni ansatte; stifterens beslutning hvis en kunde kræver det |

PSPO II (500 USD) og ICAgile ICP-APO (1.195-1.300 USD, kursusbundtet uden eksamen) springes over uden diskussion. Priserne er krydstjekket via søgeresultater, ikke læst hos udbyderne — verificér før køb. "PRINCE2 og SAFe er i høj kurs i Danmark" stammer fra kursusudbydernes egne sider (uverificeret), og PSPO I's prøveformat er heller ikke verificeret (uverificeret).

**Det skarpeste træk er at tage indholdet og droppe badgen.** EBM-guiden er gratis, og "Ability to Innovate" måler bogstaveligt hvor stor en andel af teamets tid der går til vedligehold og defektfiks frem for ny kundeværdi. Det er teknisk gæld som ledelsesmåling — den eneste form stifteren kan handle på. Giv slottene til arkitektur og cloud i stedet; AZ-204 blev pensioneret 31. juli 2026 til fordel for det AI-drejede AI-200, mens AZ-305 og AZ-400 fortsat er aktive pr. september 2026.

## Spikes med fysisk output

**A. Regulatorisk roadmap-kort 2026-2030 (12-15 t, derefter 2 t/kvartal).** Én række pr. regulering: anvendelsesdato, kundesegment, hvilken dokumentationstype den udløser i leverandørkæden, hvilken produktkapabilitet det implicerer, og din konfidens med kildehenvisning. Verificér hver dato ved retsakten. *Output:* 1-sides tidslinje til salg, 2-siders notat med kildehenvisninger, og en ikke-byg-liste i firmaets repo. *Svært ved:* at turde skrive ikke-byg-listen og stå ved den.

**B. Reference class og throughput-forecast (10-12 t, derefter 30 min./md.).** Træk leverede issues med start- og slutdato, klassificér, tegn fordelingen pr. kategori, sammenlign med de givne estimater, byg Monte Carlo. *Output:* reproducerbart script i repoet, en 1-sides graf der viser at spændet **ikke** indsnævres over tid, og en halv sides forecastregel. *Svært ved:* datakvalitet, ikke statistik.

**C. Hotspot-analyse og prisskilt på certifikat-udløbsmotoren (12-15 t + 2 t effektmåling senere).** Churn gange kompleksitet pr. fil fra git-historikken. Vælg hotspottet i certifikat- og varslingsflowet; en misset varsling er en compliance-hændelse hos kunden. Mål gennemsnitlig **og maksimal** løsningstid dér kontra baseline. *Output:* hotspot-rapport med graf, tabel med målt løsningstid, og et 1-sides beslutningsoplæg i kroner og udviklerdage uden ordet "refaktorering" i overskriften. *Svært ved:* det sociale. Et nej er ikke en fiasko; en reel beslutning truffet på dine tal er resultatet.

**D. Fire Shape Up-pitches over året (8-10 t pr. stk.).** *Output:* fire topsiders pitches plus en efterprøvningslog: appetit, faktisk tid, hvad der blev **skåret væk**, hvilke rabbit holes du ikke forudså.

**Løbende, uden nogens tilladelse.** *ADR-bootstrap (4-6 t + 20-30 min. pr. beslutning):* bagudfyld fem beslutninger firmaet allerede har truffet — tenancy-model, dokument- og certifikatlagring, integrationsmønster mod kunders ERP, sikring af revisionsspor mod efterredigering, GDPR-sletning med legal hold ovenpå. "Consequences" skal indeholde noget der **er** dårligt ved valget. *Discovery-log (1-2 t/uge i 8-10 uger):* to linjer pr. supportticket — hvad brugeren *forsøgte* at opnå, og hvad de *bad om*. *Risk-storming (6-8 t)* på fx idempotent indlæsning af leverandørstamdata fra kundens ERP, med to kolleger inde.

## Feedback udefra

"Det virkede jo" kan siges om både gode og dårlige beslutninger. Mindst to af disse skal køre **kontinuerligt**.

- **Arkitektur-kata-gruppe, tre personer, to timer om måneden.** Hver deltager navngiver én ting de ville gøre anderledes og én ting der ville brække. Solo mister du pointen, som er forsvaret. Nul kroner.
- **Betalt ekstern design-review-mentor, 1-2 t/md., 15.000-25.000 kr./år.** Bed om det som "ekstern review af vores arkitekturbeslutninger", ikke som karriereudvikling — ved 4,2 mio. i bruttofortjeneste er det risikoreduktion, ikke personalegode.
- **GOTO Meetups Aarhus og Aarhus .NET User Group**, gratis: det vigtige er at **præsentere**, ikke at deltage. GOTO Copenhagen 28. sept. - 2. okt. 2026 er om atten dage (billetpris uverificeret).
- **DILF**, 3.900+ indkøbs- og logistikprofessionelle: modspil på om du har forstået **domænet** rigtigt. Studerende er gratis medlem, og det vindue lukker den dag du bliver fuldtidsansat (øvrige vilkår uverificeret).

**Det der ikke er feedback:** at stifteren siger ja. I et nimandsfirma kan man vinde en diskussion gennem nærhed, ihærdighed og at være den der talte sidst.

## Faldgruber

- **At indføre RICE eller WSJF.** Løser et problem firmaet ikke har.
- **At forsøge at blive Product Owner.** Konkurrerer du om rollen, bliver du en forhindring i stedet for en ressource.
- **At argumentere på gennemsnittet** i stedet for på halen — og **at rydde op hvor det irriterer dig mest** i stedet for hvor det berører omsætning.
- **Story points**, og **Cagan eller Torres læst som opskrifter**. Det første fjerner information ved tre til fem udviklere; det andet koster måneder på at bede om strukturer firmaet ikke kan bære.
- **#NoEstimates som identitet**, og **kursuspligtige certificeringer**. Giv et interval med en sandsynlighed; og en badge man ikke kan dumpe signalerer "jeg køber troværdighed", ikke "jeg måler kompetence".
- **At bygge produkt på CSDDD-hastværk.** Det er 2029-omsætning.
- **At overtage salgssamtalen**, og **at behandle supporttickets som støj**. Lyt med, notér, spørg bagefter — begge kanaler er lånte.
- **At producere artefakter ingen læser.** Ændrer et dokument ikke en beslutning inden for to uger, var det dekoration.

## Sådan ved du at du kan det

| Måned | Kriterium | Bestået når |
|---|---|---|
| 6 og 9 | **Kalibrering** | 60-90 procent af de faktiske tider falder inden for det interval du angav **på forhånd**, over mindst 30 opgaver. Skrevet før arbejdet, så det kan ikke snydes |
| 6 | **Reference class** | Et script i repoet udleder cycle time-fordelingen fra jeres historik, og tre forecasts er **efterprøvet** |
| 9 | **Beslutningspåvirkning** | Mindst ét valg er ændret eller forkastet på grund af et dokument du skrev, og du kan pege på dokument, beslutning og dato. Nul betyder dekoration |
| 9 | **ADR-log** | 15 ADR'er, heraf 5 bagudfyldte domænebeslutninger og 3 "superseded" med begrundelse. Hver har mindst én reel ulempe i "Consequences" |
| 9 | **Teknisk gæld** | Ét afgrænset forslag fremlagt i kroner og udviklerdage, godkendt **eller** afvist. Et afvist forslag tæller som bestået; et der aldrig blev fremlagt gør ikke |
| 9 | **Discovery og appetit** | 30 poster med rollen (køber kontra bruger) registreret og én prioritering sporet til et mønster; fire leverancer holdt inden for selvvalgt tidsbudget ved at **skære scope** |
| 9 | **Fitness functions** | To scenarier kører i CI og har mindst én gang **fejlet et build** og stoppet en fejl. En test der aldrig er blevet rød har ikke bevist noget |
| 9 | **Ekstern nedrivning** | To designoplæg gennemgået uden for firmaet, og du kan pege på hvad du ændrede. Ellers var reviewet høfligt |
| 9-10 | **Mundtlig test** | Du forklarer på tre minutter det økonomiske argument for din seneste arkitekturbeslutning til en ikke-teknisk person, uden forberedelse, og svarer på "hvad var det billigere alternativ" uden at falde tilbage på teknik |
| Løbende | **Alternativ-disciplinen** | Din log viser at du i mindst 90 procent af afvisningerne medbragte et alternativ med et prisskilt |
