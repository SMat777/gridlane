# C02 — Månedsafslutningen der tager 40 sekunder

| | |
|---|---|
| **Type** | Incident-forensik med måleapparat |
| **Primært modul** | 02 — Det tekniske fundament |
| **Sekundære moduler** | 06 — Observability · 10 — Produkt, prioritering og leverance |
| **Timebox** | 6 timer, i én blok eller to blokke på samme uge. Præmisskiftet åbnes efter 3 t 36 min |
| **Sværhedsgrad** | 4 af 5. Giver mening i måned 5-7: efter spike 2 (async-fejlmønstre), spike 3 (allokering og GC), spike 4 (SQL uden ORM) og spike 5 (EF Core-diffen). Kørt i måned 2 producerer den gætværk med tabeller omkring |
| **Afleveringsformat** | Otte artefakter, i alt 7-9 sider: måleplan (1 s.), bevissikringsnote (10 linjer), diagnoserapport (3-4 s.) med nedbrydningstabel, prisskiltstabel (1 s.), énsides notat til en ikke-teknisk læser (maks 400 ord), ADR (maks 1,5 s.), kalibreringspost (0,5 s.) |

## Situationen

Det er torsdag den 10. september 2026, kl. 09.20. Line Sørensen fra kundeteamet har lagt en ticket i din kolonne med teksten *"scorecard-siden er stadig langsom ved månedsskifte — Ravnholm er ved at være trætte"* og en skærmoptagelse hvor en spinner kører i 38 sekunder før siden tegner.

Det handler om den 1. september. Ravnholm Industri A/S (4.118 leverandører) og Nordbeck Retail A/S (2.640 leverandører) er husets to største kunder og tilsammen 605.000 kr. om året af en bruttofortjeneste på 4,2 mio. Deres indkøbere åbner scorecard-siden om morgenen den første hverdag i måneden, fordi det er der de nye OTIF-, PPM- og claims-tal for forrige periode ligger. Application Insights viser p95 på 38 sekunder for Ravnholm den dag mod 0,4 sekunder resten af august. Én request nåede 100 sekunder og fik 504 fra gateway'en. Line mener det er sket "hver måned siden foråret". Hun har ikke datoerne.

Der er allerede sket to ting, som du ikke har været med til.

Den 4. august holdt Ravnholm deres Q2 supplier business review. Tallet på lærredet var OTIF 94,2 procent for en leverandør ved navn Halskov Metal ApS, og på det grundlag blev leverandøren taget ud af eskalering. Det korrekte tal, når de forsinkede ERP-posteringer fra kundens SAP var talt med, var 91,6. Ravnholms compliancechef har bedt skriftligt om en forklaring. To dage efter lagde Thomas Riis, husets mest erfarne udvikler og den der skrev scorecard-modulet i 2019, en cache ind foran beregningen med 24 timers TTL. Siden blev hurtig. Thomas er på ferie i Vietnam til den 21. september og svarer ikke.

Den 28. august skrev Jesper Halkjær, stifteren, en mail til Katrine Vestergaard, indkøbsdirektør hos Ravnholm. Der står to sætninger du skal leve med: *"Fra 1. oktober er scorecard-siden under 3 sekunder også ved månedsskifte"* og *"caching-problemet er løst"*. Ravnholms kontrakt genforhandles den 15. oktober. Jesper har givet dig maks tre udviklerdage og siger at han ikke vil have nye faste månedlige omkostninger over 500 kroner.

To ting bliver nævnt af kolleger, uopfordret. Bjarne, der passer databasen ved siden af sit rigtige arbejde, siger at det nok er fragmentering — den natlige indeksvedligeholdelse blev slået fra den 14. marts med commit-beskeden *"midlertidigt, jobbet kørte 4 timer"*, og ingen har slået den til igen. Og Azure-portalen viser at App Service-instansen lå på 97 procent CPU mellem 07.40 og 08.15 den 1. september; Line har allerede spurgt om vi ikke bare kan købe en større.

Databasen er Azure SQL, General Purpose, 4 vCores. `ScorecardFact` har 96 mio. rækker. Der er 22 tenants. Der findes ikke en kopi af produktionsdata du kan arbejde på.

Den 1. oktober er en torsdag. Der er 21 dage til.

## Det du skal aflevere

| # | Artefakt | Format | Krav |
|---|---|---|---|
| 1 | **Måleplan** | 1 side, tidsstemplet, skrevet **før** din første måling | Hver hypotese med: hvilket værktøj, hvad værktøjet viser hvis hypotesen er sand, hvad det viser hvis den er falsk, og **hvad værktøjet ikke kan svare på**. Plus dit forudsagte tal per hypotese |
| 2 | **Bevissikringsnote** | 10 linjer | Hvad du hentede ud af hvilken kilde, hvornår kilden udløber, og hvor kopien ligger |
| 3 | **Diagnoserapport** | 3-4 sider | Faktatidslinje i minutter for den 1. september; plananalyse med den dyreste operator navngivet og hvorfor; mindst to hypoteser **falsificeret** med det bevis der gjorde det |
| 4 | **Nedbrydningstabel** | I rapporten | De 38-41 sekunder brudt ned i navngivne bidrag i millisekunder, **hver med et usikkerhedsspænd og antal kørsler bag**, plus en restpost du tør kalde rest |
| 5 | **Prisskiltstabel** | 1 side | 3-4 muligheder. Per mulighed: kr./md. løbende, udviklerdage som interval (ikke ét tal), forventet effekt på p95 i ms med spænd, og hvad der bliver **værre** |
| 6 | **Notat til Jesper og Line** | Maks 400 ord, ingen tekniske ord | Hvad der skete, hvad Katrine kan få at vide om den 4. august, hvad vi lover til den 1. oktober og med hvilken sandsynlighed, og hvad vi udtrykkeligt **ikke** lover |
| 7 | **ADR** | Maks 1,5 side, MADR | Alternativer afvist på en akse du har målt eller prissat. Consequences skal indeholde noget der er dårligt ved dit eget valg. Faldsbetingelse med tal og med hvordan den opdages |
| 8 | **Kalibreringspost** | 0,5 side | Forudsigelser mod faktisk, og feltet "hvad var jeg sikker på og tog fejl om" |

