# 01. Rollen: hvad en Solution Architect faktisk laver

> Du sigter mod en rolle, der ikke findes på din arbejdsplads. Ni ansatte og syv årsværk betyder ingen arkitektstige, ingen at blive forfremmet af, og ingen der kan give dig kvalificeret modspil på et designvalg. Det er ikke et argument mod målet. Det betyder, at målet skal defineres som en kompetence med observerbare kendetegn i stedet for som et visitkort — og at du skal kende definitionen præcist nok til at se, hvornår du mangler den.

## Arkitektur er de dyre beslutninger

Simon Brown formulerer det skarpest: arkitektur er de beslutninger, der er kostbare at ændre senere. Forskellen på en dygtig senior udvikler og en solution architect er derfor ikke teknisk dybde. Den er ejerskab over det ikke-funktionelle, dokumentation af fravalgene, og at leve med konsekvensen.

| | Senior udvikler | Solution architect |
|---|---|---|
| Leverance | Feature X, godt bygget | Design med begrundelse og to forkastede alternativer |
| NFR-ejerskab | Diffust, eller ingen | Arkitekten, med tal på |
| Dokumentation | Kode, tests, README | ADR'er, kontrakter, kostmodel, risikoliste |
| Forsvar | Sjældent nogen | Arkitekten, mod en der vil have det billigere |
| Horisont | Til sprintet er slut | Til om 18 måneder, hvor det brænder |
| Måles på | Om det virker | Latency, tilgængelighed, kost, opbevaringsperiode, revisionsspor |

Oversat til dit domæne: en senior udvikler bygger jobbet, der varsler om udløbende leverandørcertifikater, og bygger det godt. Arkitekten spørger først, hvor mange certifikater den største kunde har, hvad der sker når 400.000 udløber i samme uge, hvad en revisor skal kunne få svar på om tre år, og hvad varslingen koster i Azure ved ti gange så mange tenants — og skriver bagefter ned, hvilke to andre løsninger der blev fravalgt, og hvad de ville have kostet.

Unge arkitektkandidater afvises sjældent på manglende viden. De afvises, fordi de svarer som senior udviklere: springer til teknologivalg før de har spurgt om volumen, budget, SLA og datafølsomhed; præsenterer ét design uden fravalg; kan ikke sætte tal på noget; forsvarer i stedet for at iterere, når præmissen ændres. Det målte er dømmekraft og spændvidde, ikke korrekthed.

## Det danske ord betyder noget andet end det engelske

I Dansk ITs Architecture Competence Framework er løsningsarkitekten den, der **implementerer** en løsning beskrevet af andre arkitektroller — en udførende rolle under en enterprise- eller domænearkitekt. I dansk B2B SaaS og internationalt betyder Solution Architect det modsatte: den der **ejer** designet og brændpunktet mellem forretning og teknik. Regel: læs ansvarslisten, aldrig titlen. To opslag med identisk titel kan være to jobs med fem års forskel i adgangskrav.

## Tre virksomhedstyper, tre jobs, tre adgangskrav

| Type | Hvad rollen reelt er | Adgangskrav | Prisen |
|---|---|---|---|
| Mindre dansk SaaS | Titlen findes ofte ikke. Findes den: enten den ene der ejer platformens retning (reelt lead/principal), eller en kundevendt implementeringsrolle | Tillid, ikke år | Ingen ladder, ingen at lære af, ingen ekstern vekselkurs på titlen |
| Konsulenthus (Netcompany, KMD, twoday, Trifork, Devoteam, Fellowmind, Accenture) | Arkitektur er en fakturerbar vare: sælges, estimeres, forsvares i udbud, leves med i leverancen | 3-6 år. Netcompany har eksplicit ladder (Senior, Managing Architect) med akademi og mentor | Timeregnskab, salgspres, risiko for at ende med tilbudsafsnit |
| Enterprise/offentlig | Én løsning i et stort landskab under en EA-funktion, med standarder og leverandørstyring | 4-8 år, undtagen de eksplicitte junioropslag | Lavere løn, tungere proces, mindre kodekontakt |

**Konsulenthuset er den mest undervurderede rute**: flest arkitektstillinger pr. medarbejder, tre til seks kundelandskaber på to år, og forfremmelse der følger dokumenteret leverance frem for anciennitet. **Offentlig sektor er det ene dokumenterede indgangshul**: Københavns Kommune Koncern IT har annonceret Solution Architect eksplicit til kandidater med 0-5 års relevant erhvervserfaring, med datamatiker/cand.IT nævnt som baggrund, i et kontor på ca. 80 medarbejdere og 12 teams. Vejdirektoratet, Aarhus Universitet og Lægemiddelstyrelsen har haft tilsvarende opslag. Titlen findes altså reelt på indgangsniveau i Danmark, med governance og mindre kodetid som pris.

