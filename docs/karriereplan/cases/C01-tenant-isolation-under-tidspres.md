# C01 — Tenant-isolation under tidspres

| | |
|---|---|
| **Type** | Trade-off-kata under tidspres |
| **Primært modul** | 01 — Rollen: hvad en Solution Architect faktisk laver |
| **Sekundære moduler** | 03 (Azure-arkitektur), 08 (Compliance og risiko), 04 (Systemdesign og integration) |
| **Timebox** | 8 timer, hård. Præmisskiftet lægges oveni og må koste maks. 30 minutter ekstra |
| **Sværhedsgrad** | 3 af 5. Svær på dømmekraft, let på teknik. Giver mening i **måned 4-7**: før måned 4 har du ikke egne Azure-tal at prissætte med, og efter måned 8 er den for nem, fordi flagskibsspiken i modul 08 har givet dig svarene gratis. Kør den én gang i måned 4-5 og igen i måned 10 med samme rubrik og sammenlign scorerne |
| **Afleveringsformat** | Otte artefakter: kravsspørgsmålsliste (1 side, tidsstemplet), løsningsdesign (maks. 5 sider, C4 kontekst + container), fravalgsnotat (1 side), kostmodel (regneark + 1 sides sammenfatning, med spænd i procent), risikoliste (1 side, 7 risici), ADR (maks. 1,5 side, MADR-minimal), notat til stifteren (præcis 1 side, ikke-teknisk), selvvurdering (0,5 side). I alt maks. 11 sider plus ét regneark |

> Alle personer og den tyske koncern i denne case er opdigtede. Tallene for LeanLinkings egen platform er konstrueret, men i den størrelsesorden en ni-mandsvirksomhed reelt ligger i. Azures listepriser er **ikke** oplyst — dem henter du selv via Retail Prices API, og gætter du, mærker du gættet som gæt.

## Situationen

Fredag den 11. september 2026, kl. 08.40. Jens kommer ind på kontoret i Skejby med telefonen i hånden og siger, at vi er kommet videre i Bergmann-Kessler.

Bergmann-Kessler Industriegruppe SE er en tysk industrikoncern i Ludwigsburg: pumper og drivteknik, elleve fabrikker i fem lande, en indkøbsorganisation på tres mennesker og en kvalitetsafdeling der selv kører surveillance audits hos deres leverandører. De har haft RELATIONS i pilot siden juni med to indkøbere og fyrre leverandører. Nu vil de op i fuld skala, og de har lagt det i et formelt Lastenheft med tilbudsfrist den 2. oktober kl. 12.00 CET.

Katrine fra salg har oversat de relevante afsnit til dansk og lagt et resumé i Teams i går aftes. Der står fire ting: alle data forbliver i EU; kundens data skal være fysisk adskilt fra andre kunders, og adskillelsen skal kunne dokumenteres; kunden skal have sin egen krypteringsnøgle; og kundens revisor skal kunne få adgang til et revisionsspor over hvad der er sket med deres leverandører, uden at kunne se andre kunders data. Nedenunder står "4.000 leverandører" og "3-årig kontrakt". Resuméet er på halvanden side. Det oprindelige Lastenheft er på 34 sider på tysk og ligger i mappen.

På salgsmødet den 3. september sagde Jens "das können wir" til det hele. Han husker det selv som "vi kan holde data i EU og adskille dem, det er jo det vi gør". Katrine sendte dagen efter en opfølgende mail til deres Head of Group Procurement, hvor der blandt andet står *"dedicated database per customer available"*. Den mail er nu en del af udbudskorrespondancen.

RELATIONS kører i dag på én Azure SQL-database med delt skema, `tenant_id` på 140 tabeller og EF Core global query filters. 34 tenants. Dokumenterne ligger i én storage account med en container pr. tenant. Alt står i West Europe. Thomas har bygget det meste af det og mener ikke, der er noget i vejen med det. Rasmus har som den eneste ud over Jens produktionsadgang, og han er på ferie til den 22.

Jens' egne ord i morges: "Vi skal ikke tabe den her på en teknikalitet. Sig til hvis der er noget vi ikke kan — men sig det inden fredag, for jeg skal have en pris ind til Katrine." Han har ikke spurgt om noget teknisk. Han har spurgt om et tal.

Du har otte timer. Du har ikke set kontrakten med den norske kunde, som Katrine mener "spurgte om noget lignende sidste år". Du ved ikke, hvad Bergmann-Kessler selv betragter som personoplysninger i deres materiale. Der ligger en kalenderinvitation fredag kl. 14.00 der hedder "Bergmann-Kessler — go/no-go", med Jens, Katrine og dig på deltagerlisten.

## Det du skal aflevere

