# C07 — Guardrail uden mandat

| | |
|---|---|
| **Type** | Governance uden autoritet |
| **Primært modul** | 07 — Governance: at styre uden at kvæle |
| **Sekundære moduler** | 12 (Mandat, bredde og overgangen til fuldtid), 11 (Kommunikation og indflydelse), 03 (Azure-arkitektur) |
| **Timebox** | 5 timer, hård. Præmisskiftet lægges oveni og må koste maks. 40 minutter ekstra |
| **Sværhedsgrad** | 4 af 5. Teknikken er en eftermiddag; det svære er at indføre en begrænsning der rammer to kolleger med længere anciennitet end dig, uden at nogen bliver din modstander. Giver mening i **måned 4-8**: før måned 4 har du ikke bygget G1, og så bliver håndhævelsestrappen et citat i stedet for noget du har målt; efter måned 9 har kompetenceporten allerede spurgt til den. Bedst i **måned 5-6**. Kør den igen i måned 11 med samme rubrik |
| **Afleveringsformat** | Ti artefakter: kravsspørgsmål (1 side, tidsstemplet), målt nulpunkt (regneark + 0,5 side), policy-as-code i git (repo + `measurements.md`), håndhævelsestrappen (1 side), fravalgslisten (0,5 side), ADR (maks. 1,5 side, MADR-minimal), notat til Jens (præcis 1 side, ikke-teknisk), beskeden til Thomas og Rasmus (maks. 120 ord, ordret), udkast til svar til Fjordhus (maks. 1 side, ekstern ikke-teknisk læser), selvvurdering (0,5 side). I alt maks. 6 sider brødtekst, ét regneark og ét repo |

> Alle personer, kunder og hændelser i denne case er opdigtede. Beløb, ressourceantal og målte tal er konstrueret, men i den størrelsesorden en dansk ni-mandsvirksomhed med et multi-tenant SaaS på Azure reelt ligger i. **Slå ikke policy-definitions-ID'er, SKU-navne eller regionslister op midt i timeboxen.** Casen kan ikke løses ved at finde det rigtige indbyggede initiativ. Skal et definitions-ID stå i en Bicep-fil du afleverer, markerer du det som ukontrolleret og verificerer efter timeboxen. Det er i øvrigt præcis den disciplin casen måler. Og én regel gælder ubetinget: **du kører ikke et scanningsværktøj mod LeanLinkings produktionstenant i denne case.** Gør du det alligevel, er casen dumpet, uanset hvad rubrikken ellers siger.

## Situationen

Mandag den 14. september 2026, kl. 09.10. Ingen har bedt dig om noget.

Fredag eftermiddag sad du med en ticket om en fejlet natkørsel på Nordbjerg Industris ERP-integration. Undervejs faldt du over et Service Bus-namespace der ligger i `swedencentral`. Du kiggede videre. Der er også fem ressourcer i `eastus`, og en af dem er en Document Intelligence-konto der læste leverandørcertifikater fra marts til maj. Ingen af de to ting fremgår af noget dokument du har kunnet finde.

I marts kunne Rasmus ikke få den modelversion han skulle bruge til at trække udløbsdatoer og akkrediteringsnumre ud af uploadede ISO- og IATF-certifikater. Han fandt en vejledning, oprettede kontoen dér hvor vejledningen sagde, og gik videre. I august skulle Thomas have Nordbjergs Infor M3-forbindelse op inden deres kvartalsskifte. Han oprettede en resource group i portalen, kørte den Bicep-fil I bruger til ERP-konnektorer, og den lagde tingene hvor resource groupen lå.

Jens sagde i køkkenet i fredags, uden at du havde spurgt, at "vi har jo en regel på det der med regioner — jeg satte noget op dengang vi startede". Han var mere optaget af regningen. Augustregningen fra Azure lød på 61.400 kr. ekskl. moms. I marts var den 44.200. Han spurgte, halvt i luften, hvem af kunderne der egentlig står for stigningen. Ingen kunne svare, og samtalen gik videre til noget andet.

Thomas skrev den 4. juni i udviklerkanalen at han tager en tagging-oprydning i uge 33, så I kan se hvad tingene koster. Uge 33 lå i august. Han nævnte det igen den 2. september: den ligger klar, han mangler bare at få den kørt. Han har været her i elleve år, han byggede deploy-pipelinen, og han er den eneste der ved hvorfor tre af jeres resource groups hedder det de gør.

Rasmus skal i uge 40 til 42 sætte den samme ERP-konnektor op for tre kunder til: Fjordhus Retail Group på Dynamics 365, Vestjysk Plast på SAP-IDoc, og et norsk emne Katrine er tæt på. Han holder ferie fra den 12. til den 19. oktober. Han ved ikke at du har kigget.

I fredags videresendte Katrine en mail fra Helle Brix, kvalitetschef hos Fjordhus. Fjordhus har surveillance audit på deres eget ISO 27001-certifikat den 6. og 7. oktober, og deres revisor har bedt om dokumentation fra deres kritiske leverandører. Helle skal bruge tre ting senest **fredag den 25. september**: hvilke Azure-regioner Fjordhus' data ligger og behandles i, hvilke underdatabehandlere der er, og en bekræftelse på at der ikke overføres personoplysninger uden for EU/EØS. Katrine har svaret Helle at hun nok skal klare det. Katrine har ikke spurgt dig om noget.

Du har Reader på produktionsabonnementet siden den 9. juni, fordi du bad om det med den formulering der ikke kan afvises. Du fik Cost Management Reader den 21. august. Du har ingen skriveadgang nogen steder.

Der er ingen der har bedt dig om at gøre noget ved noget af det her.

Du har fem timer.

## Det du skal aflevere

| # | Artefakt | Format | Krav der ikke kan forhandles |
|---|---|---|---|
| 1 | **Kravsspørgsmål** | 1 side, tidsstemplet pr. spørgsmål | Skrevet **før** første policy-navn, første tag-navn og ordet "deny". Hver linje har en note om hvad svaret ville ændre |
| 2 | **Målt nulpunkt** | Regneark + 0,5 side | Mindst fire tal med metode (query, kilde, dato) og et **spænd**: antal ressourcer, tag-dækning i procent, ressourcer uden for de tilladte regioner, og kroner. Gættede tal mærkes som gæt i regnearket |
| 3 | **Policy-as-code** | Repo med `infra/policy/` i Bicep + `measurements.md` | Deployet til **dit eget** abonnement, ikke firmaets. Mindst ti bevidst non-compliante ressourcer, compliance-procent før og efter, og **målt varighed** på remediation-kørslen med antal kørsler |
| 4 | **Håndhævelsestrappen** | 1 side, tabel | Tre trin. Hvert trin har: hvad der udløser det (et tal), en dato, en navngiven ejer og en udløbsdato på selve reglen |
| 5 | **Fravalgslisten** | 0,5 side | Mindst fire ting der **ikke** skal styres, hver afvist på én navngiven, målbar akse med et tal |
| 6 | **ADR** | Maks. 1,5 side, MADR-minimal | Mindst to navngivne afviste alternativer. Afsnittet "Dette ville få os til at vælge om" med mindst tre betingelser, hver med tærskel og enhed |
| 7 | **Notat til Jens** | Præcis 1 side | Nul jargon. Ordene *governance*, *policy*, *compliance* og *teknisk gæld* må ikke optræde. To muligheder med pris, én anbefaling, og hvad han kan sige til en kunde i morgen |
| 8 | **Beskeden til Thomas og Rasmus** | Maks. 120 ord, ordret som den ville blive sendt | Skal kunne sendes som den står. Skal indeholde mindst ét tal i minutter eller timer om hvad det sparer **dem** |
| 9 | **Udkast til svar til Fjordhus** | Maks. 1 side, til Katrines underskrift | Ekstern, ikke-teknisk læser. Skal angive hvad vi ved, hvad vi ikke ved, og hvornår det ukendte er afklaret. Ingen kontraktbegreb du ikke har læst i vores egen kontrakt |
| 10 | **Selvvurdering** | 0,5 side | Hvilke af dine egne kravsspørgsmål endte du med at besvare med et gæt, og hvilken påstand i artefakt 7 og 9 hviler på det gæt |