Foreslået fordeling: 40 min. spørgsmål og måleplan, 30 min. bevissikring, 2 t måling, 1 t nedbrydning og prisskilt, 1 t skrift, 50 min. buffer. Bruger du over 2,5 timer på måling, har du ikke en måleplan, du har en udforskning.

To ting tæller ikke som aflevering. Et skærmbillede af en execution plan uden din egen skrevne kommentar er ikke plananalyse — værktøjet har allerede sat den gule advarselstrekant, og det er ikke dig der har læst planen. Og en anbefaling uden løbende omkostning er ikke en anbefaling; det er en teknisk præference. Jesper har givet dig et loft på 500 kr./md., og et forslag der ikke oplyser sit forhold til det loft, kan han ikke svare på.

Artefakt 1 og artefakt 2 skal have et tidsstempel der ligger **før** dit første måletal. Kan du ikke dokumentere den rækkefølge, scorer K1 og K3 nul, uanset hvor gode dokumenterne er. Det er casens eneste formelle regel, og den er der fordi rækkefølgen er hele pointen.

Tre formkrav der er billige at opfylde og dyre at glemme:

- **Faktatidslinjen i artefakt 3 skrives i minutter, ikke i afsnit**, og den skelner mellem tre tidspunkter: hvornår problemet opstod, hvornår nogen opdagede det, og hvornår nogen gjorde noget. De tre tal er ikke det samme, og i denne case ligger der uger mellem det første og det sidste.
- **Ingen navne i årsagsbeskrivelsen.** Thomas' cache er "cachen indført 6. august", ikke "Thomas' fejl". Det er ikke pænhed; det er den ene ting der afgør om nogen tør skrive den næste postmortem.
- **Prisskiltstabellen skal have en nulmulighed:** hvad koster det at gøre ingenting frem til den 1. november. Uden den række kan Jesper ikke se hvad han køber, kun hvad det koster.

## Skjulte oplysninger

Reglen: du må kun læse svaret på spørgsmål du **selv har skrevet ned i måleplanen før du begyndte at designe en løsning**. Skriv spørgsmålene først, i én blok, og stryg dem ikke bagefter. Formuleringen behøver ikke ramme ordret — spørger du "hvad kører der om natten den 1.", har du fortjent svar nr. 1. Spørger du "hvorfor er databasen langsom", har du ikke spurgt om noget.

Casens hårdeste enkelttal er hvor mange af de fjorten du henter. Under fem, og du arbejder i blinde uden at vide det. Over ni, og du har brugt tid på oplysninger du ikke bruger til noget — hvilket også er en fejl, bare en billigere en.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Kører der planlagte jobs natten til den 1.? | Ja. Periodelukningsjobbet indsætter mellem 780.000 og 1,1 mio. rækker i `ScorecardFact` mellem 02.00 og 03.05. Kl. 03.10 kører `sp_updatestats` på hele databasen. Begge dele kun natten til den 1. |
| 2 | Hvordan fordeler de langsomme requests sig over døgnet den 1. september? | Første langsomme request 07.41. Alle langsomme requests ligger mellem 07.41 og 16.20. Ingen requests overhovedet før 07.41. Ingen opvarmningskurve — den første er lige så langsom som den sidste |
| 3 | Er den langsom for alle tenants, eller kun de to store? | 14 af 22 tenants har p95 under 900 ms den 1. september. Ravnholm, Nordbeck og Hørkær Food (1.140 leverandører) er langsomme. Grænsen ligger et sted omkring 1.000 leverandører. Ingen har målt hvor præcist |
| 4 | Hvad viser CPU og IO på selve Azure SQL-instansen den 1.? | Gennemsnitlig CPU 34 procent, maksimum 61 procent. Data IO maksimum 22 procent. Log IO maksimum 9 procent. Ingen ressourcemætning på databasen på noget tidspunkt den dag |
| 5 | Hvad koster det at gå fra 4 til 8 vCores, og hvad ville det give? | Cirka 2.900 kr./md. ekstra, altså 34.800 kr./år. Ingen har målt hvad det ville give. Det ligger 5,8 gange over Jespers loft på 500 kr./md. |
| 6 | Hvad er indeksstrukturen på `ScorecardFact`? | Clustered index på `Id` (identity). Ét nonclustered på `(TenantId, PeriodEnd)`, oprettet i 2021, uden INCLUDE-kolonner. Forespørgslen selekterer 11 kolonner. Natlig indeksvedligeholdelse har været slået fra siden 14. marts |
| 7 | Er andre endpoints langsomme den 1.? | Ja. `POST /api/scorecards/{id}/export` går fra p99 2,1 s til p99 71 s, og det er det eneste endpoint der ramte 504. Der blev kaldt 23 eksporter den dag. I PDF-rendereren står `.GetAwaiter().GetResult()` på et kald til blob-storage |
| 8 | Hvad gjorde cachen præcist forkert den 4. august? | Nøglen er `(tenantId, scorecardId)`. TTL er 24 timer absolut. Et opvarmningsjob fyldte den kl. 06.12. Ravnholms forsinkede juli-posteringer fra SAP landede kl. 07.50. Bestyrelsen så tallet fra kl. 06.12. Cachen har ingen invalidering ved dataændring |
| 9 | Står der noget om svartid i Ravnholms kontrakt? | Nej. Der er ingen SLA på svartid i kontrakten. Jespers mail af 28. august er ikke et kontrakttillæg, men den er skriftlig, og Katrine har videresendt den til sin compliancechef |
| 10 | Hvad skete der den 1. juli og den 1. august? | 1. juli: samme mønster, p99 38 s. 1. august: p99 2,4 sekunder, ingen klager. **Ingen ved hvorfor august var anderledes.** Det eneste nogen kan pege på er at 1. august var en lørdag, og at den første hverdag derfor var mandag den 3. Hvad de 48 timer gjorde, har ingen undersøgt |
| 11 | Kan jeg få en kopi af produktionsdatabasen? | Nej. Databehandleraftalen forbyder kopiering af leverandørkontaktdata til udviklingsmiljø. Der findes en maskeret restore fra 1. juli — 11 uger gammel, uden juli- og august-periodelukningerne, altså med andre statistikker end produktion. Restore tager 40-70 min. og koster ca. 90 kr. i compute |
| 12 | Er Query Store slået til, og hvor længe gemmer den? | Ja, det er default i Azure SQL. `QUERY_CAPTURE_MODE = AUTO`, retention 30 dage. Planerne fra 1. september findes stadig. De forsvinder omkring 1. oktober |
| 13 | Hvordan er Application Insights sat op? | Fixed-rate sampling på 20 procent. Retention 90 dage. Der er ingen custom span-attributter — ingen `tenant_id`, intet leverandørantal, intet periode-id. Auto-instrumenteringen fortæller dig at requesten tog 38 sekunder og intet andet |
| 14 | Hvor mange brugere og hvor meget samtidighed er der den 1.? | Ravnholm: 31 navngivne brugere, ca. 180 sideindlæsninger mellem 07.30 og 10.00. Nordbeck: 19 brugere, ca. 90 indlæsninger. Højeste målte samtidighed på scorecard-endpointet: 14 requests |