| # | Artefakt | Format | Krav der ikke kan forhandles |
|---|---|---|---|
| 1 | **Kravsspørgsmål** | 1 side, tidsstemplet pr. spørgsmål | Skrevet **før** første diagram og før første teknologinavn. Hvert spørgsmål har én linje om hvad svaret ville ændre i designet |
| 2 | **Løsningsdesign** | Maks. 5 sider | C4 kontekst + container for den valgte model. Én tabel over hvad der er **delt** og hvad der er **adskilt** pr. lag: compute, database, blob, nøgler, telemetri, backup, deployment |
| 3 | **Fravalgsnotat** | 1 side i alt | To forkastede alternativer, hver afvist på **én navngiven, målbar akse med et tal** — ikke to |
| 4 | **Kostmodel** | Regneark + 1 sides sammenfatning | Tre tenancy-modeller × mindst fire omkostningsposter × to volumener, i DKK/md ekskl. moms. **Et spænd i procent pr. model** og en note om hvilken post der driver spændet. Volumentallet skal være en celle, ikke en konstant |
| 5 | **Risikoliste** | 1 side, 7 risici | Hver med konsekvens i kroner **eller** kalenderdage, sandsynlighed i tre trin, navngivet ejer, og en tidlig indikator man kan se før det sker |
| 6 | **ADR** | Maks. 1,5 side, MADR-minimal | Afsnittet "Dette ville få os til at vælge om" med mindst tre betingelser, hver med en tærskel og en enhed |
| 7 | **Notat til Jens** | Præcis 1 side | Nul teknisk jargon. Hvad vi kan love, hvad vi ikke kan, hvad et ja koster i kr./md og udviklerdage, to muligheder og én anbefaling. Skal kunne læses på fire minutter |
| 8 | **Selvvurdering** | 0,5 side | Hvilke af dine egne kravsspørgsmål besvarede du til sidst med et gæt, og hvilket af de gæt bærer mest af designet |

Artefakt 4 er det der har et tal **med en usikkerhed**. Artefakt 7 er det der skal kunne læses af en ikke-teknisk læser — og det er det eneste af de otte, der reelt bliver brugt til noget om fredagen.

## Skjulte oplysninger

Du må kun læse svaret på et spørgsmål, du **faktisk har skrevet ned** på artefakt 1, før du begyndte at designe. Skriver du ni spørgsmål og læser fjorten svar, har du ikke lavet katáen — du har læst en løsning.

| # | Spørgsmål du kunne stille | Svaret du får |
|---|---|---|
| 1 | Er de 4.000 leverandører registrerede eller aktive? | 4.000 er antal rækker i deres SAP vendor master på tværs af syv company codes. Dedupliceret på VAT/LEI er der ca. **2.600 juridiske enheder**. **1.150** har haft en transaktion inden for 12 måneder. Den volumen du regner med, er 3,5 gange for høj |
| 2 | Hvad står der ordret i Lastenheftet om adskillelse? | *"Logische **oder** physische Trennung der Mandantendaten, dokumentiert und durch einen unabhängigen Dritten prüfbar."* Logisk adskillelse er tilladt. Kravet er, at den kan **efterprøves af en tredjepart**. Katrines danske resumé er en fejloversættelse |
| 3 | Hvad mener de konkret med "egen krypteringsnøgle"? | Kravet er skrevet af koncernens CISO-kontor. Ved forespørgsel: nøglen skal kunne **spærres af kunden**, og spærringen skal gøre data utilgængelige inden for 24 timer. De kræver ikke HSM, ikke FIPS-niveau, ikke egen Key Vault-instans. De kræver en dokumenteret spærringsproces og en test af den |
| 4 | Hvad skal revisoren faktisk kunne? | Ekstern revisor (Süddeutsche Revision GmbH) skal **én gang årligt** kunne få: hvem så hvad hvornår på deres egne leverandører, hvem ændrede status på en nonconformity eller en CAPA, og bevis for at posterne ikke er efterredigeret. De vil ikke have live-adgang. De accepterer et signeret udtræk med en dokumenteret integritetskontrol |
| 5 | Er der en Q&A-runde, og hvornår lukker den? | Ja. Skriftlige spørgsmål kan stilles til **18. september kl. 17.00**, og svarene er bindende for begge parter og deles med alle bydende. Der er endnu ikke stillet ét eneste spørgsmål fra nogen. Det står på s. 4 i Lastenheftet |
| 6 | Hvad har Jens præcis lovet, og hvad står der på skrift? | Der findes ikke noget referat af den 3. september. Jens husker en generel bekræftelse. Katrines mail af 4. september siger "dedicated database per customer available" og er sendt. Der er forskel på hvad der er sagt og hvad der er skrevet, og kun det skrevne er i korrespondancen |
| 7 | Hvad koster platformen i dag pr. måned, og hvordan fordeler det sig? | 11.400 DKK/md ekskl. moms for alle 34 tenants: SQL elastic pool 4.100, App Service Plan 2.900, blob storage inkl. transaktioner 950, Log Analytics + App Insights 1.150, backup og long-term retention 720, øvrigt 1.580. Ingen har regnet det ud pr. tenant. Der er ingen `tenant`-tag på nogen ressource |
| 8 | Hvad er kontrakten værd? | 480.000 DKK/år i licens plus 220.000 i onboarding, treårig med option på to. Ca. 11 % af LeanLinkings samlede ARR. Den største eksisterende tenant har 620 leverandører og betaler 190.000/år |
| 9 | Hvem drifter det, og hvad kræver kunden i svartid? | Rasmus, som eneste ud over Jens, i arbejdstiden CET. Ingen formel vagtordning, ingen dokumenteret restore-test. Lastenheftet kræver svartid på **4 timer ved P1 døgnet rundt**, og en årlig restore-test med skriftlig rapport |
| 10 | Hvad kræver de om opbevaring og sletning? | Revisionsspor skal opbevares i **10 år**. Personoplysninger om leverandørkontakter skal slettes efter **24 måneders inaktivitet**. Begge krav står i samme bilag, og begge rammer den samme tabel. Ingen hos kunden har bemærket det |
| 11 | Har de klassificeret det data, de vil lægge ind? | **Det ved vi ikke.** Deres indkøbschef har ikke spurgt sin egen sikkerhedsafdeling, om leverandørkontrakter, auditrapporter og claims-data falder i klassen "intern" eller "vertraulich" internt hos dem. Svaret kommer tidligst efter kontraktunderskrift, muligvis først ved deres næste interne revision. Det er ikke en manglende oplysning, det er et arkitekturvilkår: designet skal kunne tåle at svaret bliver det strengeste |
| 12 | Hvordan kommer deres data ind? | SAP S/4HANA, syv company codes. De tilbyder IDoc-eksport til en SFTP-drop, ikke et API. Deres SAP-team har seks ugers kø og leverer ikke ændringer i eksportformatet inden for kontraktens første år. Peppol bruges kun til fakturering og er uden for scope |
| 13 | Har vi ISO 27001, og kræves den? | Nej, vi har den ikke. Lastenheftet kræver ISO 27001 **eller** "gleichwertige nachgewiesene Kontrollen ved kontraktunderskrift, godkendt af kundens revisor". Vi har hverken certifikat, SoA eller et besvaret spørgeskema der er dokumenteret frem for påstået |
| 14 | Er der andre kunder i pipelinen med samme krav? | To. En norsk offshore-leverandør spurgte om noget lignende i marts, fik nej, og købte alligevel. En fransk retailkoncern er i tidlig dialog og har ikke nævnt nøgler. Ingen andre af de 34 nuværende tenants har krævet dedikeret noget som helst |