**Artefakt 2 og 3** er dem der har tal med angivet usikkerhed. **Artefakt 7 og 9** skrives til ikke-tekniske læsere, og artefakt 9 er det eneste af de ti der forlader huset. **Artefakt 8 er casens sværeste halve side** — den er ikke en formalitet, den er hele testen af om det bliver oplevet som en hjælp.

## Skjulte oplysninger

Du må kun læse svaret på et spørgsmål, du **faktisk har skrevet ned** på artefakt 1, før du begyndte at designe. Skriver du fem spørgsmål og læser fjorten svar, har du ikke lavet casen — du har læst en løsning, og du kan ikke score over 1 på K1 og K2.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Findes der allerede en regel om regioner, og hvem har ændret den? | **Ja.** Det indbyggede initiativ om tilladte lokationer blev assignet på produktionsabonnementet den 3. februar 2021 af Jens, i Enforce, med to tilladte lokationer: `westeurope` og `northeurope`. Activity Log viser resten: `eastus2` tilføjet 19. november 2023 af Thomas til en demo for et amerikansk lead; **`eastus` tilføjet 11. marts 2026 kl. 16.42 af Rasmus — dagen før hændelse 1**; `swedencentral` tilføjet 27. august 2026 kl. 09.05 af Thomas, tolv minutter før han deployede. Der er tre exemptions: én fra 2022 uden udløb, én der udløb 30. juni 2024 og stadig står, og én oprettet 27. august for Nordbjergs resource group. Reglen har aldrig fejlet. Den blev udvidet, hver gang den var i vejen, og det tog under et minut |
| 2 | Hvad står der **ordret** i kundernes kontrakter om datalokation? | Den generiske databehandleraftale på hjemmesiden siger "inden for EU/EØS". Bilag 2 i de tre største kontrakter — Fjordhus, Nordbjerg og Indkøbsfællesskab Midtjylland — navngiver derimod konkret: *"Microsoft Azure, West Europe (Holland) og North Europe (Irland)"*. Samme bilag kræver **30 dages skriftligt varsel** ved tilføjelse eller ændring af en underdatabehandler eller en behandlingslokation. `swedencentral` ligger i EU og er derfor ikke et tredjelandsproblem — men det står ikke i bilag 2, og varslet er ikke givet. Det er et kontraktbrud, ikke et GDPR-brud, og de to skal håndteres forskelligt |
| 3 | Hvor mange ressourcer er der, og hvor mange har tags i dag? | 3 abonnementer, 41 resource groups, **312 ressourcer**. 31 af dem (9,9 %) har mindst ét tag. Der er otte forskellige tag-nøgler i brug, hvoraf fire er stavevarianter af det samme: `Miljø`, `miljoe`, `Environment`, `env`. Værdierne er heller ikke normaliserede — seks skrivemåder af "produktion". Tolv ressourcer har `Owner` med en mailadresse; to peger på Aleks Rytter, der stoppede 28. februar 2025, og én på en fællespostkasse ingen læser. Regionsfordeling: `westeurope` 231, `northeurope` 62, `swedencentral` 11, `eastus` 5, `global` 3 |
| 4 | Hvor stor en del af regningen kan overhovedet henføres til én kunde med et tag? | **22 %.** Af de 61.400 kr. ligger 13.600 kr. i ressourcer der tilhører præcis én kunde: et dedikeret storage account (5.400), Nordbjergs `swedencentral`-fodaftryk (2.800), en anden kundes ERP-fodaftryk (2.100) og en dedikeret App Service Plan til en white-label-portal (3.300). De resterende **47.800 kr. (78 %)** ligger i delte ressourcer: SQL elastic pool 18.900, to delte App Service Plans 8.100, delt blob-storage 9.100, Log Analytics og App Insights 7.300, backup og langtidsretention 4.800, Front Door 1.500, uklassificeret 4.100. Ingen tag i verden fordeler dem. Det kræver en forbrugsmodel med proxies: lagrede dokumenter, integrationskørsler, GB pr. tenant |
| 5 | Hvad driver stigningen fra 44.200 til 61.400 kr.? | Stigningen er 17.200 kr., og der er ikke én skyldig. Log Analytics og App Insights: **+4.900 kr. (28 %)** — logniveauet på ERP-konnektoren har stået på verbose siden en hændelse 11. juni, og ingestion gik fra ca. 160 til ca. 490 GB/md. Storage og backup-retention: **+5.200 kr. (30 %)** — revisionssporet er append-only og krymper aldrig, og dokumentmængden er vokset med tre nye kunder. Nye fodaftryk: **+5.100 kr. (30 %)**. Prisreguleringer og resten: **+2.000 kr. (12 %)**. Det tal Jens gerne vil have, kan altså ikke fremskaffes af noget tag |
| 6 | Hvad skete der præcis den 12. marts? | Rasmus oprettede en Document Intelligence-konto i `eastus`, fordi den vejledning han fulgte sagde at modellen var tilgængelig dér først. Den behandlede **1.847 leverandørdokumenter** mellem 12. marts og 7. maj: ISO 9001- og 14001-certifikater, IATF-certifikater, BRCGS-rapporter og et par forsikringsbeviser. Diagnostic settings var slået til med kategorien for request/response, og de logs ligger i et Log Analytics workspace der **også** ligger i `eastus` og **stadig eksisterer** med 4,2 GB data og default retention. Selve kontoen blev sat på pause den 7. maj. Den blev ikke slettet |
| 7 | Forlod der personoplysninger EU i marts-maj? | **Det ved vi ikke.** Ingen har kørt en query mod det workspace. Vi ved ikke om de 4,2 GB indeholder dokumenttekst eller kun metadata, og vi ved ikke om kontaktpersoner, underskrivere eller auditornavne er med. Der findes ingen fortegnelse efter art. 30 for behandlingen, og der er ikke lavet en risikovurdering. Der er en yderligere krølle: at læse i loggen for at finde ud af det, er i sig selv en behandling, og der er ingen der har taget stilling til hvem der må gøre det. Det er ikke en oplysning der kan hentes på en time. **Det er et arkitekturvilkår du skal skrive ind i svaret til kunden som et åbent punkt med en dato** |
| 8 | Hvad koster det at flytte `swedencentral`-fodaftrykket? | Et Service Bus-namespace kan ikke flyttes mellem regioner; det skal genskabes og køen drænes. Anslået 6-9 timer af Rasmus, et vindue hvor Nordbjergs natkørsel ikke kører, og en besked til kunden. Storage-kontoen kan heller ikke flyttes: 1.100 blobs, 3,4 GB, kopiering ca. 40 minutter plus omlægning af forbindelsesstrenge. **Men tre af de 1.100 blobs er under legal hold** i forbindelse med en claims-sag mellem Nordbjerg og en af deres leverandører. De kan kopieres. De kan ikke slettes før holdet ophæves, forventeligt i første kvartal 2027. "Flyt og slet det gamle" er altså ikke en mulighed før da |
| 9 | Hvad har Thomas lovet, hvornår, og hvad ligger der? | Den 4. juni i udviklerkanalen: *"Jeg tager en tagging-oprydning i uge 33 så vi kan se hvad tingene koster."* Uge 33 var 10.-16. august. Der ligger en branch `chore/tagging` fra 14. august med et PowerShell-script på 190 linjer der sætter `Owner` og `Miljø` på ressourcerne i én resource group. Det er kun kørt i hans eget sandbox-abonnement. Han nævnte det igen den 2. september. Ekstra kontekst du kun får hvis du spørger til hans holdning: på hans forrige arbejdsplads, et større dansk energiselskab, blokerede et centralt platformsteams deny-regel hans deployments i tre dage. Han siger ordet "policy" med et hørbart suk |
| 10 | Hvad sker der, hvis man spørger Jens om lov? | Han siger ja på cirka fyrre sekunder, uden at læse noget, og han husker det ikke to uger senere. To udviklere har inden for det seneste år fået overlappende ja'er til det samme område. Det han faktisk reagerer på, er augustregningen og et spørgsmål fra en kunde han ikke kan svare på. Han har sagt højt to gange i år: *"Jeg vil ikke have flere processer."* At bede om lov er altså billigt og næsten værdiløst. Begrænsningen er ikke tilladelse — den er at ingen må opleve det som noget de har fået trukket ned over hovedet |
| 11 | Hvilken adgang har du helt præcist? | Reader på produktionsabonnementet siden 9. juni. Cost Management Reader på faktureringsscope siden 21. august. Reader på testabonnementet. **Ingen skriveadgang overhovedet.** Du kan ikke oprette en policy assignment — det kræver Resource Policy Contributor eller Owner. Du kan ikke oprette management groups — det kræver en rolle på tenant root som kun Jens har. Du kan læse Resource Graph på de scopes du har Reader til, og du kan læse Activity Log 90 dage tilbage. Du kan altså **måle alt** og **deploye ingenting**. Og du må ikke køre et scanningsværktøj mod produktionstenanten uden skriftlig aftale |
| 12 | Hvad er Rasmus' plan de næste tre uger? | Han sætter den samme ERP-konnektor op for tre kunder i uge 40-42: Fjordhus på Dynamics 365 F&O, Vestjysk Plast på SAP-IDoc, og et norsk emne. Han bruger `infra/erp-connector/main.bicep`, hvor der står `param location string = resourceGroup().location`, og der er ingen tags-blok i filen. Han opretter resource groupsene i hånden i portalen. De sidste tre gange tog efterarbejdet — det der skal rettes bagefter, når noget fejler — henholdsvis 22, 41 og 18 minutter; ingen har målt det systematisk, tallene står i hans egne noter. Han er på ferie 12.-19. oktober, og han ved endnu ikke at du har fundet noget |
| 13 | Hvad har Fjordhus bedt om, og hvad sker der hvis vi ikke svarer? | Helle Brix, kvalitetschef, skal bruge tre ting senest fredag den 25. september: regionsliste, underdatabehandlerliste og en bekræftelse om EU/EØS. Fjordhus' egen surveillance audit ligger 6.-7. oktober. Får hun ikke et brugbart svar, skriver revisor en **nonconformity** på Fjordhus' egen leverandørstyring, ikke på os — men den bliver til en **CAPA** med 60 dages lukkefrist, og lukningen kræver dokumentation fra os alligevel, plus en genverifikation. Fjordhus står for ca. 8 % af omsætningen. Katrine har fået spørgsmålet videresendt og har svaret Helle at hun klarer det |
| 14 | Hvad ville det koste at gøre den rigtige vej **hurtigere** end den nemme? | Ingen har målt det. Den nuværende vej: resource group oprettes i hånden i portalen (ca. 2 minutter), `az deployment group create` mod den delte `main.bicep` (ca. 7 minutter), derefter efterarbejde (22, 41 og 18 minutter de sidste tre gange). Der findes ingen parameterfil pr. kunde. Et modul med lokation og de obligatoriske tags bagt ind, plus en `.bicepparam` pr. kunde, er anslået 4-6 timers arbejde og ville fjerne det manuelle trin helt. Det tal er ikke efterprøvet af nogen |

