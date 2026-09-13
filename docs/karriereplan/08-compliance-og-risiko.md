# 08. Compliance, sikkerhed og risiko: din differentiering

> Du sidder i et ni-mandsfirma hvis produkt bogstaveligt talt er leverandørcompliance. Domæneviden du tilegner dig af karrieregrunde, er samtidig produktviden din arbejdsgiver betaler for. Den dobbelttælling er sjælden — de fleste må vælge mellem at lære noget til jobbet og noget til karrieren. Kombinationen "kan bygge systemet OG kan læse det regulatoriske krav" er tynd i Danmark, og den er den enkeltfaktor der mest realistisk kan accelerere dit mål.

## Hvorfor det er det eneste argument du kan vinde som junior

Normalt tjener man arkitekturindflydelse gennem anciennitet. Compliance er undtagelsen. Et regulatorisk krav er en ekstern begrænsning der rangerer over interne meninger, og "vi kan ikke gøre X, fordi GDPR art. 32 kræver Y" er derfor et argument en junior kan vinde — ikke fordi han er senior, men fordi det ikke er hans holdning. Ingen anden type teknisk argument har den egenskab.

Efterspørgslen er lovbestemt frem for diskretionær: et innovationsbudget kan skæres i en nedtur, et NIS2-budget kan ikke. Udbudssiden er strukturelt smal — compliance bemandes af jurister der ikke kan læse en datamodel, engineering af udviklere der finder regulering kedelig. Den knappe kompetence er aldrig den dybeste, den er den brobyggende. Og flaskehalsen i enterprise-SaaS-salg er ikke produktet; det er security questionnaire'en og databehandleraftalen. Det arbejde er ubeskyttet territorium, fordi alle betragter det som lort.

## Den absolutte regel

Holder du op med at skrive kode, er titlen du ender med GRC Analyst. Den betaler mindre og topper tidligere. **Hvert compliance-artefakt leveres sammen med kørende kode og en måling. Aldrig et dokument uden en deployment.** Compliance uden engineering er en GRC-analytiker; engineering uden compliance er en senior udvikler; værdien ligger udelukkende i OG'et.

## Læseplan: primærtekster, ikke leverandørlitteratur

Regulativerne er gratis og kortere end whitepaperne om dem. NIS2 art. 20-23 er fire sider. URL'erne er på officielle domæner, men ikke verificeret — klik dem efter.