## Præmisskiftet

**Åbnes først når 4 timer og 48 minutter af timeboxen er gået (60 %). Ikke før. Sæt en timer.**

Kunden svarer på Q&A-runden den 18. september. Tre linjer i svaret ændrer opgaven:

1. **Nøglen skal ligge i kundens egen Azure-tenant.** Koncernens CISO-kontor har præciseret: kundens eget Key Vault i deres eget abonnement, og de skal kunne spærre nøglen ensidigt, uden varsel, med effekt inden for 24 timer. Det er ikke længere en dokumenteret proces — det er en teknisk rettighed hos dem.
2. **Det schweiziske datterselskab kommer med i samme kontrakt.** Bergmann-Kessler Antriebstechnik AG i Winterthur, 340 leverandører. Deres juridiske afdeling kræver, at deres leverandørdata **ikke forlader Schweiz**. Koncernens eget Lastenheft siger på s. 11 "Alle Daten verbleiben innerhalb der EU".
3. **Pengene er skrumpet.** Indkøbsafdelingen har gjort det indkøbsafdelinger gør: onboarding-honoraret er forhandlet fra 220.000 til 95.000 DKK. Jens sætter derfor et loft: maks. **2.500 DKK/md ekstra Azure-forbrug** for denne kunde og **15 udviklerdage** i alt. Licensprisen står fast.

**Hvad skiftet er en test af**

- Om du **regner om** frem for at argumentere om, hvorvidt dit oprindelige design egentlig stadig holder. En opdateret kostmodel inden for tres minutter er beviset; en velformuleret forklaring er det ikke.
- Om du kan sige højt, hvilke af dine beslutninger der **ikke** er berørt, og hvorfor. En kandidat der laver alt om, har ikke forstået sit eget design bedre end en der ikke laver noget om.
- Om din egen faldsbetingelse fra ADR'en faktisk **udløses** af linje 1 — og om du så følger den, eller finder på en grund til at lade være. Dette er det skarpeste enkeltmålepunkt i hele katáen.
- Om du opdager, at linje 2 modsiger kundens eget krav på s. 11, og behandler det som et **spørgsmål til kunden** frem for som et designproblem, du selv skal løse. Bemærk at Schweiz har en gyldig tilstrækkelighedsafgørelse; panikker du over "tredjeland", løser du et juridisk problem der ikke findes, i stedet for det kontraktuelle der gør.
- Om loftet i linje 3 får dig til at ændre **hvad du tilbyder**, ikke bare hvad du bygger. Et nej med et prisskilt er et lovligt svar i et udbud.

## Rubrik

Tolv kriterier, hvert scoret 0-3, med vægt. Maksimum er 87 point. Ankrene er tællelige med vilje: en bedømmer skal kunne sætte scoren uden at kende kandidaten og uden at bruge ordet "god".

| # | Kriterium | Vægt | Maks. point |
|---|---|---|---|
| K1 | Kravsspørgsmål før første teknologinavn | 3 | 9 |
| K2 | Spørgsmålene rammer de akser der flytter designet | 2 | 6 |
| K3 | Det allerede afgivne løfte og den bindende kanal | 2 | 6 |
| K4 | Tre tenancy-modeller prissat i kroner med usikkerhed | 3 | 9 |
| K5 | Kost pr. tenant mod kontraktværdi, og hvad der flytter tallet | 2 | 6 |
| K6 | Fravalgene afvist på en målbar akse | 3 | 9 |
| K7 | Faldsbetingelsen | 3 | 9 |
| K8 | Revisionssporet: revisor får svar uden at se andre tenants | 2 | 6 |
| K9 | Krypteringsnøglen: hvad den koster og hvad den brækker | 2 | 6 |
| K10 | Iteration ved præmisskiftet | 3 | 9 |
| K11 | Én side stifteren kan handle på | 2 | 6 |
| K12 | Det arkitektur ikke kan løse | 2 | 6 |
| | **I alt** | **29** | **87** |