## Præmisskiftet

**Åbnes først når 3 timer af timeboxen er gået (60 %). Ikke før. Sæt en timer.**

Onsdag den 16. september kl. 11.20. Jens har videresendt dit notat — det du skrev til ham, internt, med dine fund i — til Helle Brix hos Fjordhus, med Katrine og Thomas i kopi. Han har skrevet tre linjer over: *"Vi har fuldt overblik. Simon har lavet en gennemgang og sætter reglerne op i næste uge, så det ikke kan ske igen. Vend tilbage hvis I mangler noget."* Fire ting følger.

1. **Dit interne dokument er nu en ekstern forpligtelse med en dato.** Ordret, inklusive sætningen om at ingen har set i det workspace der ligger i `eastus`. Helle Brix har kvitteret og skrevet at hun sender det videre til revisor som bilag.
2. **Du har fået Owner på produktionsabonnementet.** Jens tildelte den i går aftes "så du kan komme videre". Du har ikke bedt om den. Rasmus fandt ud af det, fordi Azure sendte ham en mail om rolletildelingen, og han har skrevet ét spørgsmålstegn i udviklerkanalen. Thomas har ikke skrevet noget.
3. **Katrine har allerede svaret på Helles spørgsmål to.** Mandag kl. 15.40 sendte hun underdatabehandlerlisten fra den generiske databehandleraftale: "West Europe (Holland), North Europe (Irland)". Det er dateret, sendt og forkert.
4. **Jens har sat et tal på regningen.** I samme tråd: *"Og find ud af hvad der driver de 61.400 — jeg vil have den under 50 til november."* Det er 11.400 kr. om måneden, og de tre nye ERP-fodaftryk i uge 40-42 trækker den anden vej.

**Hvad skiftet er en test af**