Fire af svarene vælter en oplagt løsning: nr. 4 og nr. 5 dræber "skalér databasen op", nr. 11 dræber "jeg reproducerer det bare lokalt på rigtige data", og nr. 3 dræber "hele systemet er overbelastet den 1.". Nr. 10 er det ærlige "det ved vi ikke", og det er ikke en undskyldning for at ignorere det: enhver forklaring du afleverer skal enten forklare hvorfor august var hurtig, eller sige eksplicit at den ikke gør, og hvad det betyder for din tiltro til din egen diagnose.

## Præmisskiftet

**Åbnes først når 3 timer og 36 minutter af timeboxen er gået. Ikke før.**

Line videresender en mail fra Ravnholms compliancechef, Anders Thorup. På baggrund af episoden den 4. august påberåber Ravnholm sig en klausul i leverandøraftalen om revisionsspor: **ethvert offentliggjort scorecard-tal skal kunne genskabes 24 måneder tilbage, sådan som det så ud på den dag det blev vist.** Bliver de spurgt "hvilket OTIF-tal viste systemet os den 4. august 2026", skal svaret være 94,2 — ikke det tal en genberegning giver i dag — og der skal kunne vises hvilke posteringer der lå bag. Anders vil have et skriftligt svar inden kontraktforhandlingen den 15. oktober.

Det gør tre ting ved dit arbejde. Cachen er ikke længere kun en fejl — den er det eneste sted i systemet der ved hvilket tal kunden faktisk så. Enhver løsning der gør beregningen hurtigere ved at regne oftere, gør problemet værre, fordi historiske tal så kan skifte lydløst. Og et arbejde du har budgetteret til tre udviklerdage har fået en dimension der ikke kan være i tre udviklerdage.

Jesper er i øvrigt ikke blevet mindre optimistisk. Han har svaret Anders Thorup at "det er noget vi allerede arbejder på". Det er ikke løgn, og det er heller ikke sandt.

**Hvad skiftet tester:** om du behandler dine egne målinger som et svar eller som et input. En stærk besvarelse siger på under ti minutter hvilke af de foregående 3,5 timers resultater der stadig gælder, hvilke der er blevet irrelevante, og hvad der nu skal måles i stedet — og deler leverancen i "det der skal virke 1. oktober" og "det der skal besvares 15. oktober", med hver sin pris. En svag besvarelse forklarer hvorfor den oprindelige anbefaling faktisk også dækker det nye krav.

Det er værd at bemærke hvad skiftet **ikke** er. Det er ikke en straf for at have valgt forkert i de første 3,5 timer, og det er ikke en invitation til at kassere arbejdet. De fleste af målingerne er stadig gyldige; det er kravsbilledet der har flyttet sig, ikke virkeligheden. Den dyreste fejl her er at behandle et skiftet krav som en fejl i sin egen analyse, og den næstdyreste er at behandle det som noget der ikke rørte analysen.

## Rubrik

Hvert kriterium scores 0-3. Vægten ganges på. Maksimum er 99 point.