| Ressource | Prio | Tid | Pris | Hvad du henter |
|---|---|---|---|---|
| GDPR — kun art. 4, 5, 17, 20, 25, **28**, 30(2), 32, 33, kap. V ([eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj)) | Kerne | 6-8 t | 0 | Art. 28 er jeres rolle som databehandler. Din vigtigste artikel |
| Datatilsynets vejledninger ([datatilsynet.dk](https://www.datatilsynet.dk)) | Kerne | 8-10 t | 0 | Det en dansk DPO citerer. Læs også afgørelserne |
| NIS2, art. 20-23 ([eur-lex.europa.eu/eli/dir/2022/2555/oj](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)) | Kerne | 2 t | 0 | Art. 21(2)(d) skal du kunne recitere |
| Sikker Digital / Digitaliseringsstyrelsen + Erhvervsstyrelsen ([sikkerdigital.dk](https://www.sikkerdigital.dk)) | Kerne | 4-6 t | 0 | Dansk implementering og dansk fagsprog. NB: CFCS's ikke-militære funktioner overgik til SAMSIK januar 2025; CFCS er nu på [cfcs.dk](https://cfcs.dk) |
| Azure Architecture Center, multitenant ([learn.microsoft.com/.../multitenant/overview](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/overview)) | Kerne | 10-12 t | 0 | Kernemateriale til flagskibsspiken |
| OWASP Cheat Sheets ([cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org)) + API Security Top 10 ([owasp.org/API-Security/](https://owasp.org/API-Security/)) | Kerne | 12-15 t | 0 | Kun Authorization, Secrets Management, Logging, **File Upload**. API1 (BOLA) er bogstaveligt "tenant A henter tenant B's id" |
| ISO/IEC 27001:2022 + 27002:2022 ([ds.dk](https://www.ds.dk)) | Kerne | 8-10 t, plus 15-20 t på SoA | Et par tusinde kr. (uverificeret) | Emnets eneste udgift der er pengene værd — men først i SoA-arbejdet |
| CSA CAIQ v4.1 ([cloudsecurityalliance.org/research/cloud-controls-matrix](https://cloudsecurityalliance.org/research/cloud-controls-matrix)) + MVSP ([mvsp.dev](https://mvsp.dev)) | Kerne | 1 uge | 0 | Det spørgeskema kunder faktisk sender. v4.1 udkom januar 2026. MVSP først |
| GACI CertSearch (tidl. IAF CertSearch; IAF + ILAC fusionerede til GACI 1. jan 2026) ([iafcertsearch.org](https://www.iafcertsearch.org)) | Kerne | 2 t + spike | 0 / API-vilkår ukendt | Emnets mest anvendelige opdagelse. Se spike 3. Verificér om domænet er migreret |
| Threat modeling-pakken: Shostack kap. 1-4 og **7-9**; Manifesto ([threatmodelingmanifesto.org](https://www.threatmodelingmanifesto.org)); Threat Dragon ([owasp.org/www-project-threat-dragon/](https://owasp.org/www-project-threat-dragon/)); Elevation of Privilege ([shostack.org/games/elevation-of-privilege](https://shostack.org/games/elevation-of-privilege)) | Kerne | 16-18 t | Bog brugt, resten 0 | Kap. 7-9 er facilitering, og dem springer alle over. Threat Dragon lægger modellen i git, så den reviewes i en PR |
| Data Act kap. VI ([eur-lex.europa.eu/eli/reg/2023/2854/oj](https://eur-lex.europa.eu/eli/reg/2023/2854/oj)), CSDDD art. 5-11 ([eur-lex.europa.eu/eli/dir/2024/1760/oj](https://eur-lex.europa.eu/eli/dir/2024/1760/oj)), DORA art. 28-30 ([eur-lex.europa.eu/eli/reg/2022/2554/oj](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)), CRA ([eur-lex.europa.eu/eli/reg/2024/2847/oj](https://eur-lex.europa.eu/eli/reg/2024/2847/oj)) | Støtte | 10 t samlet | 0 | Fuld tenant-eksport er lovkrav, ikke en pæn feature. CSDDD's due diligence-proces ER produktflowet i lovsprog. DORA bliver kerne i det sekund I har én finansiel kunde |

**Fravalgt med vilje:** NIST SP 800-53, COBIT, ITIL, ESRS Set 1, GPAI-kapitlet i AI Act, Microsofts Threat Modeling Tool, alle "ISO 27001 for dummies"-bøger, og alt indhold fra Vanta, Drata, Secureframe og Sprinto. Værktøjerne skal du vide findes; deres indhold er markedsføring designet til at få compliance til at lyde sværere end det er. Gratis undtagelse værd at læse: Building Secure and Reliable Systems ([sre.google/books/building-secure-reliable-systems/](https://sre.google/books/building-secure-reliable-systems/)), kapitlerne om least privilege og recovery.

## Fem krav du sporer hele vejen ned

At referere ti direktiver gennemskues øjeblikkeligt. At spore ét krav fra lovtekst til en linje i en Bicep-fil er mere værd end alle ti resuméer. Byg tabellen for dit eget system, én række ad gangen.

| Krav | Dansk kilde | ISO 27001:2022 | Kontrol i dit system | Evidens |
|---|---|---|---|---|
| GDPR art. 32(1)(a) pseudonymisering | Behandlingssikkerhed | A.8.11 | Redaktionsprocessor i telemetripipelinen | Test: ingen e-mail når exporteren |
| GDPR art. 17 sletning | Sletning | A.5.34 | Orkestreret sletning på tværs af SQL, Blob, DLQ, søgeindeks, logs | Sletteattest + målt p95 |
| NIS2 art. 21(2)(d) leverandørkæde | Sikker Digital | A.5.19-A.5.22 | Vurdering af egne underleverandører + SBOM i pipeline | Underleverandørliste + CycloneDX |
| NIS2 art. 21(2)(b) hændelser | Sikker Digital | A.8.15, A.8.16 | Audit-log adskilt fra diagnostisk log, append-only | Immutable blob-politik + SLO |
| GDPR kap. V overførsler | Tredjelandsoverførsler | A.5.14 | Azure Policy der begrænser tilladte regioner til EU | Policy-fil i git + rapport |

Sidste række er hele nichen på tredive sekunder: en regionspolicy er bogstaveligt talt GDPR kapitel V udtrykt som kode, og du kan pege på filen.

## Fire spikes med fysisk output

Alle henter deres problem fra leverandørkæde-, dokumentations- og compliance-domænet, så arbejde og øvebane fodrer hinanden i stedet for at konkurrere om dine 10-15 timer.

### 1. Tenant-isolation i tre modeller, målt og angrebet (25-30 t, flagskib, læg den først)

Byg et minimalt .NET-API med domænet Leverandør + Certifikat + Auditfund, og implementér isolation tre gange: EF Core global query filter, Azure SQL Row-Level Security på SESSION_CONTEXT, og database-per-tenant i elastic pool. Identisk API-overflade. Budgetloft 300 kr./md for hele serien; brug Azure SQL Serverless og riv miljøet ned mellem sessioner.

Skriv abuse-testsuiten **først**, uafhængigt af implementeringen: for hvert endpoint bruges tenant A's token mod tenant B's id, og der asserteres 404. Introducér derefter tre realistiske fejl med vilje — et baggrundsjob med en DbContext bygget uden for request-scope, et `FromSqlRaw` uden tenant-prædikat, en cachenøgle uden tenant-præfiks — og registrér hvad hver model fanger. Pointen er ikke at designe isolation, det kan næsten alle. Det er at kende fejlmønstrene. En læk her afslører en kundes indkøbsstrategi til en konkurrent.

**Output:** ADR med eksplicit beslutningsregel — ved hvilket tenantantal og hvilken datasensitivitet skifter svaret. C4-diagram med trust boundaries. Resultattabel med p95-latens, kr./tenant/md ved 50 og 500 tenants, migrationstid. Bugmatrix. Retrospektiv.

### 2. Sletning og retention, inklusive backup-paradokset (20-25 t)

Start med kortlægningen, ikke koden: list hvert sted et navn eller en e-mail kan ende, inklusive Application Insights, dead letter queues og søgeindekset. Det er den øvelse der giver indsigten. Byg derefter sletningen som en orkestreret, genstartbar proces. Den ADR de fleste undgår, gør spiken værd at lave: hvordan opfylder du art. 17 når du ikke kan slette fra en immutable backup. Det accepterede svar — dokumenteret backuprotation plus en suppressionsliste der genanvendes ved restore — kan de færreste formulere.

**Output:** ADR "Sletning kontra backups". Retentionsmatrix per datakategori. Datastrømskort. Målt p95 for fuld sletning. Sletteattest-format. Citér Datatilsynet frem for en blog.

### 3. Certifikatverifikation mod akkrediteringskæden (10-15 t, ren domæneguldåre)

Et ISO-certifikat er kun noget værd hvis udstederen er akkrediteret af et IAF MLA-medlem — i Danmark DANAK. Falske og uakkrediterede certifikater er et reelt problem i leverandørstyring, og de færreste SRM-systemer tjekker. Byg verifikationen mod IAF CertSearch (undersøg API-vilkårene først). Læg to regler oveni: overgangsfristen fra ISO 27001:2013 til 2022 udløb 31. oktober 2025 (uverificeret), så et 2013-certifikat fremvist i dag er ugyldigt; og er ISO 9001:2026 udkommet, får hvert leverandørcertifikat en treårig versionsovergang.

**Output:** Kørende verifikationsservice. ADR om uakkrediteret udsteder — fail open eller fail closed, og hvorfor. Regelsæt for versionsovergange. Og en note på én side til produktteamet. Det er den spike du kan bringe til arbejdet i næste uge uden at spørge om lov.

### 4. Spørgeskemaet og din Statement of Applicability (12-15 t)

Besvar CAIQ v4.1 eller MVSP ærligt mod dit eget system. Hvert "ja" skal have et evidenslink der virker; hvert "nej" bliver et backlog-punkt med et estimat. Skriv derefter en SoA for alle 93 bilag A-kontroller, anvendelig eller ej, med begrundelse for hver udeladelse. Ingen optimisme: kan du ikke pege på evidensen, er svaret nej. Seriens mest ubehagelige uge — og samtidig det artefakt der mest overbevisende beviser at du kan operere i overlappet. Læg den efter fire tekniske spikes; en SoA for et system der ikke findes, er en skriveøvelse.

**Output:** Udfyldt CAIQ/MVSP med evidenslinks. Komplet SoA. Prioriteret mangelregister. En optælling af hvor mange kontroller du kan *dokumentere* mod hvor mange du kan *påstå*.

### Øvelsen ved siden af: den faciliterede session

STRIDE kan læres på en weekend. Faciliteringen kan ikke, og det er den der er sjælden. Modellér først alene to gange på egne features. Rekruttér derefter to kolleger: "jeg vil gerne øve mig på noget, må jeg låne en time på jeres feature." Det er en anmodning om at lave arbejde, ikke om mandat, og den bliver næsten aldrig afvist. Timebox skænderier til to minutter, slut til tiden med ejer på hver linje, og skriv bagefter et halvsides retrospektiv om hvad der gik galt i **rummet**, ikke i modellen. Mål: tre sessioner på kode du ikke skrev.

## Trade-off-øvelsen der skiller arkitekt fra senior udvikler

Vælg ét rigtigt enterprise-krav, byg omkostningsmodellen i et regneark med tal fra Azure Pricing Calculator, og skriv memoet til en CFO. Én side, og det skal ende i en **regel**, ikke en holdning.

| Krav en stor kunde stiller | Hvad det koster | Ny fejlklasse | Beslutningsregel du skal turde skrive |
|---|---|---|---|
| Customer-managed keys | Key Vault-drift + implementeringsdage | Nøglerotation, tab af nøgle, utilgængelig vault vælter tenanten | "Nej, indtil første kunde over X i ARR betaler for det" |
| EU-dataresidens, sekundær region | Fordoblet storage + krydsregional trafik | Replikeringsforsinkelse, split-brain ved failover | "Ja hvis kunden er offentlig eller finansiel, ellers primær region plus dokumenteret residenspolitik" |
| Etårig audit-log-retention | Målt delta 30 vs. 90 vs. 365 dage | Kollision med art. 17-sletning i selvsamme log | "Audit-log 365 dage, diagnostisk log 30 — to forskellige stores" |

Forskellen mellem "vi bør bruge CMK, det er mere sikkert" og fjerde kolonne er forskellen mellem en senior udvikler og en arkitekt. Fejlklasse-kolonnen er den en senior udvikler glemmer.

## Certificeringer: hvad dette emne må koste

Landskabet flyttede sig i sommeren 2026, og flere gængse anbefalinger er nu forældede. Verificeret 10. september 2026 på learn.microsoft.com.

| Eksamen | Status | Tid | Pris | Dom |
|---|---|---|---|---|
| **SC-500** — Cloud and AI Security Engineer Associate | Aktiv. Udkom 21. juli 2026 og **erstatter AZ-500**, pensioneret 31. august 2026 | 45-60 t | Ca. USD 165 (uverificeret) | **Tag den.** Skills measured er identity/access/governance og storage/databases/networking — AZ-500's kerne med AI-workloads oveni. Hands-on på din stack, og alt i den bruger du i spikes alligevel |
| **SC-100** — Cybersecurity Architect Expert | Aktiv. Kræver nu én af SC-500, SC-200 eller SC-300 | 40-50 t | Som ovenfor | **Betinget.** Siger bogstaveligt "arkitekt", og SC-500 låser den op. Kun hvis porten i måned 9-10 siger du er foran |
| **AZ-305** (aktiv, opdateret 17. april 2026) og **AZ-400** (aktiv) | AZ-400's expert-titel kræver en aktiv associate-forudsætning | Budgetteres andetsteds | Som ovenfor | AZ-305 er ikke til forhandling hvis titlen er målet. Fælden ved AZ-400: AZ-204 blev pensioneret 31. juli 2026 og erstattet af det AI-drejede AI-200, så hvilke associate-certs der kvalificerer i dag, skal verificeres (uverificeret) |
| **CIPP/E** (IAPP) | Aktiv (uverificeret) | 50-70 t | Dyr, plus medlemskab | **Kun som tredje cert, kun hvis du er foran.** Ren viden uden praksis; er du bagud, ryger den først |
| ISO 27001 Lead Implementer | — | 5 kursusdage | 20-30.000 kr. (uverificeret) | **Spring over.** Køb standarderne og byg en SoA. Artefaktet slår certifikatet i et arkitektinterview |
| CISSP, CCSP, CISM, CRISC, CISA, CEH, OSCP, TOGAF, SAFe, Security+ | — | 0 t, det er pointen | — | **Spring over**, med begrundelse: de fem første kræver fem års erfaring, så værdien er netop den validering du ikke har. OSCP er 300+ timer i offensiv retning. TOGAF er enterprise- og ikke solution-arkitektur og bærer i danske produktvirksomheder et let negativt signal |

Tre certifikater og intet kørende system taber til ét certifikat og en driftet tjeneste. Certifikater er deadline-motor, ikke indhold.

## Sådan bliver det til arbejde uden at bede om mandat

I et ni-mandsfirma får du mandat ved at spørge stifteren direkte — men det meste her kræver slet ingen tilladelse.

- **Bed om første gennemløb på næste kundespørgeskema.** En anmodning om at lave kedeligt arbejde bliver næsten aldrig afvist. Efter to spørgeskemaer ved du mere om jeres faktiske sikkerhedsposition end de fleste i udviklingsteamet.
- **Byg svarbiblioteket efter det andet.** Hvert svar med evidens, ejer og sidst-reviewet-dato. Rent gavearbejde, og det gør dig til routingpunkt for en kommercielt kritisk opgave. Routingpunkter bliver arkitekter — ikke fordi nogen beslutter det, men fordi information begynder at gå gennem dem.
- **Tilføj en cross-tenant test til hver PR du laver.** Ikke et projektforslag. Bare en test der asserter at tenant B ikke kan læse tenant A's ressource på det endpoint du lige har rørt. Reviewere godkender tests. Om seks måneder er der en suite med dit navn på hver commit.
- **Læs kundekontrakterne og DPA'erne.** Indramningen der virker: "jeg vil gerne forstå hvad vi har lovet, så jeg ikke bygger noget der bryder det." Hvert hul mellem løfte og virkelighed er et memo — og et memo baseret på virksomhedens egen underskrift kan ikke afvises som en juniors mening.

**Det ene du skal bede om tilladelse til**, efter fire til seks måneders gavearbejde: rollen "sikkerheds- og compliance-kontaktpunkt for engineering". Ikke arkitekt — det er for tidligt og bliver afvist. En navngiven ansvarlighed koster ingenting, det er en rolle folk undgår, og det er en verificerbar CV-linje.

## Det eksterne modspil du får gratis her

Ingen på arbejdet kan give dig kvalificeret modspil på et designvalg, og planens største enkeltrisiko er at du øver dig forkert i tolv måneder uden at opdage det. Dette emne leverer sit eget modspil udefra. Et kundespørgeskema er en fjendtlig gennemgang af din arkitektur, skrevet af nogen der ved mere end dig og ikke har grund til at være venlig. Et auditopkald er halvfems minutters udspørgen fra en kundes sikkerhedschef; bed om at sidde med som referent, så du har legitim grund til at være i rummet uden at skulle præstere. Byg det ind som mål: to auditopkald som referent, fire besvarede spørgeskemaer.

## Faldgruber

1. **At blive compliance-manden i stedet for arkitekten.** Størst, derfor først. Aldrig et dokument uden en deployment.
2. **At samle på regulativer i stedet for at forstå ét system.** Dybde i én sporing slår bredde hver gang.
3. **At overingeniere isolationen.** Database-per-tenant "af sikkerhedshensyn" ved tyve tenants koster penge og troværdighed. Arkitektkompetencen der testes, er at vide hvornår man **ikke** skal.
4. **At skrive en trusselsmodel ingen bruger.** Bliver truslerne ikke til tickets med ejere og datoer, var det en skriveøvelse.
5. **At tale om compliance uden en måling.** "Jeg forstår GDPR" signalerer det modsatte. "Jeg byggede en sletteproces der gennemløber SQL, Blob og søgeindekset på fire minutter p95, og her er ADR'en om hvorfor vi ikke kan slette fra backups" vinder rummet.
6. **At lægge personoplysninger i logs og traces.** Den hyppigste GDPR-overtrædelse i engineering, begået af de samme udviklere der har skrevet databehandleraftalen. Antag det sker, og tjek efter.
7. **At påstå compliance virksomheden ikke har.** Et optimistisk svar skaber kontraktuel eksponering for din arbejdsgiver. Det korrekte svar er "nej, og her er vores roadmap", og det dræber handlen sjældnere end folk frygter.
8. **At udtale forældede tal med selvtillid.** Omnibus-tærsklerne har flyttet sig flere gange på to år. En superseded tærskel sagt med sikkerhed er en troværdighedsdræber.

## Sådan ved du at du kan det

- [ ] Du kan uden noter og på under tre minutter hver forklare hvad GDPR art. 28 og art. 32, NIS2 art. 21(2)(d) og ISO 27001 A.5.19-A.5.22 kræver — **og** navngive den konkrete kontrol i dit eget system der opfylder hver af dem.
- [ ] Cross-tenant abuse-testsuiten kører i CI, dækker hvert endpoint, og har fanget mindst én rigtig fejl. Gerne din egen.
- [ ] Der findes en komplet SoA over alle 93 bilag A-kontroller med skriftlig begrundelse for hver udeladelse.
- [ ] Tre faciliterede threat modeling-sessioner på kode du ikke skrev, hver med tickets der efterfølgende blev lukket.
- [ ] Du kan sige hvad dit system koster per tenant per måned, og har ét trade-off-memo hvor konklusionen var en regel og ikke en holdning.
- [ ] Fire rigtige kundespørgeskemaer besvaret, og et svarbibliotek andre bruger.
- [ ] Dit navn optræder i et LeanLinking-dokument som en **kunde** ser: et spørgeskemasvar, et DPA-bilag, en arkitekturbeskrivelse, et auditsvar.
- [ ] Mindst én uden for dit team har spurgt dig "er det et problem hvis vi...". Det er det første rigtige tegn på arkitektstatus, og det kan ikke fremtvinges, kun fortjenes.
- [ ] Du kan nævne tre ting du troede for seks måneder siden og nu mener var forkerte. Kan du ikke det, har du læst og ikke bygget.

## Verifikationsgæld

Tjek selv i primærkilden før du udtaler dig. Rækkefølgen er efter hvor hurtigt en fejl koster troværdighed.

| Emne | Hvad der mangler | Hvor |
|---|---|---|
| CRA-rapporteringspligt | Datoen 11. september 2026 (uverificeret), og om ren SaaS er uden for scope — enhver downloadbar komponent eller on-prem-konnektor trækker jer ind | EUR-Lex |
| AI Act, højrisiko | Originaldatoen var 2. august 2026; en udskydelse var i trilog. Om den blev vedtaget, haster mest (uverificeret) | EUR-Lex |
| NIS2 i Danmark | Lovens navn, ikrafttrædelse og bekendtgørelsesnumre (uverificeret). Dansk ret om et dansk produkt — værre at tage fejl her end om et direktiv | retsinformation.dk, sikkerdigital.dk |
| Omnibus-tærskler, ISO 9001:2026, OWASP Top 10/ASVS | Endelige CSRD/CSDDD-tal; om ISO-revisionen er udkommet; hvilken OWASP-version der er aktuel | EUR-Lex, Dansk Standard, owasp.org |
| Lønniveauer | Træk selv tallene: IDA's lønstatistik, PROSA, samt lønguides fra Hays, Robert Half og Michael Page — bureauernes som loft, ikke median | ida.dk, prosa.dk |