- Om du **indsnævrer løftet skriftligt** i stedet for at leve op til det. Jens har lovet Fjordhus noget du ikke har lovet, på en dato du ikke har sat. En stærk besvarelse skriver rettelsen og sender den gennem Katrine eller Jens, uden at trække noget tilbage — den tilføjer.
- Om du **håndterer Owner-rollen som et problem, ikke som en gevinst.** Modulets hårdeste advarsel handler om præcis denne rolle på præcis dette abonnement. Beholder du den ubetinget, har du fået det du ville have, på den dyreste måde der findes: over hovedet på de to der har været her længst.
- Om du går til **Thomas og Rasmus før du rører noget** med den nye adgang. Din stilling blev forringet af din egen sponsor kl. 11.20. De 120 ord fra artefakt 8 er ikke længere de rigtige 120 ord.
- Om **audit → modify → deny overlever presset.** Jens har skrevet "sætter reglerne op i næste uge". Den nemme reaktion er at deploye Deny på regioner og tags i denne uge, før Rasmus' tre deployments. Det ville brække alle tre.
- Om **din egen faldsbetingelse udløses** af punkt 2 eller punkt 4 — og om du så følger den, eller finder en grund til at lade være.
- Om de 11.400 kr. ændrer **hvad** du gør, ikke bare hvor meget. Det største enkeltgreb ligger i logniveauet fra 11. juni og i retentionen, og ingen af delene har noget med tags eller regioner at gøre. Kan du sige det højt, uden at dit eget arbejde bliver mindre relevant af det?

## Rubrik

Tolv kriterier, hvert scoret 0-3, med vægt. Maksimum er **102 point**. Ankrene er tællelige med vilje: en bedømmer skal kunne sætte scoren uden at kende kandidaten og uden at bruge ordet "god".

| # | Kriterium | Vægt | Maks. |
|---|---|---|---|
| K1 | Kravsspørgsmål før første policy-navn | 3 | 9 |
| K2 | Spørgsmålene rammer de akser der vælter designet | 2 | 6 |
| K3 | Nulpunktet: antal, dækning og kroner med spænd | 3 | 9 |
| K4 | Omkostningsfordelingen: hvad et tag kan og ikke kan | 3 | 9 |
| K5 | Guardrail frem for gatekeeper, målt på tid | 3 | 9 |
| K6 | Progressionen audit → modify → deny, med tal og datoer | 3 | 9 |
| K7 | Fravalget: hvad der ikke styres | 3 | 9 |
| K8 | Faldsbetingelsen og reglens udløbsdato | 3 | 9 |
| K9 | Adgang, mandat og den hårde advarsel | 3 | 9 |
| K10 | Formuleringen der ikke skaber en modstander | 3 | 9 |
| K11 | Det eksterne svar: at rette en afgivet erklæring | 2 | 6 |
| K12 | Iteration ved præmisskiftet | 3 | 9 |
| | **I alt** | **34** | **102** |

### K1 — Kravsspørgsmål før første policy-navn (vægt 3)

*Findes fordi:* det her er det emne hvor det er allersværest at lade være med at begynde med løsningen. Du kender syntaksen. Det tager tyve minutter at skrive initiativet, og så har du løst det forkerte problem.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen spørgsmålsliste, eller den er skrevet bagefter. Et policy-navn, et tag-navn eller ordet "deny" optræder inden for de første 20 minutter |
| 1 | 3-7 spørgsmål, ikke tidsstemplede, og mindst ét er et løsningsforslag i spørgeform ("skal vi ikke sætte deny på regioner?") |
| 2 | 8-11 tidsstemplede spørgsmål skrevet før første policy-navn, mindst fem rammer skjulte oplysninger, hver med en note om hvad svaret ville ændre |
| 3 | 12+ tidsstemplede spørgsmål, mindst otte rammer skjulte oplysninger, listen er gennemgået igen til sidst, og det står markeret hvilke der **stadig** er ubesvarede i artefakt 7 og 9, og hvilken påstand der derfor hviler på et gæt |

### K2 — Spørgsmålene rammer de akser der vælter designet (vægt 2)

*Findes fordi:* tolv spørgsmål om tag-navne er ét spørgsmål. De seks dyre akser er: findes reglen allerede og hvem har ændret den; hvad står der ordret i kundekontrakterne; hvilken adgang har jeg faktisk; hvor stor en del af regningen kan overhovedet henføres; hvad sker der i uge 40-42; og hvem har allerede lovet at gøre det her.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen af de seks akser berørt |
| 1 | 1-2 af de seks |
| 2 | 3-4 af de seks, og mindst ét spørgsmål indeholder selv et tal ("hvor mange af de 312 ligger uden for de to regioner i bilag 2?") |
| 3 | Mindst fem af de seks, plus mindst ét spørgsmål der ville have afdækket at regionsreglen blev **udvidet** før hver af de to hændelser, og mindst ét formuleret som det skal stilles til Jens eller Katrine, ikke til en kollega |

### K3 — Nulpunktet: antal, dækning og kroner med spænd (vægt 3)

*Findes fordi:* uden tal er det en mening, og en junior-mening om andres arbejde er den dyreste ting du kan sige i et hus på ni.

| Score | Sådan ser det ud |
|---|---|
| 0 | Intet målt nulpunkt, eller tallene er afskrevet fra briefet uden metode |
| 1 | Antal ressourcer og tag-dækning nævnt som ét tal uden metode og uden spænd |
| 2 | Mindst fire målte tal, hvert med metode (query, kilde, dato) og et spænd: ressourceantal, tag-dækning i procent, ressourcer uden for de tilladte regioner, kroner. Gæt er mærket som gæt |
| 3 | Derudover: målt igen efter modify-/remediation-kørslen i eget abonnement, med compliance-procent før og efter og **målt varighed** med antal kørsler; og mindst ét tal hvor det står hvorfor spændet er så bredt som det er |

### K4 — Omkostningsfordelingen: hvad et tag kan og ikke kan (vægt 3)

*Findes fordi:* casens overskrift lyder "ingen kan se hvilken kunde der betaler for hvad, fordi tags mangler". Den sætning er delvist falsk, og hele Jens' spørgsmål hænger på det.

| Score | Sådan ser det ud |
|---|---|
| 0 | Antager at tags vil vise hvad hver kunde koster |
| 1 | Noterer at noget af forbruget er delt, uden et tal |
| 2 | Deler regningen i henførbar og ikke-henførbar med kroner, procent og et spænd, og navngiver mindst én forbrugsproxy for den delte del |
| 3 | Derudover: proxyens fejl er navngivet (hvem den overbelaster og undervurderer, og cirka hvor meget), det står hvilket spørgsmål tallet er godt nok til at besvare og hvilket det ikke er, og der står hvad det koster i udviklertimer pr. måned at holde modellen sand |

### K5 — Guardrail frem for gatekeeper, målt på tid (vægt 3)

*Findes fordi:* den målbare test er forskellen mellem tid-til-compliant-miljø og tid-til-non-compliant-miljø. Er den compliante vej langsommere, træner du folk i at rute uden om — og casen indeholder allerede beviset på at det er præcis det der er sket fire gange siden 2021.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forslaget er at nogen skal godkende, at der skal være en tjekliste, eller at "vi aftaler at" |
| 1 | Automatiseret regel, men ingen udtalelse om hvad den koster den der deployer |
| 2 | Angiver målt eller estimeret tid for den rigtige vej mod den nemme vej, og mindst ét greb gør den rigtige vej **hurtigere** — et modul, en parameterfil, en resource group der oprettes for dig |
| 3 | Derudover: tiden er målt i eget abonnement med et tal og et spænd; mindst ét eksisterende manuelt trin **fjernes** i stedet for at der lægges et til; og det står skriftligt hvordan han forsøgte at omgå sin egen kontrol, og hvad det krævede |