| # | Kriterium | Vægt | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|---|
| **K1** | **Spørgsmål før design** | 3 | Ingen spørgsmålsliste findes, eller den er skrevet efter at løsningen var valgt | 1-4 spørgsmål, overvejende om kode ("hvor ligger forespørgslen") | 5-8 spørgsmål nedskrevet før design, mindst tre af dem falsificerende (svaret kan vælte en hypotese) | 9+ spørgsmål før design, mindst fem falsificerende, og mindst ét om hvem der bærer risikoen frem for om teknik. Spørgsmålene er nummereret og krydsrefereret til hypoteserne i måleplanen |
| **K2** | **Det ubesvarede gjort til et vilkår** | 2 | 1. august-anomalien nævnes ikke | Nævnes, men bortforklares uden bevis ("det var nok tilfældigt") | Nævnes som åbent, og diagnosen mærkes eksplicit som uverificeret på det punkt | Nævnes, formuleres som to konkurrerende hypoteser, hver med det billigste eksperiment der ville afgøre den, og med angivelse af hvad det koster i tid at lade den stå åben til 1. oktober |
| **K3** | **Måleplanen: værktøj og forudsigelse før første måling** | 3 | Ingen måleplan. Værktøjer prøves i rækkefølge indtil noget viser noget | Værktøjer navngives, men uden hvad de ville vise hvis hypotesen er falsk | Mindst fire hypoteser, hver med værktøj, forventet signatur ved sand og ved falsk. Mindst tre forudsagte tal skrevet ned før måling | Som 2, plus mindst ét værktøj **fravalgt** med begrundelse (fx: en gcdump svarer ikke på hvorfor kun tre tenants er ramt), og forudsigelserne har enheder og spænd, ikke retninger |
| **K4** | **Bevissikring under udløbende retention** | 2 | Intet sikret. Det opdages i rapporten at beviset ikke længere findes | Skærmbilleder taget, uden tidsstempel eller kilde | Query Store-planerne og de relevante App Insights-udtræk gemt med kilde og tidsstempel, og retentionsgrænsen noteret | Som 2, plus: sampling-graden på 20 procent er indregnet i hvad tallene betyder, og der står hvilket bevis der **ikke** kan skaffes mere og hvad det gør ved konklusionens sikkerhed |
| **K5** | **Execution plan læst uden værktøjshjælp** | 3 | Ingen plan hentet, eller planen vises uden kommentar | Planen vises, og den operator værktøjet har markeret som dyrest gengives | Dyreste operator udpeget selv, med logical reads og med estimeret mod faktisk rækkeantal for netop den operator | Som 2, plus forklaring af **hvorfor** estimatet er forkert, sammenligning med planen for en lille tenant, og en forudsigelse af hvordan planen ændrer sig efter dit indgreb — skrevet før indgrebet |
| **K6** | **Differentialdiagnose og falsifikation** | 3 | Én årsag udpeges uden at alternativer nævnes | Alternativer nævnes og afvises på smag eller erfaring | Mindst fire af fem kandidater behandlet (parameter sniffing, manglende eller utilstrækkeligt indeks, N+1 fra EF Core, ThreadPool starvation, GC-pres), og mindst to **falsificeret** med et konkret måletal | Som 2, plus: for hver falsificeret kandidat står det bevis der ville have overbevist om det modsatte, og der skelnes eksplicit mellem den udløsende faktor og årsagen — inklusive hvad der forklarer den ene 504 mod de 180 langsomme sideindlæsninger |
| **K7** | **Nedbrydning i tal med usikkerhed** | 3 | Ingen nedbrydning. "Det er databasen" | Ét tal per komponent, én kørsel, intet spænd | Mindst fire navngivne bidrag i ms, hver med spænd, mindst to kørsler bag hvert tal, og en navngiven restpost. Summen afstemmes mod de målte 38-41 s | Som 2, plus: to kørsler af den samme måling ligger inden for 5 procent af hinanden, afvigelsen er oplyst, og der står hvilken måling der **ikke** var reproducerbar og hvorfor. Bidrag under 5 procent af totalen er markeret som ikke værd at forfølge |
| **K8** | **Prisskilt og den ikke-tekniske side** | 3 | Ingen priser. Anbefaling uden omkostning | Udviklerdage angivet som ét tal, ingen løbende omkostning | 3-4 muligheder med kr./md., udviklerdage som interval, og forventet ms-effekt med spænd. Notatet til Jesper og Line indeholder ingen tekniske ord og et konkret tal | Som 2, plus: sandsynlighed sat på om løsningen holder den 1. oktober (fx "70-80 procent"), en eksplicit pris på at tage fejl, og en sætning om hvad Katrine kan få at vide om den 4. august uden at love mere end vi kan holde. Under 400 ord |
| **K9** | **Fravalg på en målbar akse** | 3 | Alternativer nævnes ikke | Alternativer nævnes og afvises med "det er ikke den rigtige løsning" | Mindst tre alternativer afvist, hver på én navngiven akse med et tal (kr./md., ms, udviklerdage, skrivetid på periodelukningsjobbet, lagerplads) | Som 2, plus: mindst ét alternativ afvises på en akse hvor det faktisk **vinder** over det valgte, og prisen for det tab står skrevet. Skalér-op-muligheden er prissat og afvist på effekt, ikke kun på pris |
| **K10** | **Faldsbetingelse med tærskel og detektion** | 2 | Ingen faldsbetingelse | "Vi tager det op igen hvis det bliver et problem" | Faldsbetingelse med et tal og en dato (fx "hvis p95 den 1. november overstiger 4 s, eller hvis Ravnholm passerer 6.000 leverandører") | Som 2, plus: hvordan betingelsen opdages uden at nogen husker at kigge — hvilken metric, hvilken tærskel, hvem der vågner, og hvad der sker hvis ingen reagerer i to timer |
| **K11** | **Cachen: staleness, risikobærer og kollegaen** | 3 | Cachen behandles ikke, eller fjernes uden erstatning | "Cachen skal væk, den er forkert" | Staleness-vinduet angivet i sekunder for den nuværende og for den foreslåede løsning, og det står hvem der bærer risikoen for et forkert tal | Som 2, plus: staleness knyttet til hvornår perioden er lukket nok til at offentliggøres (watermark) frem for til en fast TTL; og Thomas' beslutning behandles skriftligt som en beslutning truffet med den information han havde, ikke som en fejl — uden at det bløder konklusionen op |
| **K12** | **Iteration ved præmisskiftet** | 3 | Præmisskiftet ignoreres, eller besvarelsen afsluttes uden det | Skiftet noteres, og den oprindelige anbefaling forsvares som "dækker også det" | Anbefalingen ændres. Det står hvad der stadig gælder af de foregående 3,5 timer og hvad der er faldet bort | Som 2, plus: leverancen deles i to spor med hver sin dato (1. oktober mod 15. oktober) og hver sin pris; det står hvad der nu skal måles som ikke blev målt; og mindst én tidligere konklusion trækkes eksplicit tilbage med begrundelse |

