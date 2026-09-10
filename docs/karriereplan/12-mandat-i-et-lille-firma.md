# 12. Mandat, bredde og overgangen til fuldtid

> I et firma med ni ansatte findes der ingen review board, ingen sponsor og ingen HR-afdeling der husker hvad du fik lovet. Der findes en stifter der har for travlt, tre til fem udviklere der ved at du er den yngste, og en række opgaver ingen har ejet i årevis fordi de er kedelige. Det er hele dit mulighedsrum, og det er større end det lyder. Mandat gives ikke her — det tages, men først efter du har afleveret det kedelige upåklageligt.

## Uge 1: fem ting du kan gøre uden at spørge om lov

Ingen af dem kræver en beslutning fra nogen. Alle fem er i gang inden fredag.

1. **Læs firmaets egen databehandleraftale** på [leanlinking.com/dataprocessing](https://leanlinking.com/dataprocessing/) — hele vejen, inklusive bilaget om underdatabehandlere. 45-60 minutter. De færreste udviklere i mikrofirmaer har læst deres egen DPA. Bagefter er sletning, opbevaringstid og datalokation ikke abstraktioner, men noget firmaet har skrevet under på over for kunder.
2. **Bed om read-only adgang til supporthenvendelser.** Ikke for at besvare dem — for at læse dem. Det er en meget lille bøn som næsten aldrig afvises, og det er den billigste domænekundskab der findes. Kundens sprog er ikke udviklerens sprog, og forskellen mellem de to er halvdelen af det, en arkitekt får betalt for at oversætte.
3. **Start en privat beslutningslog.** Hver ikke-triviel beslutning i dine egne tickets: hvad valgte jeg, hvad var alternativet, hvad ville få mig til at fortryde det. Ti minutter pr. ticket. Kald den ikke ADR i de første måneder — et engelsk akronym på en privat fil er en unødvendig måde at signalere ambition på.
4. **Meld dig ind i IDA eller PROSA nu**, ikke i forhandlingsugen. Kontraktgennemgangen skal ligge klar før du underskriver noget, og medlemskab har karenstid i praksis.
5. **Tilmeld dig næste ANUG- eller GOTO-meetup i Aarhus.** Gratis, fysisk, i din egen by. Mød op for at møde mennesker, ikke for at høre oplægget — oplægget ligger på YouTube, folkene gør ikke.

Og én vane fra dag ét: efter hver samtale med stifteren der ligner en aftale, sender du samme dag seks linjer. "Som jeg forstod det: jeg tager X, du siger ja til Y, vi ser på Z i marts. Ret mig hvis jeg husker forkert." Fire minutter, ingen konfrontation, ingen jura. Om otte måneder er det forskellen mellem en aftale og en erindring. Træn vanen på småting nu — hvis den første opsummeringsmail du nogensinde sender, er den efter lønsamtalen, virker den påfaldende.

## De første 30 dage: beskriv, mål, foreslå intet

Den eneste form for arkitekturarbejde du kan udføre helt uden mandat, er beskrivelse. Ingen afviser en beskrivelse. Og det er beskrivelsen der skaber mandatet til forslaget.

**Absolut regel de første 30 dage: nul strukturelle forslag.** I et hus med tre til fem udviklere har de andre bygget det, du vil ændre. En junior der begynder at lege arkitekt før han er pålidelig, bliver låst ude, ikke inde, og det tager atten måneder at komme tilbage.

Til gengæld måler du. I dine egne tickets, uden at foreslå noget: hvor lang tid tager den langsomste query, hvor mange rækker er der faktisk i den tabel, hvor stor er den største request. At gå rundt med tal i lommen er forskellen mellem at have en mening og at have et argument.

Parallelt kalibrerer du udefra: tre til fem samtaler á 30 minutter på [ADPList](https://adplist.org/find-a-mentor) i måned 1-2. Formålet er ikke kontinuitet — gratis mentorer aflyser. Formålet er at finde ud af hvilke af dine spørgsmål der er dumme, og hvordan folk med femten års erfaring faktisk taler om trade-offs.

## Dag 30-90: overtag én ting der gør ondt på stifteren

I ethvert mikrofirma findes der tre til fem ting ingen har ejet i årevis: deploy-processen, on-call, kunders sikkerhedsspørgeskemaer, databehandleraftalen og underdatabehandlerlisten, en backup-restore der aldrig er testet, onboarding-dokumentation, logging. Bredde i et mikrofirma købes med kedeligt arbejde. Det er den eneste valuta der findes.

Du beder ikke om "arkitekturansvar". Det er abstrakt, og det lyder som en titelambition. Du beder om at eje ét konkret af de her, og du afleverer det synligt bedre end det var.

| Kandidat til overtagelse | Hvad det giver dig | Risiko for uundværlighed | Overdragelsesklausul fra dag ét |
|---|---|---|---|
| Deploy og release | Systemkendskab i bredden, drift, adgang til alt | **Høj** — den klassiske fælde | Navngiven efterfølger + oplæring i md. 4-6 |
| Kunders sikkerhedsspørgeskemaer | Compliance som arkitekturkrav, kundekontakt | Lav | Svarbibliotek i repo, ikke i dit hoved |
| Backup og restore | Måleteknik, risikovurdering, troværdighed hos stifteren | Lav | Runbook der er testet af en anden |
| On-call | Incidenter at eje, hurtigst mulige troværdighed | **Meget høj** — kan æde din ferie | Maks. seks måneder, skrevet ind |
| Lokal onboarding og dev-miljø | Goodwill, tvunget kendskab til alle dependencies | Lav | Automatiseret, altså allerede overdraget |

Formuleringen ved overtagelsen — ikke bagefter: "Jeg tager on-call og deploys i seks måneder, og i måned fire til seks lærer jeg [navn] op, så det ikke hænger på mig alene." Skriv det i mailen samme dag. Hvis stifteren ikke vil acceptere en overdragelsesplan, har du lige lært noget meget vigtigt om de næste tre år, og det var billigt at lære.

**Forretningsargumentet du bruger, når du beder om lov, er NIS2 — ikke CSDDD.** Den danske NIS2-lov trådte i kraft 1. juli 2025 uden overgangsperiode, og Center for Cybersikkerhed påbegyndte aktivt tilsyn i første halvår 2026. Artikel 21 pålægger omfattede virksomheder leverandørkæde-risikostyring, hvilket betyder at kunderne lige nu skubber kontraktuelle sikkerhedskrav, auditadgang og hændelsesrapporteringskrav ned på LeanLinking som leverandør. Det er et levende salgsproblem. CSDDD er derimod kraftigt indsnævret af Omnibus I (Direktiv (EU) 2026/470, i kraft 18. marts 2026): tærskel hævet til 5.000 ansatte og 1,5 mia. EUR, anvendelse udskudt til 26. juli 2029, trickle-down til SMV'er eksplicit begrænset. Går du ind med "CSDDD kommer", bliver du modsagt. Går du ind med "vores kunder bliver ført tilsyn med under NIS2 fra i år, og de sender kravene videre til os — kan vi svare på dem?", rammer du et problem stifteren allerede ligger vågen over.

Deadlines i samme periode: **ekstern sparring booket inden udgangen af måned 2** (sker det ikke, er det planens første og alvorligste afvigelse), **code review-bytte etableret i måned 3** med én udvikler på nogenlunde dit niveau i et andet firma, 45 minutter en fast dag om måneden.

## Tre spikes med fysisk output

Mindst halvdelen af hvert spike skal have et internt aftryk: en side i firmaets repo, en gennemgang på tyve minutter for udviklerne, eller ét tal i en mail til stifteren. Ellers konverterer tolv måneders arbejde til nul mandat.

**1. Systemkortet (15-20 timer over tre uger).** Fysisk output: C4 context- og container-diagram over platformen som den faktisk er; komplet liste over alle integrationspunkter ud af systemet (kunders ERP, mail, filstorage, auth, tredjeparts-datakilder); en tabel med ti rækker "hvad sker der hvis X falder" med estimeret kundepåvirkning; en dataflow-tegning der viser hvor persondata går hen. Uge 1: læs deployment-konfiguration og infrastruktur, ikke kode. Uge 2: tegn, og gå til hver enkelt udvikler med tegningen og ét spørgsmål — "hvad er der galt her", ikke "hvad synes du". Uge 3: ret, læg den i repoet ved siden af koden. Ingen anbefalinger i version 1. Kortet er i sig selv et compliance-artefakt: et dataflow-diagram med underdatabehandlere og datalokationer er første side i ethvert kundesikkerhedsspørgeskema. LeanLinking hoster på Azure med datacentre i Irland og Holland (uverificeret — bekræft internt).

**2. Restore-testen (8-12 timer).** Fysisk output: en dokumenteret, tidsstemplet restore af produktionsdatabasen til et isoleret miljø med **målt** RTO og RPO, en énsides rapport bygget op om "det vi troede" over for "det vi målte", og en runbook en anden kan følge klokken tre om natten. Dette er den ene spike hvor du skal have eksplicit skriftlig tilladelse, med angivelse af at det sker i et isoleret subscription eller en isoleret resource group uden forbindelse til produktion. Definér succeskriterier på forhånd. Præsentér resultatet neutralt, uanset hvor dårligt det er — pointen er at tallet er ægte. RTO og RPO er kontraktuelle punkter i SLA'er og et direkte spørgsmål i NIS2-drevne leverandørvurderinger. I et system der opbevarer certifikater og revisionsspor med lovbestemt opbevaringstid, er datatab ikke en driftsforstyrrelse, men et compliance-brud hos kunden.

**3. Spørgeskema-maskinen (12-15 timer + ca. 2 timer/md.).** Fysisk output: et versioneret svarbibliotek i markdown i firmaets repo med 60-100 standardsvar, hvert koblet til sin kilde — hvor i systemet beviset findes; et gap-register over de spørgsmål I endnu ikke kan svare oprigtigt ja til; en kort proces for hvem der opdaterer hvad. Fremgangsmåde: bed om de sidste tre besvarede spørgeskemaer, konsolidér, og markér hvert svar som *dokumenteret*, *sandt men udokumenteret* eller *ikke sandt*. Den tredje kategori er både din backlog og dit mandat — og grunden til at fundet skal håndteres diskret og skriftligt til stifteren først, ikke i et fællesforum. Dette er det korteste stykke mellem "junior udvikler" og "med til kundemøder" der findes i virksomheden.

**4. Enhedsøkonomi pr. tenant (12-18 timer), hvis du kun kan nå tre, så vælg denne som nummer tre.** Fysisk output: en model der fordeler Azure-forbrug pr. tenant på storage, egress, compute og backup-retention, plus én graf: omkostning pr. tenant mod hvad tenanten betaler. Findes der ikke tags pr. tenant, *er* dét fundet. Estimér i mellemtiden med proxies: antal dokumenter, storage-forbrug, antal integrationskørsler. Præsentér som spørgsmål: "Ved vi hvad det her koster?" Cost-arkitektur er den ene arkitektdisciplin der taler direkte til en ejer, og dokumenttung compliance-storage er præcis det, der løber løbsk: certifikater med lovbestemt opbevaringstid, append-only revisionsspor der per definition aldrig krymper, vedhæftninger uden sletningspolitik.

## Fuldtidsforhandlingen

**Timing: to til tre måneder før du er færdig, ikke efter.** I et 9-mandsfirma budgetterer stifteren i hovedet; er han allerede mentalt landet på "han fortsætter til 40.000", er det langt sværere at flytte. Bed om en afsat halv time, ikke en gangsnak: "Jeg vil gerne have en halv time om hvordan min ansættelse ser ud når jeg er færdig. Kan vi tage den i [måned]?"

**Regn skalaen ud før du åbner munden.** 4,2 mio. kr. i bruttofortjeneste fordelt på syv årsværk er ca. 600.000 kr. pr. årsværk. Personaleomkostninger betales *af* bruttofortjenesten. En fuldtidsudvikler til 45.000 kr./md. koster firmaet ca. 600.000-650.000 kr./år all-in med pension, ATP og feriepenge. Du lægger altså alene beslag på cirka ét helt årsværks bruttofortjeneste, og resten skal dække husleje, Azure, salg, revisor og overskud. Konklusionen er ikke at du skal være beskeden. Konklusionen er at **kontant løn er det dyreste du kan bede om og det sted du har mindst leverage** — og at hele dit reelle forhandlingsrum ligger i det, der koster lidt eller ingen kontanter.

De tre tal du skal kende, og hvorfor de er forskellige:

| Kilde | Tal | Hvad det er værd |
|---|---|---|
| IDA 2026 | Nyuddannet softwareingeniør 43.800 kr./md. (civilingeniør 42.800, datalog-bachelor 41.100), landsplan, **inkl. både egen og arbejdsgivers pensionsbidrag** | Tættest på din faktiske situation. Beregneren kan trække et Midtjylland-tal ud |
| PROSA 2026 (lønsedler jan. 2026, n=2.642) | Op til 2 års erfaring: nedre kvartil 48.361, median 52.977, øvre kvartil 59.015, gennemsnit 52.862 kr. | Loft, ikke gulv. Selvrapporteret, ikke rene nyuddannede, tilfredse medlemmer indberetter oftere |
| LønRadar | Median softwareudviklere i Aarhus ca. 55.000 kr./md. på tværs af alle erfaringsniveauer | Irrelevant som direkte sammenligning. Brugbar til at vise at Aarhus ligger 0-20 % under København (kilderne er indbyrdes inkonsistente) |

Et forsvarligt spænd for en nyuddannet udvikler i et lille Aarhus-firma i 2026 er ca. **42.000-48.000 kr./md. inkl. pension**. Alle tal bør bekræftes på kildesiderne før mødet (uverificeret via direkte hentning i researchen — kilderne var proxy-blokerede).

Den vigtigste enkeltbeslutning i mødet: **ansvarsområde først, løn sidst.** Kommer lønnen først, bliver hele mødet en lønforhandling, og alt andet bliver til "det finder vi ud af hen ad vejen". Åbning: "Jeg vil gerne blive her på fuldtid. Jeg har tænkt over hvad jeg gerne vil have ansvar for, og hvad jeg skal bruge for at kunne bære det. Lad os tage lønnen til sidst."

| # | Post | Kontant pris for firmaet | Formulering |
|---|---|---|---|
| 1 | **Anciennitet** fra oprindelig tiltrædelsesdato som studentermedhjælper | 0 kr. nu, 1-3 mdr. løn værd senere | "Anciennitet regnes fra [dato]." Afvis ny prøvetid ved uafbrudt ansættelse |
| 2 | **Ansvarsområde i skrift**, med ord ikke titel | 0 kr. | "Ansvarlig for drift, deployment og platformsikkerhed, herunder besvarelse af kunders sikkerheds- og databehandlingsspørgsmål" |
| 3 | **Fire timer/uge i arbejdstiden**, samme halve dag, til ikke-sprint-arbejde | Lav | Den mest værdifulde post på listen og den der oftest ikke bliver bedt om. Uden den skal alle spikes ligge i dine private 10-15 timer |
| 4 | **Ekstern sparring**, 15.000-20.000 kr./år, ca. 1 time/md. | Lav | Se formulering nedenfor |
| 5 | **Uddannelsesbudget** 20.000-25.000 kr./år, som du selv disponerer inden for rammen | Middel | Ikke ansøgning pr. gang — så bliver det aldrig brugt. Arbejdsgiverbetalt erhvervsrelevant uddannelse er fradragsberettiget for firmaet og skattefri for dig |
| 6 | **Konference**, én om året, helst lokal | Middel | Lavest prioritet af de betalte poster |
| 7 | **Løn**, i nedre halvdel af spændet, bundet til en genforhandlingsdato | Højest | "Jeg vil gerne starte på [X]. Til gengæld vil jeg gerne have en aftalt samtale den [dato, 6-9 mdr. frem], hvor vi ser på lønnen igen, og hvor kriterierne er [kompetenceportens]" |

Post 4 er den sværeste, fordi den er usædvanlig, og argumentet skal derfor handle om **firmaets risiko**, ikke om din karriere: "Vi har ingen herinde der kan sige nej til mig på et designvalg. Hvis jeg tager fejl om noget strukturelt, opdager vi det først når det er dyrt at rette. En time om måneden hos en der har bygget og driftet det her før, er billigere end én forkert beslutning." Referencepunkt på bordet: danske specialistkonsulenter koster 1.200-2.500 kr./time i 2026, så 15.000-20.000 kr./år er cirka én time om måneden i den lave ende. Sig aldrig "jeg vil gerne have en mentor så jeg kan udvikle mig" — det er sandt, og det er præcis derfor det lyder som et personalegode og bliver skåret først.

**Send én side dagen før mødet.** Syv punkter, et tal ved hvert. Ikke seks sider, og ikke udleveret på mødet — stifteren skal kunne nå at tænke, så mødet ikke bliver hans første forsvarsreaktion.

### Certificeringer som deadline-motor

| Eksamen | Status pr. sept. 2026 | Anbefaling |
|---|---|---|
| AZ-204 / Azure Developer Associate | **Pensioneret 31. juli 2026** | Nævn den aldrig. Siger du "AZ-204" i mødet, afslører du at din research er et år gammel |
| AI-200 (Azure AI Cloud Developer Associate) | Aktiv, erstatter AZ-204 | Spring over. AI-drejet, ikke en generel .NET-udviklereksamen |
| AZ-104 | Aktiv | Reelt forudsætningen for expert-eksamenerne nu |
| [AZ-305](https://learn.microsoft.com/en-us/credentials/certifications/exams/az-305/) Solutions Architect Expert | Aktiv, opdateret 17. april 2026, 165 USD listepris | Primær. Verificér status ved booking — enkelte sekundære kilder påstod fejlagtigt at den var pensioneret |
| AZ-400 DevOps Engineer Expert | Aktiv, opdateret 27. juli 2026 | Sekundær, passer til deploy-/driftsansvaret |

Dansk kronepris for eksamenerne er ikke verificeret.

## Ressourcer

| Ressource | Prioritet | Tidsforbrug | Pris |
|---|---|---|---|
| [Fagforeningens kontraktgennemgang](https://www.prosa.dk/raadgivning/loen-og-forhandling/loenstatistik-2026/) (IDA eller PROSA), før underskrift | Kritisk | 30-45 min. + indmeldelse | Gratis som medlem |
| [PROSA Startløn 2026](https://www.prosa.dk/raad-og-svar/loenstatistik-2026/startloen-2026) | Kritisk | 1 time | Gratis |
| [IDA lønberegner](https://studerende.ida.dk/snart-nyuddannet/loen/loenberegner-for-snart-nyuddannede/) | Kritisk | 30 min. | Gratis |
| [Ase om anciennitet](https://www.ase.dk/faa-svar/ansaettelse/kontrakter-og-vilkaar/anciennitet) | Kritisk | 30 min. | Gratis |
| [NIS2 i dansk lovgivning](https://www.rismasystems.com/da/ressourcer/artikler/nis2-loven-implementering-i-dansk-lovgivning-risma) | Kritisk | 1-2 timer | Gratis |
| [ANUG Aarhus .NET User Group](https://www.meetup.com/anugdk/) | Kritisk | 2-3 timer/md. | 0 kr. |
| [Lederne om uddannelsesklausuler](https://www.lederne.dk/faa-hjaelp-og-svar/ansaettelsesvilkaar/klausuler/uddannelsesklausul) | Høj | 45 min. | Gratis |
| [Ansættelsesbevisloven, Bird & Bird](https://www.twobirds.com/da/insights/2023/denmark/ny-lov-om-ansaettelsesbeviser) | Høj | 40 min. | Gratis |
| [LeanLinkings egen DPA](https://leanlinking.com/dataprocessing/) | Høj | 45-60 min. | Gratis |
| [Omnibus I og CSDDD, Clifford Chance](https://www.cliffordchance.com/insights/resources/blogs/business-and-human-rights-insights/2026/02/omnibus-i-the-european-union-concludes-csddd-and-csrd-reforms.html) | Høj | 1 time | Gratis |
| [GOTO Meetups Aarhus](https://www.meetup.com/goto-meetups-aarhus/) | Høj | 2-3 timer/md. | 0 kr. |
| [ADPList](https://adplist.org/find-a-mentor) | Høj | 3-5 samtaler á 30 min., md. 1-2 | Gratis |
| [MentorCruise](https://mentorcruise.com/filter/softwareengineering/) som fallback | Høj | 1 time/md. | 120-450 USD/md. |
| [Jobindex Tjek din løn](https://www.jobindex.dk/tjek-din-loen/softwareudvikler) | Middel | 15 min. | Gratis |
| [Danske konsulenttakster 2026](https://loenradar.dk/en/guides/freelance-it-hourly-rate-denmark-2026) | Middel | 20 min. | Gratis |
| [Architectural Katas](https://nealford.com/katas/), kun med modpart | Middel | 2-3 timer pr. kata | Gratis |
| [Dansk IT: It-arkitektur i praksis](https://dit.dk/Netvaerksgrupper/It-arkitektur-praksis) | Middel | 4 dage/år | 10.495 kr. ekskl. moms |
| [IDAs fagtekniske netværk](https://ida.dk/viden-og-netvaerk/ida-netvaerksgrupper/it), maks. to | Middel | Efter behov | Gratis for medlemmer |

Skal du vælge mellem konference og fast ekstern sparring, er det sparring uden tøven. Retten til ti dages selvvalgt uddannelse er overenskomstbetinget og gælder efter al sandsynlighed ikke her — bruger du det argument i mødet, afslører du at du ikke ved hvordan din egen arbejdsplads fungerer.

## Faldgruber

- **At foreslå arkitektur før du har afleveret.** Nul strukturelle forslag de første tre måneder på fuldtid. Kun beskrivelser og målinger.
- **At bruge ordet "arkitektur" internt.** Over for de andre udviklere lyder det som en titelambition og dermed en trussel; over for stifteren er det abstrakt og dermed uinteressant. Tal om nedetid, kundespørgsmål I ikke kan svare på, hvad det koster, og hvor lang tid det tager.
- **Den nye kontrakt der nulstiller ancienniteten.** Den dyreste tekniske fejl i præcis din situation, og den opdages først flere år senere. Anciennitet beregnes uafhængigt af arbejdstid — 20 timer om ugen giver samme anciennitet som 37 — og følger som udgangspunkt med ved overgang uden afbrydelse i samme virksomhed. Men få det skrevet eksplicit ind.
- **At sige ja til en uddannelsesklausul uden at læse den.** 30.000 kr. med 24 måneders binding for en Azure-certificering er ude af proportion. Dit modtilbud: maks. 12 måneders binding, kun ved egen opsigelse, kun for enkeltbeløb over 15.000 kr.
- **Uundværlighedsfælden.** Du bliver den eneste der forstår deployment, alle deploys venter på dig, det bliver for dyrt at sætte dig på noget nyt, du kan reelt ikke holde ferie. Ser ud som succes i seks måneder og som en blindgyde efter atten. Modgiften er strukturel og skal på plads *før* overtagelsen.
- **At bede om titlen.** En Solution Architect-titel i et 9-mandsfirma diskonteres kraftigt eksternt og er direkte skadelig internt. Bed om ansvarsområde. "Ansvarlig for drift, deployment og platformsikkerhed" er sandt, kan verificeres af en fremtidig arbejdsgiver og siger mere i et interview om tre år.
- **At forhandle mod et tal firmaet ikke kan bære.** "PROSA siger 52.862" i et firma med ca. 600.000 kr. bruttofortjeneste pr. årsværk giver sjældent et nej — det giver et ja med indestående vrede, og i et 9-mandsfirma koster indestående vrede mere end de 4.000 kr. du vandt.
- **At tro at "vi tager en snak om det senere" er et ja.** Accepter maksimalt én post på "det ser vi på senere", og skriv datoen ned.
- **At tage ISO 27001-certificering på dig som mål.** En fuld certificering for et 9-mandsfirma er et projekt til flere hundrede tusinde kroner og en ejerbeslutning om markedsposition. Foreslå aldrig certificeringen. Foreslå forarbejdet: svarbiblioteket, adgangsstyring, logging, restore-test.
- **At antyde at du overvejer andre muligheder, medmindre du faktisk gør.** Relationen er personlig, og hukommelsen er lang.

## Læringsloft-checkpoint, måned 6

Loftet rammes ikke af mangel på opgaver. Det rammes af mangel på modstand. Du kan have travlt i fem år og lære mindre og mindre, uden at det nogensinde føles galt. Signalet er ikke kedsomhed — kedsomhed er let at opdage. Signalet er at du holder op med at blive *rettet*, og at det føles som at have ret.

Sæt en time af i måned 6 og besvar seks spørgsmål skriftligt:

| # | Signal | Rødt hvis |
|---|---|---|
| 1 | Hvor mange gange i de sidste otte uger har nogen fået dig til at **ændre retning** på et design du allerede havde besluttet? Ikke en fundet bug — en retningsændring | Under 2 |
| 2 | Af de sidste ti opgaver: hvor mange krævede at du lærte noget du ikke kunne i forvejen? | Under 3 |
| 3 | Har du inden for seks måneder rørt et reelt skalaproblem — en tabel over 10 mio. rækker, en kø der stod stille, en query der måtte omskrives på grund af volumen? | Nej |
| 4 | Hvad var den dyreste konsekvens af en fejl du selv har lavet? | "Vi rettede det inden nogen opdagede det" |
| 5 | Kan du forklare et designvalg til en person uden for firmaet på ti minutter, så vedkommende stiller et spørgsmål du ikke selv havde tænkt på? | Du har ikke prøvet |
| 6 | Hvor stor en andel af arbejdstiden gik til at **holde** ting kørende mod at **ændre** ting? | Over 60 % drift |

**Handlingsregel.** Dette er ikke et "skal jeg sige op"-checkpoint. Det er et "hvad mangler jeg, og kan jeg skaffe det her".

- **0-1 røde:** fortsæt uændret.
- **2-3 røde:** manglen er specifik og skal navngives og skaffes udefra med det samme. Er signal 1 rødt, skal frekvensen af ekstern sparring op nu, og du skal begynde at skrive offentligt. Er signal 3 rødt, findes skalaeksponering ikke internt og skal hentes via open source med rigtig trafik eller syntetiske datasæt i millionklassen på dine egne spikes. Er signal 6 rødt, aktiveres overdragelsesplanen fra kontrakten denne måned, ikke næste kvartal.
- **4 eller flere røde:** firmaet kan ikke levere din plan, og det er ikke firmaets skyld — de har aldrig lovet det. Spørgsmålet er ikke "siger jeg op i dag", men "hvad er den ene ting jeg kan flytte internt, og hvis den ikke er flyttet ved måned 10, hvad er så min næste arbejdsplads". Beslutning med 12-24 måneders horisont.

Baggrund for alle seks: **bredden** i et 9-mandsfirma mættes realistisk efter ca. 18-30 måneder for en der målrettet går efter den. **Dybden** kan fortsætte længere, fordi dokumenttung multi-tenant compliance-storage indeholder ægte tekniske problemer. Den **organisatoriske** kompetence — at få fem teams til at trække samme vej — kan du ikke få dér, hverken nu eller om tre år. Det bliver dit svageste punkt i et eksternt interview, og det kan kun hentes ved senere at arbejde et større sted eller ved at lede noget tværorganisatorisk udenfor: open source-maintainer, arrangør i et fagligt fællesskab. Det er ikke et argument mod at blive. Det er et argument for at vide præcis hvad du bytter væk.

## Sådan ved du at du kan det

Observerbare kriterier. Ingen af dem kræver en vurdering fra nogen.

- **Mandat:** over 30 % af dine tickets er formuleret af dig selv ved måned 6, over 50 % ved måned 12. Måned 0 er 0 %. Kan ikke snydes, kræver ingen samtale.
- **Bredde:** du har rørt mindst 5 af 7 systemområder i produktion ved måned 6, alle 7 ved måned 12 — database, deployment, integrationer, auth, storage, support, kundemøde. Under 4 ved måned 6 betyder at du stadig er i ticket-sporet, uanset hvad kontrakten siger.
- **Synlighed:** nogen anden i firmaet har spurgt dig hvordan noget hænger sammen, mindst to gange på en måned, senest fra måned 6. Stadig nul i måned 6 betyder at du har bygget portefølje uden at bygge position.
- **Kundeeksponering:** mindst én kunde- eller supportsamtale om måneden fra måned 2. Nul i tre måneder i træk betyder at du er blevet i maskinrummet.
- **Driftsansvar:** tre hændelser ejet fra alarm til færdig postmortem med gennemførte handlinger, inden måned 9. En postmortem hvis punkter aldrig blev udført, tæller ikke.
- **Forhandling, fem binære spørgsmål dagen efter mødet:** Står anciennitet fra oprindelig tiltrædelsesdato i kontrakten? Står ansvarsområdet formuleret med ord du ikke selv skal forklare? Står der kronebeløb for uddannelse, certificering, konference og ekstern sparring, med angivelse af hvem der disponerer? Er der en dato for genforhandling? Er en eventuel uddannelsesklausul under 12 måneder og kun udløst ved egen opsigelse? Er svaret nej på nogen af de første fire, har forhandlingen ikke fundet sted — uanset hvor god stemningen var.
- **Timebudget:** faktisk målte timer på spike-arbejde mod loftet på 10-15 timer/uge. To uger over 15 i træk er ikke flid, det er en plan der ikke går op, og det er planen der skæres. Får du de fire ugentlige timer i arbejdstiden igennem, falder den private andel tilsvarende — den lægges ikke oveni.
- **Ikke fanget:** du har givet mindst to områder væk til en navngiven kollega med runbook og en periode hvor kollegaen kører det, og du har været væk en uge uden at nogen mærkede det. Det er det eneste binære bevis på at du ikke er faldet i uundværlighedsfælden.