### K6 — Progressionen audit → modify → deny, med tal og datoer (vægt 3)

*Findes fordi:* foreslår du Deny først, er du "ham med policyerne" i to år, og casen har lige vist at en Deny-regel uden ejer bliver udvidet på fyrre sekunder.

| Score | Sådan ser det ud |
|---|---|
| 0 | Deny foreslås først, eller der er ingen trapper — bare "en policy" |
| 1 | Nævner audit før deny, men uden tal, dato eller ejer |
| 2 | Tre navngivne trin, hvert med: hvad der udløser trinnet (et tal), en dato og en navngiven ejer. `enforcementMode` er brugt bevidst og det står hvorfor |
| 3 | Derudover: audit har faktisk kørt mod rigtige ressourcer i eget abonnement med compliance-procent før og efter; det står hvilken **ene** regel der går i Deny nu og hvorfor netop den; og der står hvad der ville få ham til at tage en regel **ud** af Deny igen |

### K7 — Fravalget: hvad der ikke styres (vægt 3)

*Findes fordi:* fire obligatoriske tags er meget, otte er nul. Og en governance-plan uden et fravalg er en ønskeseddel med Bicep-syntaks.

| Score | Sådan ser det ud |
|---|---|
| 0 | Alt skal styres, eller listen over obligatoriske tags er på seks eller flere |
| 1 | 1-2 fravalg, afvist på smag ("det er overkill") |
| 2 | Mindst fire navngivne fravalg, hvert afvist på én navngiven, målbar akse med et tal |
| 3 | Derudover: for hvert obligatorisk tag kan han navngive den rapport eller query der **læser** det, og hvem der læser den; mindst ét fravalg er noget han selv gerne ville have gjort; og mindst én allerede eksisterende regel foreslås **fjernet** med en begrundelse |

### K8 — Faldsbetingelsen og reglens udløbsdato (vægt 3)

*Findes fordi:* hver regel uden ejer og udløbsdato er permanent, og en beslutning uden en betingelse der vender den er en begrundelse, ikke en beslutning.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen faldsbetingelser |
| 1 | "Vi tager det op igen hvis det ikke virker" — ingen tærskel, ingen enhed, ingen dato |
| 2 | Mindst tre faldsbetingelser, hver med tærskel, enhed og målepunkt. Hver indført regel har navngiven ejer og udløbsdato |
| 3 | Derudover: mindst én faldsbetingelse ville få ham til at **fjerne** en guardrail igen, ikke stramme den; mindst én udløses af noget uden for hans kontrol; og efter præmisskiftet står der hvilken af dem der faktisk blev udløst |

### K9 — Adgang, mandat og den hårde advarsel (vægt 3)

*Findes fordi:* det er det eneste sted i hele planen hvor du kan komme i alvorlige problemer i stedet for at fremme dig selv.

| Score | Sådan ser det ud |
|---|---|
| 0 | Antager skriveadgang i produktion, eller har kørt et scanningsværktøj mod produktionstenanten. Sidstnævnte dumper hele casen |
| 1 | Noterer at han mangler adgang, og løsningen er at bede Jens om Owner |
| 2 | Angiver præcis hvilken adgang han har, hvad han gjorde med den uden at spørge nogen, hvad han **ikke** gjorde og hvorfor. Policy-as-code er deployet og målt i eget abonnement |
| 3 | Derudover: det han beder om er det mindste der låser ham op, tidsbegrænset og scoped til ét abonnement eller én resource group, med den ordret formulering; det står hvad han gør hvis svaret er nej; og det står skriftligt hvad han **afstod** fra at køre mod produktion, og hvorfor |

### K10 — Formuleringen der ikke skaber en modstander (vægt 3)

*Findes fordi:* Thomas har været her i elleve år, har allerede lovet det her offentligt, og har et dårligt minde om ordet policy. Rasmus' arbejdsgang er den der ændrer sig. Ingen af dem har bedt om noget.

| Score | Sådan ser det ud |
|---|---|
| 0 | Et dokument navngiver hvem der forårsagede hændelserne, eller beskeden til kollegerne er et forslag om en proces |
| 1 | Neutralt formuleret, men Thomas' løfte og hans branch er slet ikke nævnt — der er gået udenom |
| 2 | Maks. 120 ord til Thomas og Rasmus, som indeholder: hvad det koster **dem** i minutter eller timer, hvad der forsvinder fra deres arbejde, og et sted hvor Thomas' eksisterende script eller branch bruges eller krediteres. Ordene *governance*, *policy* og *compliance* optræder ikke |
| 3 | Derudover: mindst én ting gives væk eller bedes om som hjælp frem for at blive annonceret; beskeden kan sendes som den står; mindst én regel har en navngiven ejer der ikke er ham selv; og notatet til Jens beskriver ikke hændelserne som nogens fejl, men **udvidelsesvejen** som en designfejl, med Activity Log som kilde |

### K11 — Det eksterne svar: at rette en afgivet erklæring (vægt 2)

*Findes fordi:* Katrine har sendt noget forkert med dato på, og der er et åbent ukendt der ikke kan lukkes inden den 25. september.

| Score | Sådan ser det ud |
|---|---|
| 0 | Udkastet siger at alle data ligger og har ligget i West Europe og North Europe |
| 1 | Nævner de to hændelser, men beskriver dem som lukkede uden evidens |
| 2 | Udkastet angiver i ikke-teknisk sprog: hvilke regioner, hvilke underdatabehandlere, hvad der skete i de to tilfælde, hvad der rettes og hvornår, og hvad der **stadig er ukendt** med datoen for hvornår det er afklaret. Det står hvem der skriver under, og at Katrines svar fra mandag skal korrigeres |
| 3 | Derudover: rettelsen er formuleret så den kan sendes uden at bede Fjordhus genåbne noget; varslingsbestemmelsen om underdatabehandlere er håndteret eksplicit; og det står hvad der sker hvis svaret alligevel udløser en nonconformity hos Fjordhus — og hvorfor det stadig er det billigste udfald |

### K12 — Iteration ved præmisskiftet (vægt 3)

*Findes fordi:* det er det ene observerbare kriterium på dømmekraft der ikke kan fabrikeres bagefter.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forsvarer den eksisterende plan. Sætningen "det havde jeg egentlig taget højde for" optræder |
| 1 | Justerer noget, men tager Jens' eksterne leveringsdato for givet og planlægger efter den |
| 2 | Inden for 40 minutter: en omskrevet plan der (a) navngiver hvad der **ikke** ændrer sig, (b) håndterer Owner-tildelingen eksplicit, (c) angiver hvilken af hans egne faldsbetingelser skiftet udløser |
| 3 | Derudover: det eksterne løfte indsnævres **skriftligt** i stedet for at blive indfriet; han går til Thomas og Rasmus før han rører noget med den nye adgang, og de 120 ord omskrives fordi situationen er en anden; og mindst én tidligere beslutning bliver eksplicit omgjort med en begrundelse, ikke forsvaret |

### Beståelsesgrænse