### Bestået og stærk

**Bestået (kompetent):** mindst 64 af 99 point, **og** mindst 2 på hvert af K1, K3, K6, K7 og K9, **og** ingen nuller.

**Fældet port uanset totalsum:** 0 på K1 eller 0 på K3. Casen handler om at måle frem for at gætte; en høj score bygget oven på et gæt måler noget andet end det den skal.

**Stærk:** mindst 80 af 99 point, **og** 3 på K6, K7, K9 og K12, **og** højst ét kriterium på 1. Dertil, i overensstemmelse med kompetencemodellen i modul 01: din egen score tæller ikke alene. Diagnoserapporten og prisskiltstabellen skal have været læst af mindst én praktiserende .NET- eller dataudvikler uden for LeanLinking, og du skal kunne pege på hvad du ændrede efter den læsning. Ændrede du intet, var reviewet høfligt.

**Sådan scorer du dig selv uden at snyde.** Score først på artefakterne alene, uden at læse dine egne noter og uden at huske hvad du mente undervejs. Findes påstanden ikke skrevet i et dokument, findes den ikke. Derefter, og først derefter, må du læse `## Modelbesvarelsens omrids`. Læser du omridset før du scorer, kan du ikke længere adskille "det tænkte jeg også" fra "det skrev jeg". Den skelnen er hele forskellen mellem en kalibreringslog og en dagbog.

Casen kan tages om, men ikke på det samme scenarie: du har set de skjulte oplysninger, og de fjorten svar kan ikke ses igen. Vil du måle fremgang på den samme kompetence, er det en ny incident-forensik-case du skal bruge, ikke en gentagelse af denne.

## Kalibrering: skriv dette ned FØR du går i gang

Fem felter. Tidsstempl dem. De kan alle efterprøves om seks timer.

1. **Hvor stor en andel af de 38 sekunder ligger i ét enkelt databasekald?** Skriv et procenttal med spænd (fx "70-85 procent").
2. **Hvor mange databasekald laver ét sideindlæsning for Ravnholm?** Skriv et tal. Ram inden for en faktor 3.
3. **Rangordn alle fem kandidater før du måler:** parameter sniffing, manglende eller utilstrækkeligt indeks, N+1 fra EF Core, ThreadPool starvation, GC-pres. Skriv rækkefølgen og din tiltro til nummer ét i procent.
4. **Hvor lang tid går der før du har dit første reproducerbare tal** — altså et tal du har målt to gange inden for 5 procent? Skriv minutter.
5. **Hvad bliver sværest: at måle det, at forstå det, eller at prissætte det?** Ét ord, og én sætning om hvorfor.

Skriv dem i din prædiktionslog, ikke i et løst dokument. Pointen er ikke posten fra i dag; det er at fejlmarginen skal kunne aflæses som en kurve over seks måneder, og det kræver at posterne står samme sted i samme format. Modul 02's kompetenceport måler præcis det, og den måler det på loggen, ikke på fornemmelsen.

Bemærk hvad felt 3 gør: det tvinger dig til at rangordne fem kandidater du ikke har målt endnu, og det føles ubehageligt at skrive ned. Ubehaget er signalet om at øvelsen virker. En rangordning du kan stå ved bagefter uanset resultatet, var for vag til at være en forudsigelse.

Og til sidst, efter timeboxen, feltet der gør resten falsificerbart:

> **Hvad var jeg sikker på og tog fejl om?** Skriv præcis hvad du troede, præcis hvad målingen viste, og hvad forskellen skyldtes. Ét ærligt svar her er mere værd end tre rigtige diagnoser.

## Modelbesvarelsens omrids

**Læs først efter forsøget.** Dette er ikke et facit. Der findes flere forsvarlige veje; det her er hvad de har til fælles, og hvad der skiller dem.

**Fælles for enhver stærk besvarelse.** Den skelner tidligt mellem tre spørgsmål der bliver blandet sammen: hvorfor er siden langsom den 1., hvorfor timeoutede præcis ét kald, og hvorfor var tallet forkert den 4. august. De har ikke nødvendigvis samme svar, og at behandle dem som ét problem er den hurtigste vej til en forkert konklusion. Den bruger oplysning nr. 3 (kun tenants over ca. 1.000 leverandører) tidligt, fordi den alene udelukker enhver forklaring der er global for instansen — og dermed også den 97 procent CPU der stod i briefet. Den henter planen ud af Query Store inden for de første 45 minutter, fordi den udløber. Og den regner baglæns: 38 sekunder er cirka 95.000 gange et lokalt SQL-kald på 0,4 ms; hvilke mekanismer kan overhovedet producere den faktor?