### K1 — Kravsspørgsmål før første teknologinavn (vægt 3)

*Findes fordi:* det er den enkeltfejl unge arkitektkandidater oftest afvises på — at svare som senior udvikler og springe til teknologi før volumen, budget, SLA og datafølsomhed er kendt.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen spørgsmålsliste, eller listen er skrevet efter designet. Første Azure-tjeneste nævnt inden for de første 20 minutter |
| 1 | 3-7 spørgsmål, ikke tidsstemplede, og mindst ét er et løsningsforslag i spørgeform ("skal vi bruge RLS?") |
| 2 | 8-11 tidsstemplede spørgsmål skrevet før første diagram, ingen teknologinavne, mindst fem rammer skjulte oplysninger |
| 3 | 12+ tidsstemplede spørgsmål, ingen teknologinavne, mindst otte rammer skjulte oplysninger, og listen er gennemgået igen til sidst med markering af hvilke der **stadig** er ubesvarede i det afleverede design |

### K2 — Spørgsmålene rammer de akser der flytter designet (vægt 2)

*Findes fordi:* tolv spørgsmål der alle handler om samme akse er ét spørgsmål. De fem dyre akser her er: faktisk volumen, ordret kravformulering, hvad revisor konkret skal kunne, kontraktværdi mod infrastrukturomkostning, og hvem der drifter med hvilken svartid.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen af de fem akser berørt |
| 1 | 1-2 af de fem |
| 2 | 3-4 af de fem, og mindst ét spørgsmål indeholder selv et tal ("er de 4.000 registrerede eller aktive?") |
| 3 | Alle fem, plus mindst ét spørgsmål der ville have afdækket en modsigelse i kundens eget materiale, og hver linje har en note om hvad svaret ville ændre |

### K3 — Det allerede afgivne løfte og den bindende kanal (vægt 2)

*Findes fordi:* et løfte afgivet af en anden er et arkitekturvilkår på linje med en latenskrav. Det kan ikke ignoreres og det kan ikke overtrumfes teknisk.

| Score | Sådan ser det ud |
|---|---|
| 0 | Løftet nævnes ikke, eller designet bygger på det som om det var et krav |
| 1 | Løftet nævnes som et problem, men der skelnes ikke mellem hvad Jens sagde mundtligt og hvad Katrine skrev |
| 2 | Skelner mellem mundtligt løfte, sendt mail og udbuddets ordlyd, og foreslår én konkret formulering til stifteren der ikke kræver at nogen trækker noget tilbage |
| 3 | Ovenstående, plus at Q&A-runden med frist 18. september bruges: mindst tre spørgsmål er skrevet i den form de skal stilles til kunden, og der står hvad et bindende svar koster hvis det falder ud til den anden side |

### K4 — Tre tenancy-modeller prissat i kroner med usikkerhed (vægt 3)

*Findes fordi:* uden tal er tre modeller tre meninger. Usikkerheden er ikke en svaghed ved modellen, den er en del af leverancen.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen tal, eller kun "billigere" og "dyrere" |
| 1 | Ét samlet tal pr. model, ingen poster bag, ingen usikkerhed |
| 2 | Tre modeller × mindst fire poster (compute, SQL, blob, telemetri, backup, nøglehåndtering) i DKK/md, med et spænd i procent pr. model og en kilde pr. pris |
| 3 | Ovenstående ved **to** volumener (1.150 aktive og 2.600 juridiske enheder), spændet er begrundet i den ene post der driver det, og volumentallet er en celle i regnearket — så præmisskiftet kan regnes om på under ti minutter |

### K5 — Kost pr. tenant mod kontraktværdi, og hvad der flytter tallet (vægt 2)

*Findes fordi:* et tal uden en nævner er ubrugeligt for en stifter. 2.400 kr./md er billigt ved 40.000 i månedlig omsætning og uacceptabelt ved 4.000.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen kobling mellem hvad løsningen koster og hvad kunden betaler |
| 1 | Kontraktværdien nævnes, men der regnes ikke |
| 2 | Dedikeret infrastruktur angivet som procent af kundens månedlige omsætning, og den post der udgør over 40 % af den er navngivet |
| 3 | Ovenstående, plus en skrevet regel af formen "dedikeret X tilbydes fra Y kr. ARR", plus hvad reglen ville betyde for de 34 eksisterende tenants hvis den gjaldt generelt |

### K6 — Fravalgene afvist på en målbar akse (vægt 3)

*Findes fordi:* forskellen på kompetent og stærk i kompetencemodellen er præcis dette: at afvise på en akse man kan måle eller prissætte i stedet for på smag.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen alternativer, eller alternativer afvist med "det er ikke best practice" / "det skalerer ikke" |
| 1 | To alternativer navngivet, afvist på smag eller på en akse uden tal |
| 2 | To alternativer, hver afvist på **én** navngiven målbar akse med et tal: kr./md, timers nedetid ved senere migrering, antal tenants ramt ved nøglespærring, eller timer til per-tenant restore |
| 3 | Ovenstående, plus at kandidaten skriftligt kan argumentere **for** det fravalgte alternativ i mindst fem linjer, og navngiver det tal i sin egen model han er mest usikker på |

### K7 — Faldsbetingelsen (vægt 3)