**Bestået: 61 af 102 point (60 %) — og mindst 2 på hvert af K1, K6, K7, K8 og K12.** Under 2 på blot ét af de fem er dumpet uanset totalen: de fem er casen. En besvarelse der scorer 75 point og har 1 på K12 har vist at kandidaten kan lave analysen og ikke kan lave arbejdet.

**Stærk: 82 af 102 point (80 %), mindst 3 på K5, K6, K8 og K12, intet kriterium under 2, og mindst ét tal der er målt i eget abonnement frem for gættet.** Sproget er materialets: *kompetent* er at nævne alternativerne og afvise dem på smag; *stærk* er at afvise dem på en akse man kan måle eller prissætte, og sige hvad der ville vende valget.

**Automatisk dump, uanset point:** et scanningsværktøj kørt mod produktionstenanten uden skriftlig aftale, eller en Deny-regel deployet til produktion inden for timeboxen.

## Kalibrering: skriv dette ned FØR du går i gang

Fem forudsigelser. Skriv dem i en fil, gem den, rør den ikke før timeboxen er slut.

1. **Hvor mange af de 312 ressourcer ligger uden for de to regioner der står i kundernes bilag 2?** Ét tal, skrevet før du har læst ét eneste svar i tabellen over skjulte oplysninger.
2. **Hvor stor en del af de 61.400 kr. kan henføres til præcis én kunde med et tag?** Ét procenttal. De fleste skriver over 50.
3. **Hvor mange minutter bruger du på artefakt 8 — de maks. 120 ord til Thomas og Rasmus?** Ét tal med én decimal. De fleste skriver 10 og bruger 45, fordi det er den eneste halve side hvor hvert ord kan koste dig atten måneders arbejdsro.
4. **Hvor mange af dine kravsspørgsmål bliver besvaret med noget der reelt ændrer det du afleverer?** Et tal mellem 0 og 14.
5. **Hvad bliver sværest?** Én sætning, maks. 15 ord.

**Hvad var jeg sikker på og tog fejl om** — udfyldes efter timeboxen, mindst tre linjer, hver af formen "jeg troede X, det var Y, årsagen var Z". Er feltet tomt, er kalibreringen dumpet, ikke perfekt. Fem af fjorten skjulte oplysninger vælter en oplagt løsning; en kandidat der ikke tog fejl om noget, har ikke undersøgt problemet.

## Modelbesvarelsens omrids

**LÆS FØRST EFTER FORSØG.** Ikke et facit. Et omrids af hvad en stærk besvarelse indeholder, og hvilke veje der er forsvarlige.

**Den erkendelse hele casen hviler på**

Regionsreglen findes allerede, er i Enforce, og har aldrig fejlet. Begge hændelser blev muliggjort af at nogen **udvidede** den — tolv minutter og tyve timer før de deployede — og det tog under et minut, uden ejer, uden dato, uden spor nogen læser. Problemet er altså ikke en manglende regel. Det er at omgåelsesvejen er billigere end den rigtige vej, og at ingen ser den blive brugt. En besvarelse der starter med at foreslå en regionsregel, har ikke læst sit eget nulpunkt.

**Tre forsvarlige veje**

- **A. Den lille sande regel.** Kun to ting bliver til noget i vinduet: audit-policy på fire tags (`owner`, `costCenter`, `env`, `dataClassification`) i `DoNotEnforce`, og — den rigtige — synlighed på ændringer af selve lokations-assignmentet: en alarm på Activity Log, en fast udløbsdato på hver tilladt lokation, og et krav om en ADR-linje ved udvidelse. Deny flyttes ikke; den ligger der allerede. Billigst, og den eneste vej der rammer den faktiske årsagskæde. Falder på ét punkt: en alarm ingen læser er en regel ingen har.
- **B. Den compliante vej som modul.** Hovedinvesteringen er `infra/modules/customer-footprint.bicep` plus en `.bicepparam` pr. kunde med lokation og de fire tags bagt ind, så Rasmus' tre deployments i uge 40-42 bliver **hurtigere** med den end uden. Governance leveret som bekvemmelighed; den vej der har størst chance for at blive brugt om seks måneder. Svagest på de to fodaftryk der allerede ligger i jorden, og kræver at han kan vise et måltal på tid frem for at påstå det.
- **C. Bevis først, regel senere.** Hele timeboxen går til det målte nulpunkt og til evidenspakken til Fjordhus. Intet deployes i produktion; policy-arbejdet ligger i eget abonnement med tal. Den ærligste vej i betragtning af at han kun har Reader, og den letteste at score lavt på, fordi den kan degenerere til en rapport ingen handler på. Kun forsvarlig hvis håndhævelsestrappen har datoer, ejere og en første Deny der er ægte lille.

Alle tre er forsvarlige. Den urimelige er kun én: at deploye Deny på regioner og obligatoriske tags til produktion i denne uge. Den brækker Rasmus' tre deployments, den gør Thomas til modstander i to år, og den retter ingen af de to hændelser der allerede er sket.

**Hvad en stærk besvarelse desuden indeholder**

- Det står i første afsnit at 78 % af regningen ikke kan henføres med tags overhovedet, og at Jens' spørgsmål derfor kræver en forbrugsmodel med navngivne proxies og en navngiven fejlmargin — ikke en tagging-oprydning.
- `swedencentral` behandles som et **kontraktbrud mod bilag 2 med et 30-dages varsel**, ikke som et GDPR-problem, og `eastus` behandles som det modsatte. At de to sager er forskellige, står eksplicit, fordi de skal repareres i forskellig rækkefølge og af forskellige mennesker.
- Legal hold på de tre blobs er fanget, og planen for `swedencentral` er derfor kopiér-nu-slet-senere med en dato i første kvartal 2027 og en navngiven ejer — ikke "flyt og ryd op".
- Det åbne ukendte om `eastus`-workspacet står i svaret til Fjordhus som et åbent punkt med en dato, ikke som en beroligelse og ikke som en undskyldning. Og der står hvem der må læse i det.
- Thomas' branch er ikke omgået. Den er brugt: hans PowerShell-script bliver `modify`-policyens remediation-liste, eller han bliver navngivet ejer af tag-trinnet. Det koster ingenting og det ændrer alt.
- Fund undervejs som en der læser systemet ville finde: at logniveauet fra 11. juni er et større enkeltbeløb end alt tagging-arbejdet tilsammen, at revisionssporet per definition aldrig krymper og derfor skal have en retentionsbeslutning frem for en oprydning, og at `param location string = resourceGroup().location` er den enkeltlinje der forbinder begge hændelser med de tre kommende deployments.

**Hvad der adskiller den stærke fra den kompetente**

| Den kompetente | Den stærke |
|---|---|
| Foreslår en regionspolicy | Ser at den findes, læser Activity Log, og styrer **udvidelsesvejen** i stedet for reglen |
| Foreslår fire obligatoriske tags | Kan navngive den rapport der læser hvert af de fire, og fjerner det fjerde hvis han ikke kan |
| Skriver at tags vil vise kundeomkostninger | Skriver at de dækker 22 %, navngiver proxyen for resten og dens fejl |
| Nævner at han kun har Reader | Har målt alt der kan måles med Reader, og beder om det mindste, tidsbegrænsede der låser ham op |
| Nævner Thomas' branch | Bruger den, og gør Thomas til ejer af et trin |
| Skriver "audit før deny" | Har kørt audit i eget abonnement og har compliance-procent og en målt remediation-varighed |
| Laver planen om efter præmisskiftet | Siger også hvad der ikke ændrer sig, og afleverer Owner-rollen tilbage eller tidsbegrænser den skriftligt |
| Skriver et pænt svar til Fjordhus | Skriver også rettelsen af Katrines mail, og hvem der sender den |