Den skelner også mellem tre slags tal i briefet, og siger hvilken slags hvert er: målt (p95 fra Application Insights, med 20 procents sampling bag sig), oplyst af et menneske (Lines "hver måned siden foråret"), og udledt (grænsen omkring 1.000 leverandører, som ingen har målt præcist). Blandes de tre sammen i én tabel, ser besvarelsen mere sikker ud end den er, og det er den fejl der er dyrest at tage med ind til Jesper.

**Tre forsvarlige veje til den 1. oktober.**

*Vej A — planstabilisering.* Behandl det som et plan-valgsproblem: en plan kompileret på ét sæt forudsætninger, genbrugt under et andet. Værktøjerne er `OPTION (RECOMPILE)`, `OPTIMIZE FOR (@tenantId UNKNOWN)`, eller en tvunget plan i Query Store. Billigst, hurtigst, nul løbende kroner. Skrøbelig: den løser symptomet uden at gøre forespørgslen billigere, og den flytter en omkostning ind i hver eneste eksekvering, som skal måles og opgøres — den målbare akse her er kompileringstid i ms gange antal eksekveringer per døgn, og det tal skal stå i besvarelsen, ikke antydes.

*Vej B — indeksering og statistik.* Giv forespørgslen et dækkende indeks, og flyt statistikopdateringen ind i periodelukningsjobbet så planen kompileres på friske statistikker fra den store tenant frem for fra den første bruger der logger ind. Robust, men koster lagerplads og skrivetid på et job der i forvejen kører 65 minutter, og den omkostning skal måles, ikke gættes. Et fravalgt indeks er lige så meget en del af svaret som det valgte; modul 02 stiller det krav eksplicit til spike 4, og det gælder også her.

*Vej C — præberegning ved periodelukning.* Siden regner ikke noget den 1.; tallene blev skrevet natten før, og siden læser dem. Dyrest at bygge, umulig inden for tre udviklerdage — og den eneste af de tre der stadig står op efter præmisskiftet, fordi et præberegnet og gemt tal per definition er det tal kunden så.

Der findes en fjerde vej som ikke er forsvarlig, men som er fristende nok til at fortjene en linje: at gøre cachens TTL kortere. Det gør staleness-vinduet mindre uden at gøre det nul, det gør intet ved de 38 sekunder for den første bruger efter hver udløb, og det efterlader stadig ingen der ved hvad kunden fik at se. Det er den løsning der ser ud som et kompromis og er et udskudt problem.

Den stærke besvarelse vælger A eller B (eller A nu og B som opfølgning) til den 1. oktober, og navngiver C som det præmisskiftet tvinger frem, med en dato og et prisskilt — i stedet for at kassere de tre timers arbejde og starte forfra. Den siger også hvad den gør ved N+1'et og ved `.GetAwaiter().GetResult()` i eksportstien: det ene er nok en flad omkostning på nogle få sekunder, det andet forklarer sandsynligvis den ene 504, og de skal prissættes hver for sig, ikke pakkes ind i "vi rydder op mens vi er i gang".

**Hvad der adskiller den stærke fra den kompetente.** Den kompetente finder årsagen og retter den. Det er ikke lidt, og det er hvad de fleste .NET-udviklere med fem års erfaring ville levere på seks timer. Den stærke gør fem ting mere:

1. **Den har forudsagt forkert på mindst ét punkt, og skriver det.** Ikke i en fodnote — i kalibreringsposten, med hvad den troede, hvad målingen viste, og hvorfor forskellen opstod.
2. **Den kan sige hvad rettelsen koster om måneden, og hvad den koster den dag den holder op med at virke.** To tal, ikke ét. Det andet er det der gør faldsbetingelsen til andet end en høflighed.
3. **Den prissætter staleness i sekunder og navngiver hvem der bærer risikoen** — kunden, stifteren eller udvikleren. I et produkt hvor et forkert OTIF-tal kan flytte en leverandør ud af eskalering, er staleness ikke en teknisk parameter, det er en fordeling af ansvar.
4. **Den behandler Thomas' cache som en beslutning truffet under den information der var til rådighed den 6. august**, og skriver det. Ikke af høflighed: den anden fremstilling koster mere politisk end den vinder fagligt, og Thomas er tilbage den 21.
5. **Den siger højt at diagnosen ikke forklarer den 1. august**, og hvad det gør ved tiltroen til resten. En diagnose der forklarer to ud af tre observationer er en god diagnose. En der påstår at forklare alle tre uden at kunne det, er ikke.

Der er en sjette ting, som er sjælden nok til at den ikke er et krav: at besvarelsen foreslår hvad der skal instrumenteres **inden** den 1. oktober, så næste måneds hændelse — hvis den kommer — kan diagnosticeres på tyve minutter i stedet for på seks timer. En custom span-attribut med tenant-id og leverandørantal er tyve linjers kode, og den er forskellen på at kunne svare Line næste gang og på at skulle gøre alt det her igen.

## Sådan ser en dårlig besvarelse ud

Skrevet i første person, sådan som du selv ville formulere det, så du kan genkende dig selv.