*Findes fordi:* et dokument uden en faldsbetingelse er en begrundelse, ikke en beslutning. Og fordi præmisskiftet om lidt skal kunne ramme den.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ingen |
| 1 | "Vi revurderer om et år", eller "hvis kravene ændrer sig" |
| 2 | Mindst én betingelse med tærskel og enhed: "hvis kunden kræver ensidig nøglespærring med effekt under 24 timer", "hvis per-tenant restore overstiger 4 timer" |
| 3 | Mindst tre betingelser, hver med tærskel, hvem der opdager den, og hvad der så konkret gøres — og mindst én af dem udløses faktisk af præmisskiftet, hvilket kandidaten selv konstaterer skriftligt |

### K8 — Revisionssporet: revisor får svar uden at se andre tenants (vægt 2)

*Findes fordi:* det er casens egentlige domænekrav, og fordi den stærke version af "compliance-by-design" er at en revisor om tre år får svar uden at grave i logfiler.

| Score | Sådan ser det ud |
|---|---|
| 0 | Ikke behandlet, eller revisor får en læsebruger i produktion |
| 1 | "Vi filtrerer på `tenant_id`", uden at sige hvordan det bevises over for en tredjepart |
| 2 | Auditlog adskilt fra diagnostisk log; leverancen er et afgrænset udtræk, ikke en adgang; mindst tre felter pr. post navngivet (aktør, tidspunkt, objekt, før/efter, kilde) |
| 3 | Ovenstående, plus hvordan en efterredigeret post opdages maskinelt, plus et skrevet svar — ikke et forbehold — på hvad der sker når 10 års opbevaring møder sletning efter 24 måneders inaktivitet i den samme post |

### K9 — Krypteringsnøglen: hvad den koster og hvad den brækker (vægt 2)

*Findes fordi:* fejlklasse-kolonnen er den en senior udvikler glemmer. "Mere sikkert" er ikke en analyse; "utilgængelig vault vælter tenanten i N timer" er.

| Score | Sådan ser det ud |
|---|---|
| 0 | "Vi bruger customer-managed keys", uden pris og uden konsekvens |
| 1 | Nævner Key Vault og en pris, men ingen fejlklasse |
| 2 | Pris hentet frem for gættet (eller eksplicit mærket som gæt), plus mindst to fejlklasser: tabt nøgle, utilgængelig vault, rotation midt i en batch |
| 3 | Ovenstående, plus blast radius i **antal tenants og timer** for hver fejlklasse, plus hvad kunden får ret til at gøre og hvad LeanLinking skal kunne bevise bagefter |

### K10 — Iteration ved præmisskiftet (vægt 3)

*Findes fordi:* det er det ene observerbare kriterium i modul 01 der ikke kan trænes ved at læse, og fordi det er præcis det danske interviewere måler.

| Score | Sådan ser det ud |
|---|---|
| 0 | Forsvarer det oprindelige design. Intet tal ændres |
| 1 | Ændrer designet, men regner ikke om — eller regner om uden at sige hvad der nu er blevet forkert i det første design |
| 2 | Inden for 60 minutter: opdateret kostmodel, én navngiven beslutning der er omgjort, og én navngiven beslutning der **ikke** er berørt, med begrundelse |
| 3 | Ovenstående, plus at kandidaten henviser til sin egen faldsbetingelse som udløst, plus at modsigelsen mellem s. 11 og det schweiziske krav identificeres og sendes retur som spørgsmål frem for designet rundt om |

### K11 — Én side stifteren kan handle på (vægt 2)

*Findes fordi:* det eneste af de otte artefakter der reelt bliver brugt om fredagen. Et design ingen beslutningstager kan handle på, er en tilfældighed der overlevede.

| Score | Sådan ser det ud |
|---|---|
| 0 | Teknisk notat, eller over to sider |
| 1 | Én side, men konklusionen er en anbefaling uden pris eller uden alternativ |
| 2 | Maks. én side, nul jargon, indeholder alle fire: hvad vi kan love, hvad vi ikke kan, hvad et ja koster i kr./md og udviklerdage, to muligheder med én klar anbefaling |
| 3 | Ovenstående, plus at en ikke-teknisk læser kan gengive konsekvensen korrekt bagefter, plus at der står præcis hvilken sætning der skal skrives til kunden og hvilken der ikke må skrives |

### K12 — Det arkitektur ikke kan løse (vægt 2)

*Findes fordi:* et optimistisk ja i et bindende udbudssvar skaber kontraktuel eksponering for arbejdsgiveren. Det korrekte svar er nej med et prisskilt.

| Score | Sådan ser det ud |
|---|---|
| 0 | Alle kundens krav er besvaret med et design |
| 1 | Nævner at noget bliver svært, uden at pege på hvilket krav |
| 2 | Navngiver mindst to krav der ikke er arkitekturproblemer — 4 timers svartid døgnet rundt uden vagtordning, og ISO 27001 ved kontraktunderskrift — og siger hvad hvert koster i bemanding eller kalendertid |
| 3 | Ovenstående, plus et konkret formuleret forbehold eller modforslag til udbuddet for hvert af dem, plus én sætning om hvad et optimistisk ja ville have kostet kontraktuelt |

**Beståelsesgrænse:** mindst **55 af 87 point (63 %)**, **og** mindst 2 på hver af K1, K4, K6, K7 og K10, **og** intet 0 på noget kriterium. Falder ét af de tre led, er katáen dumpet uanset totalen — en besvarelse der scorer 60 point og har et 0 på fravalg, er ikke en god besvarelse med en svaghed, det er et designdokument uden arkitektur.