## Sådan ser en dårlig besvarelse ud

Skrevet som du selv ville formulere det. Formålet er genkendelse, ikke skam.

1. *"Vi mangler en policy på tilladte regioner, så jeg har skrevet et initiativ."* — Den findes. Den er i Enforce. Den blev udvidet tolv minutter før hændelse 2 af den kollega du er ved at rette. Du har brugt din vigtigste time på at genopfinde det der allerede stod der, og du har ikke læst Activity Log.
2. *"Med fire tags kan vi endelig se hvad hver kunde koster."* — Du kan se 13.600 af 61.400 kr. Resten ligger i en elastic pool, to delte App Service Plans og et delt storage account, og de bliver ikke delt op af et tag. Jens vil opdage det i november, og så er tallet dit.
3. *"`swedencentral` ligger jo i EU, så det er ikke et problem."* — Bilag 2 navngiver to regioner ved navn og kræver tredive dages varsel. Det er ikke et databeskyttelsesproblem, det er et kontraktbrud, og det er værre, fordi der står en underskrift under.
4. *"Vi flytter storage-kontoen og sletter den gamle."* — Tre blobs er under legal hold i en claims-sag. Du kan kopiere. Du kan ikke slette. Og du har lige skrevet et løfte til en kunde om noget du ikke må gøre før tidligst første kvartal 2027.
5. *"Jeg spørger lige Jens om jeg må sætte det op."* — Han siger ja på fyrre sekunder uden at læse det, og han husker det ikke. Du har fået tilladelse til noget, og du har fået nul opbakning til det. To udviklere har fået overlappende ja'er i år.
6. *"Jeg kører lige AzGovViz mod tenanten så vi har et rigtigt overblik."* — Det er den ene handling i hele planen der kan give dig et alvorligt problem i stedet for at fremme dig. Uden skriftlig aftale er casen dumpet her, uanset hvor godt resten er.
7. *"Jeg nævner ikke Thomas' branch — det bliver bare akavet."* — Han skrev det offentligt den 4. juni og igen den 2. september. Han opdager det i det sekund din tabel over tag-dækning rammer kanalen, og han opdager det som at du gik uden om ham. At bruge hans script koster dig ingenting og køber dig atten måneder.
8. *"Jeg starter med audit, og så tager vi deny når vi er klar."* — Uden et tal der udløser trinnet, en dato og en navngiven ejer er "når vi er klar" aldrig. Det er præcis sådan de tre exemptions fra 2022 og 2024 stadig står.
9. *"Præmissen ændrede sig, men det havde jeg jo taget højde for."* — Det er forsvar. Jens gav dig Owner over hovedet på de to der har været her længst, og din plan er nu et eksternt løfte med en dato du ikke satte. Der er ikke noget ved det du havde taget højde for.

## Hvor i materialet svaret står

Ubarmhjertig version. To kriterier er ikke dækket af noget modul, og det er et fund i materialet, ikke i casen.