1. *"CPU'en lå på 97 procent, så jeg skalerede App Service op til den næste størrelse og databasen til 8 vCores. Det ser bedre ud nu."* — 34.800 kr./år for at flytte en flaskehals der ikke var der. Databasen kørte på 34 procent.
2. *"Det er tydeligvis N+1 fra EF Core. Jeg har set det hundrede gange. Jeg satte `AsSplitQuery()` på og skrev forespørgslen om."* — mønstergenkendelse i stedet for måling. Måske havde du ret om at der er et N+1. Du ved bare ikke om det er 4 sekunder eller 34 af de 38, og forskellen er hele beslutningen.
3. *"Jeg lagde tre indekser på den maskerede restore fra 1. juli, og p95 faldt til 1,2 sekunder."* — du målte på 11 uger gamle statistikker uden to periodelukninger. Det tal siger noget om din restore, ikke om produktion, og du skriver det ikke.
4. *"Jeg målte efter fixet og det var 380 ms."* — én kørsel. Modul 02 kalder det for et ikke-reproducerbart tal, og det er værre end ingen tal, fordi du tager det med ind i mødet med Jesper.
5. *"Cachen er en dårlig løsning og skal fjernes."* — måske. Men du siger ikke hvad der så bærer belastningen den 1. oktober, du sætter ikke tal på staleness i den løsning du foreslår i stedet, og efter præmisskiftet fjerner du det eneste sted i systemet der ved hvad kunden fik at se.
6. *"Jeg har gennemgået alle fem hypoteser grundigt og kan ikke udelukke nogen af dem med sikkerhed."* — fire timer brugt, nul tal produceret, og en anbefaling Jesper ikke kan handle på. Analyse uden falsifikation er ikke grundighed, det er udskydelse.
7. *"Thomas er på ferie, så jeg kunne ikke få svar, og gik i gang med det jeg vidste."* — halvdelen af de skjulte oplysninger kunne du have fået af Line, Bjarne eller Azure-portalen på tyve minutter. Du skrev bare ingen spørgsmål ned.
8. *"Præmisskiftet ændrer ikke min anbefaling — reproducerbarhed er jo bare et spørgsmål om at gemme tallene."* — forsvar forklædt som dækning. Kravet er 24 måneder tilbage med lineage, og din anbefaling er en indeksændring.

De otte har én rod. Alle er hurtigere end at måle, og alle føles kompetente mens de sker. Det er derfor rækkefølgen i modul 02 er skrevet som en rækkefølge og ikke som en anbefaling: måleapparatet først, ellers er alt hvad du gør bagefter uverificerbart — også for dig selv. Genkender du dig i tre eller flere, er problemet ikke denne case; det er at måleapparatet fra spike 1 ikke er blevet driftet, og at diagnosen derfor starter forfra hver gang.

## Hvor i materialet svaret står

| Rubrikkriterium | Modul | Præcis sektionsoverskrift |
|---|---|---|
| K1 — Spørgsmål før design | 06 | `## På jobbet, uden at spørge om lov` (spørgsmålsloggen: dato, hvem spurgte, spørgsmålet, hvor lang tid det tog). Understøttes af 02, `## På jobbet: sådan konverterer dybden til autoritet uden mandat` ("stil ét spørgsmål per PR-review") |
| K2 — Det ubesvarede gjort til et vilkår | 09 | `## Tre spikes med fysisk output` → `### Spike 1: Certifikatgyldighed som tilstandsmaskine (20-25 t)` ("at turde modellere 'vi ved det ikke' som en førsteklasses tilstand") |
| K3 — Måleplanen: værktøj og forudsigelse før måling | 02 | `## Spikes: fysisk output, ellers talte det ikke` (Spike 1: ADR-001 "sådan måler vi" med hvad hvert værktøj svarer på og hvad det ikke svarer på; Spike 4: "prædiker plan, logical reads og varighed før hver kørsel") |
| K4 — Bevissikring under udløbende retention | — | **IKKE DÆKKET.** Materialet forudsætter gennemgående at fejl kan reproduceres (02, `## På jobbet: sådan konverterer dybden til autoritet uden mandat`: "reproducer enhver concurrency-fejl fra produktion i en test før du fixer den") og at instrumenteringen allerede findes. Der står intet om forensik på en overstået hændelse: hvilke kilder der udløber (Query Store-retention, App Insights-retention), hvad sampling gør ved et bagudrettet udtræk, eller hvad man sikrer i de første tredive minutter. **Mangler:** en halv side i modul 06 om bevissikring — hvad du henter ud, i hvilken rækkefølge, før det ældes ud |
| K5 — Execution plan læst uden værktøjshjælp | 02 | `## Sådan ved du at du kan det: kompetenceporten i måned 9-10` (kriterium 2: "du kan udpege den dyreste operator i en execution plan og forklare hvorfor, uden værktøjshjælp") |
| K6 — Differentialdiagnose og falsifikation | 02 | `## Hvor din leverage ligger` (kompetence 1 SQL og query-planer, 7 async og concurrency, 8 allokering og GC — "den skjulte variabel bag halvdelen af de p99-problemer folk tilskriver databasen") |
| K7 — Nedbrydning i tal med usikkerhed | 02 | `## Faldgruber` (punkt 3: "at måle én gang og kalde det et benchmark"). Kravet om to kørsler inden for 5 procent står i `## Spikes: fysisk output, ellers talte det ikke`, Spike 1 |
| K8 — Prisskilt og den ikke-tekniske side | 10 | `## Shape Up, og aldrig et nej uden prisskilt` (tredelt modtræk: pris, 80-procents-alternativet, og hvornår genvejen bliver dyr). Formen på énsideren står i 11, `## Oversæt til kroner og risiko` |
| K9 — Fravalg på en målbar akse | 01 | `## Kompetencemodellen: ti akser`, rækken "Trade-off-analyse og ADR'er": stærk = "afviser på en akse han kan måle eller prissætte, og siger hvad der ville vende valget" |
| K10 — Faldsbetingelse med tærskel og detektion | 06 | `## Sådan ved du at du kan det` (ADR hvor du siger nej til noget populært med en eksplicit genovervejelsesbetingelse; og "for hver alert kan du sige hvem der vågner, hvad de gør, og hvad der sker hvis ingen reagerer i to timer"). Understøttes af 09, `## Sådan ved du at du kan det`, ADR-tællingen |
| K11 — Cachen: staleness, risikobærer og kollegaen | 02 | `## Selvvurdering: tre niveauer med spørgsmål du ikke kan bluffe dig igennem`, Niveau 2: "kan du sige staleness-vinduet på en cache i sekunder, og hvem der bærer risikoen for det?". Watermark-halvdelen står i 09, `## Tre spikes med fysisk output` → `### Spike 3: Scorecard-metrikker som versioneret, tenant-specifik politik (30-35 t)`. **Delvist hul:** den kollegiale halvdel — at omgøre en kollegas allerede deployede fix mens han er væk — dækkes kun indirekte af 11, `## Uenighed skrives, den tales ikke` ("steelman før dit eget argument"), som forudsætter en modpart der er til stede |
| K12 — Iteration ved præmisskiftet | — | **IKKE DÆKKET.** Nærmeste naboer er 11, `## Uenighed skrives, den tales ikke` ("tab pænt, skriftligt" — men det handler om at tage fejl over for en person, ikke om at et krav skifter midt i en undersøgelse) og 10, `## Sådan ved du at du kan det`, ADR-log-kriteriet om tre "superseded" ADR'er (som måler at det er sket, ikke hvordan man gør det). **Mangler:** et afsnit — mest naturligt i modul 10 ved siden af Shape Up-afsnittet — om hvad man gør når præmissen skifter mens arbejdet kører: hvordan man afgør hvilke målinger der overlever, hvordan man deler en leverance i to datoer, og hvordan man trækker en konklusion tilbage uden at kassere det arbejde der stadig gælder |