**"Stærk" kræver:** mindst **70 af 87 (80 %)**, **og** 3 på mindst tre af K4, K6, K7 og K10, **og** mindst 2 på alle tolv kriterier, **og** at timeboxen er holdt (maks. 8 timer 30 minutter inklusive præmisskiftet). Det svarer til kompetencemodellens formulering i modul 01: kompetent på alle akser og stærk på ingen er en dumpet port, fordi rollen bæres af trade-off-analyse og faldsbetingelser. Er du over 70 point men over tid, er scoren ikke gyldig — evnen der testes, er at levere et forsvarligt design **inden for** otte timer, ikke at levere et godt design.

## Kalibrering: skriv dette ned FØR du går i gang

Fem forudsigelser. Skriv dem i en fil, gem den, rør den ikke før timeboxen er slut. Uden dette punkt er hele katáen en øvelse i at have ret bagefter.

1. **Hvilken af de tre tenancy-modeller ender du med?** Skriv navnet nu, før du har læst ét eneste svar i tabellen over skjulte oplysninger.
2. **Hvor mange af dine kravsspørgsmål bliver besvaret med noget der reelt ændrer designet?** Skriv et tal mellem 0 og 14.
3. **Hvad koster den dyreste af de tre modeller i DKK/md for denne ene kunde?** Skriv ét tal og ét spænd, fx "2.400 kr., ±40 %". Efterprøves mod din egen kostmodel til sidst.
4. **Hvor mange af de otte timer går til kostmodellen?** Skriv et tal med én decimal. De fleste skriver 1,5 og bruger 3,5.
5. **Hvad bliver sværest?** Én sætning, maks. 15 ord.

**Hvad var jeg sikker på og tog fejl om** — udfyldes efter timeboxen, mindst tre linjer, hver af formen "jeg troede X, det var Y, årsagen var Z". Er feltet tomt eller siger "ingenting", er kalibreringen dumpet — ikke perfekt. En kandidat der ikke tog fejl om noget på otte timer i et ufuldstændigt oplyst problem, har ikke undersøgt problemet.

## Modelbesvarelsens omrids

**LÆS FØRST EFTER FORSØG.** Dette er ikke et facit. Det er et omrids af, hvad en stærk besvarelse indeholder, og hvilke veje der er forsvarlige.

**Tre forsvarlige veje**

- **A. Pool med hærdet logisk adskillelse.** Fortsat delt database, men Row-Level Security på `SESSION_CONTEXT` oveni EF Cores query filters, cross-tenant abuse-tests i CI på hvert endpoint, kundeadministreret nøgle på en dedikeret storage account til deres dokumenter, og et evidenspakke-udtræk som en tredjepart kan efterprøve. Billigst. Falder på ét punkt: nøglespærring med effekt inden for 24 timer rammer alle tenants, der deler den ressource — blast radius er 34, ikke 1. Er den akse ikke prissat, er vejen ikke valgt, den er antaget.
- **B. Bridge-modellen.** De 33 små tenants bliver i poolen; Bergmann-Kessler får egen database i samme elastic pool, egen storage account med egen nøgle, delt compute og delt deployment-pipeline. Dyrere pr. måned end A, men blast radius for nøglespærring er 1, og per-tenant restore bliver et tal du kan skrive i tilbuddet. Kræver, at du skriver **tærsklen** ned: ved hvilken ARR eller hvilket kontraktkrav flyttes en tenant fra pool til silo. Tærsklen er artefaktet, ikke modellen.
- **C. Fuld silo.** Eget resource group, egen SQL, egen storage account, egen Key Vault, egen deployment. Sælgeligt, entydigt at dokumentere over for en revisor, og dyrest — både i kr./md og i de udviklerdage der går til at gøre provisionering og migrering gentagelig for én kunde. Forsvarlig, hvis du kan vise, at kontraktværdien bærer den, og hvis du samtidig siger, hvad den koster ved kunde nummer to og tre.

Alle tre er forsvarlige. Den urimelige er kun én: at vælge C fordi mailen sagde "dedicated database per customer", uden at have læst den tyske ordlyd.

**Hvad en stærk besvarelse desuden indeholder**

- Volumentallet er 1.150 eller 2.600 — ikke 4.000 — og der står hvorfor, i én linje.
- Mindst tre skriftlige spørgsmål formuleret til Q&A-runden inden 18. september, inklusive ét om ordlyden af adskillelseskravet og ét om hvad revisoren konkret skal modtage.
- To krav er besvaret med et nej og et prisskilt: 4 timers P1-svartid døgnet rundt (kræver bemanding, ikke arkitektur) og ISO 27001 ved underskrift (kræver kalendertid og et SoA-arbejde, ikke en beslutning).
- Konflikten mellem 10 års revisionsspor og 24 måneders sletning er nævnt, med et valgt svar: adskil personoplysningerne fra beviset, eller dokumentér et retsgrundlag der går forud. Ikke et forbehold.
- Fund undervejs der ikke stod i opgaven, men som en der læste systemet ville finde — for eksempel at leverandørnavne og certifikatnumre kan ende i telemetrien, og at et EU-residenskrav derfor også gælder Application Insights og enhver tredjepartstjeneste i supportstien.

**Hvad der adskiller den stærke fra den kompetente**