Hvad titlen er værd, så du ikke overvurderer den: PROSAs lønstatistik 2026 (2.642 besvarelser) sætter kategorien "Plan" — it-arkitekter — til 69.476 kr./md. inkl. tillæg, bonus og pension, mod 63.812 kr./md. for "Build". Forskellen er ca. 5.600 kr./md. Levels.fyi angiver Netcompany Solution Architect DK til ca. 844.000-850.000 kr./år total, men på tyndt selvrapporteret grundlag (uverificeret som repræsentativt). Brug aldrig Glassdoor, PayScale eller LønRadar i en forhandling; deres DK-tal svinger med en faktor to.

## Der findes ingen arkitektstige hvor du sidder

Ni ansatte, formentlig tre til fem udviklere. Der er ingen rolle at vokse ind i, og fik du titlen, ville den blive diskonteret kraftigt af enhver ekstern hiring manager. Konsekvensen er ikke, at stedet er forkert. Konsekvensen er, at det interne spor omdefineres: **internt bygger du evidens** — scope, driftsansvar, artefakter, domæneviden, ting der kan bevises for en fremmed. **Titlen indløses et andet sted, senere.** At blande de to sammen er den mest sandsynlige enkeltfejl i planen.

Til gengæld giver et mikrofirma dig bredde, som en junior i en 500-mands virksomhed ikke får i år ét: drift, database, integrationer, kundesamtaler og support inden for tolv måneder. Der uddeles ikke mandat hos ni mennesker — der er kun folk med for meget at lave. Man tager plads ved at levere noget, ingen bad om, i lille format. Hver af disse er ét spørgsmål til én person:

- Læseadgang til Application Insights, begrundet med at du vil kunne verificere dine ændringer i produktion. Uden telemetri er alle dine artefakter påstande.
- Overtag integrationsdokumentationen til kunder. Kontraktdesign i praksis, kundevendt, og ingen slås om opgaven.
- Lyt med på ét kundemøde om onboarding. Begrund det fagligt, ikke karrieremæssigt.
- Læs 12 måneders supportsager og kategorisér dem. Kræver ingen tilladelse og giver en fejlmønsteranalyse af et system i drift — materiale en kandidat med 1-3 års erfaring aldrig har.
- Skyg to deployments, kør derefter en under opsyn. Du løser samtidig et bus-factor-problem.

Rådgivning om sponsorer, review boards og magtanalyse gælder ikke her. Mandat får du ved at spørge stifteren direkte.

## Anti-rollen: PowerPoint-arkitekten

Ikke en karikatur, men en jobtype man ansættes i ved et uheld. Diagnostik på et opslag:

| Rødt flag | Grønt flag |
|---|---|
| Kun verberne sikre, understøtte, facilitere, rådgive, koordinere | Verberne designe, specificere, måle, reviewe |
| Ingen teknologier, kun "cloud" og "transformation" | Navngivne teknologier og platforme |
| Refererer til en arkitekturfunktion | Sidder i et leveranceteam |
| "Vedligeholde EA-repository" (LeanIX, Ardoq, Sparx) som kerneopgave | ADR'er og specifikationer som leverance |
| Intet om drift, incidents eller SLA | On-call, observability, målbare krav |

Beskyttelsen er en regel, du måler dig selv på hvert halve år — også i måned 13, 24 og 36:

> Har jeg deployet noget til produktion inden for de sidste 6 måneder? Har jeg haft driftsansvar for noget, jeg selv har designet, inden for de sidste 12? To nej'er i træk betyder, at jeg er på vej ind i tårnet, uanset hvad titlen siger.

## Kompetencemodellen: ti akser

Score dig selv i måned 1 og igen ved kompetenceporten i måned 9-10. Skriv datoen, gem arket.