To af tolv kriterier er ikke dækket. Begge huller er af samme slags: materialet er stærkt på at **producere** viden under kontrollerede forhold (spikes, egne services, egne målinger) og tyndt på at **forvalte** den under pres udefra — beviser der ældes, og krav der skifter mens du arbejder. Det er værd at bemærke, fordi det er præcis den situation en solution architect i et mikrofirma befinder sig i oftest.

Et tredje forbehold, som ikke er et hul men en ubalance: modul 02 og 06 er begge skrevet med den forudsætning at servicen er **din egen** — en du selv har bygget, instrumenteret og driftet. Denne case handler om en fremmed kodebase skrevet af en kollega i 2019, hvor instrumenteringen er auto-genereret og uden tenant-kontekst, og hvor den der kan forklare designet er utilgængelig i elleve dage. Materialet dækker kompetencerne, men ikke friktionen. K1 og K4 er de to kriterier der bærer den friktion, og det er værd at holde øje med om senere cases scorer systematisk lavere netop dér.

Til kvalitetsafdelingens brug: begge huller kan lukkes med under en side hver, og begge hører hjemme i moduler der findes i forvejen. De kræver ikke et nyt modul, og de skal ikke løses ved at gøre rubrikken mildere.

## Ekstern kalibrering

Din egen bedømmelse af denne besvarelse er nogenlunde værdiløs, af samme grund som modul 02 anfører: "jeg har brugt det" og "jeg forstår det" føles fuldstændig ens indefra. Tre kanaler, i prioriteret rækkefølge.

| Hvem | Hvad du sender | Hvad du spørger om — ordret |
|---|---|---|
| **En DBA eller data-platformudvikler uden for firmaet** (Aarhus .NET User Group, eller code review-byttet fra modul 12) | Planudtrækket, nedbrydningstabellen og K5-afsnittet. Ingen kundenavne, ingen rigtige datamængder — skriv om problemklassen, som modul 11 kræver | "Jeg påstår at den dyreste operator er X, og at estimatet er forkert fordi Y. Hvor er jeg upræcis, og hvilket bevis mangler jeg for at have ret?" |
| **En betalt ekstern design-review-mentor** (modul 10 sætter prisen til 15.000-25.000 kr./år for 1-2 t/md.) | ADR'en og prisskiltstabellen | "Hvilket alternativ ville du have valgt, og på hvilken akse slår det mit? Og hvad ville få dig til at vende valget?" Bed eksplicit om at få faldsbetingelsen revet i stykker — det er den del man selv skriver mildest |
| **En indkøbs- eller kvalitetsprofessionel** (DILF, eller en kunde-kontakt du allerede lytter med hos) | Kun énsideren til Jesper og Line, ingen teknik | "Hvis du fik den her mail som kunde efter at have vist et forkert OTIF-tal i din egen bestyrelse — hvad ville du så stadig være utryg ved?" Det svar kan ingen udvikler give dig |

Minimumskravet før casen tæller som bestået på "stærk": mindst én af de tre har givet substantiel modstand, og du kan pege på hvad du ændrede. Nul kritik er en dumpet test, ikke et godt resultat.

**Om kadence.** Send det inden for en uge efter timeboxen, ikke når du har pudset det færdigt. Et halvfærdigt dokument der siger "her er hvad jeg tror er svagest ved min egen diagnose" henter skarpere kritik end et poleret der ser konkluderet ud — modul 11 gør det til en regel for offentlig skrivning, og det gælder også for en enkelt læser. Book den næste læsning i kalenderen samme dag du sender, ellers bliver den til goodwill i stedet for kadence.

**Én kanal du ikke skal bruge:** Jesper. Han er ikke ekstern kalibrering, han er modtageren. At han siger ja til din anbefaling fortæller dig noget om din formidling og ingenting om din diagnose — i et nimandsfirma kan man vinde en faglig diskussion ved at være den der talte sidst, og casen her giver dig rigelig anledning til det.