| Den kompetente | Den stærke |
|---|---|
| Prissætter tre modeller | Prissætter tre modeller ved to volumener, siger hvilken post der bærer 70 % af spændet, og har volumen som en celle så præmisskiftet koster ti minutter |
| Skriver en faldsbetingelse | Skriver tre, med tærskel og ejer, og konstaterer selv efter præmisskiftet at én af dem er udløst |
| Afviser et alternativ | Kan argumentere overbevisende for det afviste alternativ, og siger hvilket af sine egne tal han er mest usikker på |
| Løser alle kundens krav | Siger nej til to af dem med en pris på, og formulerer forbeholdet i tilbudssprog |
| Håndterer stifterens løfte ved at ignorere det | Skelner mellem det talte og det skrevne løfte, og giver Jens én sætning han kan sende, som hverken lyver eller trækker noget tilbage |
| Ændrer designet efter præmisskiftet | Siger også hvad der **ikke** ændrer sig, og hvorfor |

## Sådan ser en dårlig besvarelse ud

Skrevet som du selv ville formulere det. Formålet er genkendelse, ikke skam.

1. *"Vi laver bare database-per-tenant, så er de tilfredse."* — Sagt inden nogen har læst den tyske ordlyd. Du har brugt 40 % af dit budget på at opfylde et krav, der ikke findes, og du opdager det aldrig, fordi kunden ikke retter dig når du overopfylder.
2. *"Jeg regner med 4.000 leverandører, det står jo i udbuddet."* — Hele din kostmodel er 3,5 gange for stor, og din anbefaling følger med. Det er ikke en regnefejl, det er en manglende sætning i din spørgsmålsliste.
3. *"Vi bruger Managed HSM, det er den rigtige måde at lave customer-managed keys på."* — Du har valgt den dyreste nøgleløsning til et krav, der viste sig at være "kunden skal kunne spærre den". Du har heller ikke slået prisen op, du har genkendt navnet.
4. *"Jeg ville gerne have spurgt Jens hvad han præcis havde lovet, men det virkede akavet, så jeg antog det værste og designede efter det."* — Det dyreste spørgsmål du ikke stillede. Fire minutters ubehag byttet for 15 udviklerdage.
5. *"Kostmodellen lavede jeg til sidst, den nåede jeg ikke helt færdig."* — Så har du lavet et designdokument. Kostmodellen er ikke bilaget til beslutningen, den **er** beslutningen, og det er den eneste artefakt Jens faktisk skal bruge om fredagen.
6. *"Præmissen ændrede sig, men mit design holder faktisk stadig, hvis man ser på det på den her måde."* — Det er forsvar. Det er også præcis den sætning en interviewer lytter efter, og den eneste der ikke kan bortforklares bagefter.
7. *"Revisoren får bare en read-only bruger til produktionen"* — eller til Application Insights. Du har nu givet en tredjepart adgang til 34 tenants' data for at opfylde ét krav om at kunne se én tenants revisionsspor. Det er selve det krav, du blev bedt om at opfylde, vendt på hovedet.
8. *"Jeg skrev at vi har styr på ISO 27001, vi tager den jo i næste kvartal."* — Du har skabt kontraktuel eksponering for din arbejdsgiver i et bindende udbudssvar. Det korrekte svar var "nej, og her er hvad vi har i stedet, og hvornår" — og det dræber handlen sjældnere end du tror.

## Hvor i materialet svaret står

Ubarmhjertig version. To kriterier er ikke dækket af noget modul, og det er et fund i materialet, ikke i casen.