| Kriterium | Modul | Præcis sektionsoverskrift | Hvad du henter der |
|---|---|---|---|
| **K1** Kravsspørgsmål før første policy-navn | 01 | `### Øvelse 3: Trade-off-kata på tid` | Kravet om mindst otte kravsspørgsmål **før** første diagram, den hårde timebox, og selvkontrollen til sidst: besvarede du dit eget design uden at have svar på halvdelen, er det fundet. Suppl.: 01 `## Sådan ved du at du kan det`, første punkt, om otte kravsspørgsmål før du nævner en teknologi |
| **K2** Spørgsmålene rammer de dyre akser | 12 | `## De første 30 dage: beskriv, mål, foreslå intet` | Reglen om nul strukturelle forslag og om at gå rundt med tal i lommen frem for en mening. Suppl.: 07 `## Faldgruber`, punktet om governance-gæld — en policy med to hundrede exemptions er en løgn med revisionsspor, hvilket er den akse der vælter denne case; og 10 `## Kvalitetsattribut-scenarier: din del af kravarbejdet` for kravet om at responsmålet altid er et tal |
| **K3** Nulpunktet med spænd | 07 | `### G1 — Tag- og region-guardrail som policy-as-code (måned 1-2, ~1 uge dedikeret)` | Hele mekanikken: deploy femten bevidst non-compliante ressourcer, notér compliance-procenten, kør en remediation task, **mål igen**, og `measurements.md` med før og efter samt målt varighed. Suppl.: 03 `## Sådan ved du at du kan det`, punktet om at svare med et tal, en kilde og en usikkerhedsmargin inden for 30 minutter; og 12 `## De første 30 dage: beskriv, mål, foreslå intet` |
| **K4** Omkostningsfordelingen | 12 | `## Tre spikes med fysisk output` (spike 4, Enhedsøkonomi pr. tenant) | Direkte hit: modellen der fordeler Azure-forbrug pr. tenant på storage, egress, compute og backup-retention; sætningen "findes der ikke tags pr. tenant, *er* dét fundet"; og proxyerne — antal dokumenter, storage-forbrug, antal integrationskørsler. Suppl.: 06 `## Cost er et arkitekturproblem, ikke et driftsproblem` for hvorfor Log Analytics-ingestion er det største enkeltbeløb i stigningen; og 01 `## Kompetencemodellen: ti akser`, rækken "Kostmodellering" — model med tre poster, kender usikkerheden, ved hvad der flytter tallet mest |
| **K5** Guardrail frem for gatekeeper, målt på tid | 07 | `## Guardrail eller gatekeeper` | Definitionen, og den målbare test: forskellen mellem tid-til-compliant-miljø og tid-til-non-compliant-miljø, plus de to sætninger du skal kunne for hver idé — hvordan gør det den rigtige vej hurtigere, og hvad koster det den forkerte. Suppl.: 07 `### Hvis der er luft (vælg én, måned 6-8)`, G4, for kravet om at måle den compliante vej som hurtigere og skriftligt redegøre for dit forsøg på at omgå din egen kontrol |
| **K6** Progressionen audit → modify → deny | 07 | `## Progressiv håndhævelse: manøvren der giver mandat` | Rækkefølgen ordret, `enforcementMode: DoNotEnforce`, og mønstersætningen: "jeg kørte det i audit i tre uger; der er 43 afvigelser, 38 af dem i én resource group, her er modify-policyen der retter dem — skal vi håndhæve for nye ressourcer?". Suppl.: 07 `### G1` for at kun region-policyen til sidst skiftes til Enforce; og 07 `## Faldgruber`, punktet om at foreslå Deny først |
| **K7** Fravalget | 07 | `## Faldgruber` | Punktet "For mange obligatoriske tags. Fire er meget, otte er nul. Kan du ikke navngive rapporten der **læser** `owner`, skal tagget væk." Suppl.: 07 `### G5 — ADR-serie om lejerisolation i dokumentlageret (måned 3-4, 1 uge, parallelt)` for kravet om navngivne afviste alternativer i ADR-form; og 05 `## De tre nej'er du skal skrive ned` for formen: mønster, hvorfor nej her, og betingelsen der vender svaret |
| **K8** Faldsbetingelsen og udløbsdatoen | 07 | `## Sådan ved du at du kan det` | Punktet: hver regel du har indført, også dine egne, har navngiven ejer og udløbsdato — og du kan navngive én, du **fjernede** igen, fordi den ikke betalte sig. Suppl.: 07 `## Faldgruber`, governance-gæld; 09 `## Sådan ved du at du kan det`, rækken "ADR-tællingen" — mangler afsnittet om hvad der ville ændre beslutningen, er det en begrundelse og ikke en beslutning; og 07 `### G9 — Fitness functions: principper omsat til tests` for testen på om et princip er operativt |
| **K9** Adgang, mandat og den hårde advarsel | 07 | `## Progressiv håndhævelse: manøvren der giver mandat` | Den hårde advarsel ordret: kør aldrig scanningsværktøjer mod LeanLinkings produktionstenant uden skriftlig aftale; bed om Reader på ét abonnement og vis outputtet først; får du nej, kører du mod dit eget dev-tenant. Suppl.: 03 `## Den ene ting du beder om på arbejdet` for Reader-formuleringen der ikke kan afvises og for at Cost Management Reader skal bedes om separat; 07 `## Ressourcer`, rækken om AzGovViz — "Intet, men kør den aldrig mod produktionstenanten"; og 12 `## Uge 1: fem ting du kan gøre uden at spørge om lov` for den lille bøn der aldrig afvises |
| **K10** Formuleringen der ikke skaber en modstander | — | **IKKE DÆKKET** | Materialet har delene, men ikke sagen. Det har: sig aldrig ordet governance internt, sig i stedet "det her gør næste sikkerhedsspørgeskema til en time i stedet for tre dage" (07 `## Artefakter du kan producere`); ordene teknisk gæld, kvalitet og arkitektur som forbudte over for stifter og kolleger (12 `## Faldgruber`, 11 `## Oversæt til kroner og risiko`); steelman og tab pænt skriftligt (11 `## Uenighed skrives, den tales ikke`); og forudsætningen om at governance-arbejde er **ejerløst** (07 `## Artefakter du kan producere`: "ingen ejer tagging-strategien"). Præcis den forudsætning er falsk her. Der mangler: hvordan man overtager noget en kollega med længere anciennitet **offentligt har lovet og ikke leveret**, uden at det læses som en afsløring; hvordan man indfører en begrænsning der ændrer en andens daglige arbejdsgang uden at have bedt om det; og hvad man gør når ens sponsor giver en mandat over hovedet på netop de to. Det er casens tungeste kriterium og materialets største hul på dette emne |
| **K11** Det eksterne svar: at rette en afgivet erklæring | — | **IKKE DÆKKET** | Materialet dækker evidenskæden godt: 08 `## Fem krav du sporer hele vejen ned` har rækken "GDPR kap. V overførsler → Azure Policy der begrænser tilladte regioner til EU → Policy-fil i git + rapport", og 12 `## Tre spikes med fysisk output` (spike 3, Spørgeskema-maskinen) har kategorierne *dokumenteret*, *sandt men udokumenteret*, *ikke sandt* plus gap-registret. Der mangler **korrektionen**: hvordan man tilbagekalder eller præciserer en erklæring der allerede er sendt til en kunde med dato på, hvem der skriver under, hvordan varslingsbestemmelsen om underdatabehandlere håndteres når varslet ikke er givet, og hvordan man skriver et åbent ukendt ind i et kundedokument uden at det bliver til enten en beroligelse eller en indrømmelse. 11 `## Fire spikes med fysisk output` (spike C) kræver mindst ét "det gør vi ikke i dag, og her er hvorfor", men ikke et "det ved vi ikke endnu, og her er datoen" |
| **K12** Iteration ved præmisskift | 01 | `## Sådan ved du at du kan det` | Andet punkt: "Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse." Suppl.: 01 `### Øvelse 3: Trade-off-kata på tid`, afsnittet om at en ekstern person ændrer en præmis efter fire timer; 11 `## Uenighed skrives, den tales ikke` for at skrive opdateringen selv når du tog fejl; og 12 `## Uge 1: fem ting du kan gøre uden at spørge om lov`, vanen med seks linjers opsummering samme dag efter enhver samtale med stifteren der ligner en aftale — den vane er præcis modgiften mod punkt 1 og 2 i præmisskiftet |

## Ekstern kalibrering

Din egen score er værdiløs alene, og en kollega i et ni-mandsfirma tæller halvt — særligt her, hvor Thomas har en holdning til ordet policy, og hvor Rasmus' arbejdsgang er den der ændrer sig. Mindst to af disse skal have givet **skriftlig** kritik, før casen tælles som gennemført. Spørg hver om én ting, ikke om en helhedsvurdering.

| Hvem | Hvor du finder dem | Det konkrete spørgsmål |
|---|---|---|
| En platform- eller cloud-ansvarlig fra et dansk hus på 100-500 ansatte | ANUG eller GOTO-meetup i Aarhus; bed om 30 minutter efter oplægget | "Her er min håndhævelsestrappe med tre trin, tal og datoer. Hvilket trin er det I aldrig kom videre fra, og hvad var grunden?" |
| En udvikler der har været på **modtagersiden** af et centralt platformsteams politik | Samme netværk; spørg efter en der har arbejdet i bank, energi eller offentlig sektor | "Læs mine 120 ord til to kolleger med længere anciennitet end mig. Hvor i dem ville du blive irriteret, og på hvilket ord?" Dette er det spørgsmål ingen af de andre kan svare på |
| En ISO 27001-lead auditor eller en certificeringsorganisations tekniske reviewer | Gennem en kunde der er certificeret, eller de danske certificeringsorganer; bed om 30 minutter mod at de må bruge det som salgsmøde | "Her er mit svar til en kundes kvalitetschef før deres surveillance audit. Hvilken sætning ville få jer til at skrive en nonconformity på deres leverandørstyring alligevel?" |
| En DPO eller privacy-rådgiver med databehandlererfaring | Gennem en kundes complianceafdeling, eller et dansk privacy-netværk | "Vi har en behandlingslokation der ikke står i bilag 2, og et varsel der ikke er givet. Hvad ville I helst have haft leverandøren til at gøre, og i hvilken rækkefølge?" |
| Betalt ekstern sparring, 1 time | Den faste ordning fra modul 12, post 4 i forhandlingen | "Angrib mit fravalg, ikke min analyse. Hvilket af de fire ting jeg valgte **ikke** at styre, kommer til at koste mest inden for tolv måneder?" |
| Code review-byttepartneren | Den udvikler i et andet firma du har fast kadence med fra måned 3 | "Læs min Bicep og mine faldsbetingelser. Kan du finde vejen uden om min egen guardrail på under to minutter? Sig hvordan." |

Notér for hver: hvad de sagde, hvad du ændrede, og hvad du valgte at lade stå — plus hvorfor. Den tredje kolonne er den, en kommende arbejdsgiver spørger ind til.