| Kompetence | Kompetent | Stærk |
|---|---|---|
| Kravsfremdragelse og NFR med tal | Sætter tal på, men gætter dem | Måler dem, kender usikkerheden, ved hvilke to der er i konflikt og hvad prisen er |
| Trade-off-analyse og ADR'er | Nævner alternativer, afviser dem på smag | Afviser på en akse han kan måle eller prissætte, og siger hvad der ville vende valget |
| Integrations- og kontraktdesign | Versionerer og tænker på forbrugeren | Har brækket en kontrakt i produktion og kender prisen på et deprecation-vindue |
| Driftbarhed og observability | SLI'er og alarmer før deployment | Fem fejlmønstre han selv har ramt; designer baglæns fra "hvad er svært kl. 3 om natten" |
| Sikkerhed og compliance-by-design | Threat model og dataklassifikation | Designer så en revisor om tre år får svar uden at grave i logfiler, og kender prisen i kompleksitet |
| Kostmodellering | Kan slå priser op og lave overslag | Model med tre poster, kender usikkerheden, ved hvad der flytter tallet mest |
| Stakeholder-kommunikation | Forklarer problemet før løsningen | To sider en beslutningstager handler på, og skifter i samme møde til retry-semantik |
| Domæne: procurement, supplier compliance, revision | Kan forklare hvorfor kunden køber produktet | Forudsiger kundernes krav om 18 måneder og bygger, så de er billige at opfylde |
| Estimering og risiko | Estimerer med spænd og forudsætninger | Kender sin bias, estimerer andres arbejde, ved hvilken risiko der flytter estimatet mest |
| At få noget godkendt uden mandat | Bygger forslag på målte data | Bliver spurgt uopfordret, fordi han har haft ret på en måde andre kunne efterprøve |

"Kompetent" på alle ti og "stærk" på ingen er en fældet port: rollen bæres af trade-off-analyse og driftbarhed, og dér skal du i "stærk". Og din egen score er værdiløs alene. Mindst to praktiserende arkitekter uden for LeanLinking skal have gennemgået et af dine designs skriftligt, før den tæller. En kollega i et 9-mandsfirma tæller halvt.

## Ressourcer

| Ressource | Prioritet | Tid | Springes over |
|---|---|---|---|
| Azure Well-Architected Framework, "Architect role" — `https://learn.microsoft.com/en-us/azure/well-architected/architect-role/fundamentals` | Kerne | 4-6 t., derefter opslagsværk | Resten af WAF; de fem søjler læses ikke forfra |
| 30 danske arkitektopslag kodet i et regneark (jobindex.dk, it-jobbank.dk, thehub.io, LinkedIn DK, netcompany.com/careers, kk.dk/ledigestillinger) | Kerne | 4-6 t. i måned 1, 2 t. i måned 6 og 10 | Intet |
| Dansk IT ACF, "Løsningsarkitekt" — `https://dit.dk/DIT-Arkitektur-Certificering/Dansk-IT-Architecture-Competence-Framework/Loesningsarkitekt` | Kerne | 1-2 t. | Selve certificeringen |
| Fundamentals of Software Architecture, 2. udg. (Richards & Ford, marts 2025, ISBN 9781098175511) | Kerne | 10-12 t.: architecture characteristics, trade-offs, arkitektrollen | Katalogdelen over arkitekturstile; 1. udgaven |
| Hohpe, "The Architect Elevator" — `https://martinfowler.com/articles/architect-elevator.html` | Kerne | 2 t. | Bogen af samme navn |
| Brown, "Are You a Software Architect?" — `https://www.infoq.com/articles/brown-are-you-a-software-architect/` | Kerne | 45 min. i måned 1 og igen ved porten | Intet |
| C4-modellen — `https://c4model.com/` + ADR-materiale (adr.github.io) | Kerne | 3 t., derefter kun anvendelse | arc42, TOGAFs artefaktkatalog |
| Architectural Katas — `https://github.com/walljt/architecture-katas` | Støtte | 3-4 t. pr. kata, ca. 6 over året | Brug først når du har artefakter at tale ud fra |
| PROSA lønstatistik 2026 — `https://www.prosa.dk/raadgivning/loen-og-forhandling/loenstatistik-2026/` | Støtte | 1 t. | Glassdoor, PayScale, LønRadar |
| Fællesoffentlig Digital Arkitektur — `https://arkitektur.digst.dk/` | Betinget | 6-8 t. | Alt, medmindre du vælger den offentlige rute. Beslut i måned 5-6 |
| Software Architecture: The Hard Parts | Senere | Måned 6+ | Læses når du står i problemet |