| Kriterium | Modul | Præcis sektionsoverskrift | Hvad du henter der |
|---|---|---|---|
| **K1** Kravsspørgsmål før teknologinavn | 01 | `### Øvelse 3: Trade-off-kata på tid` | "Mindst otte kravsspørgsmål stillet **før** første diagram" — kravet, timeboxen og selvkontrollen til sidst |
| **K2** Spørgsmålene rammer de dyre akser | 10 | `## Kvalitetsattribut-scenarier: din del af kravarbejdet` | Den seksdelte form, og reglen om at responsmålet altid er et tal. Suppl.: 01 `## Kompetencemodellen: ti akser`, rækken "Kravsfremdragelse og NFR med tal" |
| **K3** Det afgivne løfte og den bindende kanal | — | **IKKE DÆKKET** | Materialet dækker dine **egne** aftaler (12 `## Uge 1: fem ting du kan gøre uden at spørge om lov`, opsummeringsmailen) og skriftlig uenighed (11 `## Uenighed skrives, den tales ikke`). Der mangler: hvordan man håndterer et løfte en anden allerede har afgivet til en kunde, forskellen på et mundtligt og et skriftligt tilsagn i en udbudskorrespondance, og at en formel Q&A-runde er en arkitekturkanal med en frist |
| **K4** Tre modeller prissat med usikkerhed | 03 | `### Spike 1 — Multi-tenant isolationsmodel for leverandørdokumentation (12-16 t)` | "Cost-model for alle tre ved 50, 500 og 5.000 tenants" og den talfæstede tærskel for pool mod silo. Suppl.: 03 `## Budgetloftet: 400 DKK/md, hård alert ved 600` for Retail Prices-disciplinen |
| **K5** Kost pr. tenant mod kontraktværdi | 12 | `## Tre spikes med fysisk output` (punkt 4, "Enhedsøkonomi pr. tenant") | Modellen der fordeler Azure-forbrug pr. tenant, og grafen omkostning pr. tenant mod hvad tenanten betaler. Også: "findes der ikke tags pr. tenant, *er* dét fundet" |
| **K6** Fravalg på en målbar akse | 07 | `### G5 — ADR-serie om lejerisolation i dokumentlageret (måned 3-4, 1 uge, parallelt)` | De fire optioner, kravet om mindst to ADR'er med navngivne afviste alternativer, og at beslutningen skal adressere sletning, datalokalisering for en tysk kunde og pris pr. lejer |
| **K7** Faldsbetingelsen | 09 | `## Sådan ved du at du kan det` (rækken "ADR-tællingen") | "Hvert dokument har et afsnit om hvad der ville få os til at ændre beslutningen. Mangler det, er det en begrundelse, ikke en beslutning." Suppl.: 04 `## Saadan ved du at du kan det`, punkt 9 |
| **K8** Revisionsspor uden indblik i andre tenants | 08 | `## Fem krav du sporer hele vejen ned` | Rækken NIS2 art. 21(2)(b): auditlog adskilt fra diagnostisk log, append-only, immutable blob-politik som evidens. Suppl.: 09 `## Problemkataloget: hvad der faktisk er svært i domænet`, rækkerne "Append-only revisionsspor" og "Sletning under legal hold" |
| **K9** Krypteringsnøglen: pris og fejlklasse | 08 | `## Trade-off-øvelsen der skiller arkitekt fra senior udvikler` | Rækken Customer-managed keys med fejlklasse-kolonnen — nøglerotation, tab af nøgle, utilgængelig vault vælter tenanten — og beslutningsreglen "nej, indtil første kunde over X i ARR betaler for det" |
| **K10** Iteration ved præmisskift | 01 | `## Sådan ved du at du kan det` (2. punkt) | "Når præmissen ændres midtvejs, itererer du i stedet for at forsvare. Observerbart på optagelse." Suppl.: 01 `### Øvelse 3: Trade-off-kata på tid`, sidste afsnit om den eksterne der ændrer en præmis efter fire timer |
| **K11** Én side stifteren kan handle på | 11 | `## Oversæt til kroner og risiko` | De fire enheder, forbuddet mod at præsentere én løsning, og formen "Vi har X i dag. Problemet er Y. Spørgsmålet er hvordan vi Z. Mit svar er A, det koster B, alternativet C koster D" |
| **K12** Det arkitektur ikke kan løse | — | **IKKE DÆKKET** | Materialet har SLO'er internt (06 `## Faldgruber`, punkt 4: en SLO uden konsekvens er en graf) og on-call som karrierefælde (12 `## Dag 30-90: overtag én ting der gør ondt på stifteren`). Der mangler: hvordan man omsætter et **kontraktuelt** krav om svartid og vagtdækning til bemandingsomkostning, og hvordan et forbehold formuleres i et tilbud uden at tabe handlen. 08's faldgrube 7 forbyder at påstå compliance man ikke har, men siger ikke hvad man så skriver i stedet |

## Ekstern kalibrering

Din egen score er værdiløs alene, og en kollega i et ni-mandsfirma tæller halvt. Mindst to af disse skal have givet **skriftlig** kritik, før katáen tælles som gennemført. Spørg hver om én ting — ikke om en helhedsvurdering, for den får du en høflig udgave af.

| Hvem | Hvor du finder dem | Det konkrete spørgsmål |
|---|---|---|
| Praktiserende solution architect fra et konsulenthus (Netcompany, twoday, Trifork, Fellowmind, Devoteam) | ANUG- eller GOTO-meetup i Aarhus; bed om 30 minutter efter oplægget, ikke under | "Her er mine 12 kravsspørgsmål. Hvilke to ville du have stillet først, hvilket ville du have droppet, og hvilket mangler helt?" |
| IT-arkitekt hos en eksisterende LeanLinking-kunde | Gennem en kundeonboarding du alligevel sidder med; indramning: "jeg vil gerne vide om det her ville holde hos jer" | "Ville dette revisionsspor-udtræk have været nok hos jeres revisor, og hvad ville han have spurgt om ud over det?" |
| Ekstern IT-revisor (BDO, Beierholm, EY, PwC) | Kold henvendelse på LinkedIn til en der skriver om ISAE 3402 eller leverandørrevision; 30 minutter | "Jeg har designet et revisionsspor til én kunde ud af 34 i et delt system. Hvad ville du afvise, og hvilket bevis ville du kræve for at posterne ikke er efterredigeret?" |
| Mentor med multi-tenant SaaS-erfaring | ADPList, 30 minutter, book to i tilfælde af aflysning | "Angrib min kostmodel, ikke mit diagram. Hvor er tallet forkert, og hvilken post har jeg glemt?" |
| Dansk DPO eller privacyjurist | IAPP-netværk i DK, eller en kundes DPO | "10 års revisionsspor og sletning efter 24 måneders inaktivitet i samme tabel — hvilket af mine to svar ville du kunne stå inde for over for Datatilsynet?" |
| Code review-byttepartneren | Den udvikler i et andet firma du har fast kadence med fra måned 3 | "Læs mine to fravalg. Kan du argumentere mig ned på ét af dem?" |

Notér for hver: hvad de sagde, hvad du ændrede, og hvad du valgte at lade stå — plus hvorfor. Den tredje kolonne er den, en kommende arbejdsgiver spørger ind til.