Spring helt over i år 1: "System Design Interview"-bøger og "Solution Architect roadmap"-kurser (træner FAANG-skalering og memorerede arkitekturer, præcis det danske interviewere afviser), IASA CITA (ingen dansk udbredelse) og AWS-/GCP-certificeringer (to clouds på ét år med 10-15 timer om ugen er garanteret overfladiskhed).

## Certificeringer set fra rolleperspektivet

| Cert | Status | Pris | Dom |
|---|---|---|---|
| AZ-204 | Pensioneret 31. juli 2026, erstattet af AI-200 (Azure AI Cloud Developer Associate), som er AI-drejet og ikke en generel .NET-eksamen | — | Alt råd om "tag AZ-204" er forældet |
| AZ-104 | Aktiv | (uverificeret) | Nødvendig, hvis AZ-305 skal tælle |
| AZ-305 Solutions Architect Expert | Aktiv, opdateret 17. april 2026. 40-60 spørgsmål, 120 min., beståelse 700/1000 | ca. 165 USD | Den ene cert der matcher din stak. Udløber AZ-104, udløber Expert-statussen, selvom AZ-305 er gyldig |
| AZ-400 | Ikke bekræftet i denne research (uverificeret) | (uverificeret) | Tjek selv på learn.microsoft.com før du planlægger efter den |
| TOGAF | Aktiv | (uverificeret) | Spring over i år 1: enterprise-vokabular og governance, ikke løsningsdesign |
| Dansk IT Arkitektur Certificering | Foundation 3 dage, én gratis omprøve inden 3 mdr.; SA Practitioner 4 dage / 25 timer, casebaseret | 3.499 kr. ex moms for Foundation-certifikatet alene, plus kursusdage | Kun hvis du har valgt den offentlige rute **og** arbejdsgiver betaler |

## Tre øvelser der gør rollen målbar

### Øvelse 1: Rollerekognoscering — 30 opslag kodet

Uden denne optimerer resten af året mod et gæt. Saml 30 danske arkitektopslag (Solution Architect, løsningsarkitekt, integrationsarkitekt, cloud architect, technical architect) og gem hvert som PDF, for opslag forsvinder. Kod hvert på: årskrav, virksomhedstype, teknologier, om drift nævnes, om kodning nævnes, om dansk kræves, hvem rollen refererer til, hvilke artefakter der nævnes, og tårnrolle eller leverancerolle efter rød/grøn-listen.

**Begrænsning:** 4-6 timer, ét regneark, ingen perfektionisme. Tæl, før du konkluderer.

**Fysisk output:** Regnearket med 30 kodede opslag. Én A4-side syntese: de otte krav der går igen, fordelt på virksomhedstype. Én A4-side gap-analyse med de tre største huller navngivet, uden undskyldninger. Gentages på to timer i måned 6 og 10.

### Øvelse 2: Solution design document for platformen as-is

Du arbejder i en kodebase, du ikke har et arkitekturbillede af, og har aldrig produceret en solution design i den form en konsulent afleverer. Reverse-engineer platformen: C4 på context- og container-niveau, component kun for ét område — supplier onboarding eller certifikat- og dokumenthåndtering. Integrationsoversigt over alle eksterne grænseflader. Dataejerskab. Et NFR-katalog hvor mindst fem karakteristika er **målt**: p95 på de tre tungeste endpoints, største kundes datamængde, dyreste månedlige Azure-ressource, fejlrate under deployment, antal certifikater under overvågning.

**Begrænsning:** 20-25 timer over to uger, kun det der kan udledes af kode, konfiguration, Azure-portalen og telemetri. Ingen interviews i første omgang — det er en test af, om du kan læse et system. Tegn først forkert og hurtigt fra hukommelsen, verificér derefter, og notér hver fejl. Fejllisten er den værdifulde del.

**Fysisk output:** 8-14 sider med C4-diagrammer, NFR-katalog med målte tal, risikoliste med fem risici og deres arkitekturkonsekvens, og én side om hvad du ikke kunne finde ud af uden at spørge. Del det som et spørgsmål — "jeg tegnede det for at forstå det, hvad har jeg misforstået" — ikke som en konklusion.

### Øvelse 3: Trade-off-kata på tid

Du kan endnu ikke levere et forsvarligt design under tidspres i et ukendt domæne, og det er præcis samtaleformatet. Tag en architectural kata og lever inden for otte timer: mindst otte kravsspørgsmål stillet **før** første diagram, kontekstdiagram, to forkastede alternativer med begrundelse, det valgte design, fem NFR'er med tal, fem risici, og et groft estimat i personmåneder og Azure-kroner.

**Begrænsning:** Hård timebox på otte timer, maks. ti sider, maks. 30 minutters research. Sæt en timer. Læs kravsspørgsmålene igen til sidst: besvarede du dit eget design uden at have svar på halvdelen, er det fundet.

**Fysisk output:** Kata-besvarelse i tilbudsformat på ti sider plus skriftlig selvvurdering. Gentages fire til seks gange over året. Fra måned 7 skal en ekstern person ændre en præmis efter fire timer — ti gange trafikken, halveret budget, kunden kræver on-prem — og måle, om du itererer eller forsvarer.

## Faldgruber

- **At jagte titlen internt.** Der findes ingen arkitektladder ved syv årsværk, og titlen derfra læses som selvudnævnt. Det interne spor skal give scope, drift og artefakter.
- **At kalde dig Solution Architect på LinkedIn, før du er det.** Arkitektmiljøet i Aarhus er lille, og folk taler sammen. Beskriv hvad du har lavet, ikke hvad du kalder dig.
- **At foretrække diagrammer frem for beslutninger.** Et C4-diagram uden en ADR er dekoration. Flere diagrammer end ADR'er er et dårligt tegn.
- **At læse arkitekturbøger uden at producere artefakter.** Læsning føles som fremgang uden at være det. Ingen uge uden et artefakt.
- **At bruge system-design-interviewmateriale som forberedelse.** Danske samtaler i dit segment tester, om du spørger først, sætter tal på og itererer.
- **At tage TOGAF eller Dansk IT-certificeringen i år 1 uden at have valgt rute.** Dyre timer taget fra øvebanen.
- **At overse domæneviden til fordel for endnu en Azure-tjeneste.** Der er mange Azure-arkitekter i Danmark og få, der forstår supplier onboarding, audits, certifikathåndtering og revisionsspor. Kombinationen er din differentiering.
- **At måle dig selv på følelser.** "Jeg føler mig ikke klar" er standard hos kompetente folk; "jeg føler mig klar" hos inkompetente. Porten afgøres på tællelige ting.
- **At vente på at få lov.** Hver gang du tænker "det må jeg vist spørge om": kan det i stedet gøres på én time og vises frem bagefter.

## Sådan ved du at du kan det

Observerbare kriterier. Ingen af dem afgøres af din egen fornemmelse.

- [ ] Du kan på 45 minutter, foran en fremmed, tage et ukendt forretningsproblem og producere mindst otte kravsspørgsmål **før** du nævner en teknologi, et kontekstdiagram, to forkastede alternativer, det valgte design, fem NFR'er med tal og tre risici — uden opslag. Målt på optagelse, vurderet af en der ikke er din ven.
- [ ] Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse.
- [ ] Du kan på fem minutter forklare forskellen på rollen i et konsulenthus, i en kommune og i et B2B SaaS-firma, og sige hvilken du sigter mod og hvorfor — med henvisning til konkrete danske opslag.
- [ ] Du kan uden forberedelse svare på, hvad løsningen koster pr. måned, hvad der driver kosten, og hvad der sker ved ti gange brugere. Med tal, og med et regneark bag.
- [ ] Du har målt mindst fem ikke-funktionelle egenskaber på et system i reel drift — ikke gættet dem.
- [ ] Der ligger mindst 15 ADR'er til reelle beslutninger, hvoraf mindst fem har en konsekvens, du selv har set indtræffe. Hypotetiske beslutninger tæller ikke.
- [ ] Mindst to personer uden for LeanLinking, helst praktiserende arkitekter, har givet skriftlig kritik af et af dine designs, og du kan redegøre for, hvad du ændrede.
- [ ] Du har skrevet mindst ét dokument på højst to sider, som en ikke-teknisk person har læst, forstået og **handlet** på: en beslutning truffet, en prioritering ændret, en udgift godkendt eller afvist.
- [ ] Du kan navngive fem fejlmønstre, du selv har ramt i produktion. Retry uden backoff der forstærkede en overbelastning. En migration der ikke kunne rulles tilbage. En alarm der aldrig gik i gang. En timeout længere end den kaldende parts.
- [ ] Der er kommet mindst tre uopfordrede henvendelser om dit design eller din vurdering. Det er det eneste kriterium på, at nogen behandler dig som arkitekt, og det kan ikke fabrikeres.
- [ ] Du har deployet til produktion inden for de sidste seks måneder og haft driftsansvar for noget, du selv har designet, inden for de sidste tolv.
