# 05. Frontend-arkitektur set fra arkitektstolen

> Du skal kunne stille frontend til regnskab, ikke skrive den. Kravet er, at du på en dag kan åbne et React-repo du aldrig har set og pege på hvor det knækker om 18 måneder — og at du kan forsvare kontrakten mod .NET-backenden når nogen vil bryde den.
> Frontend er samtidig emnet hvor du hurtigst kan spilde et år: der er altid mere at lære, og det føles som fremskridt hele vejen.
> Derfor har frontend et hårdt loft på 15 procent af din øvetid, Simon. Loftet er en arkitekturbeslutning, ikke en nedprioritering.

## Timeloftet, regnet igennem

12 måneder à 10-15 timer giver 550-600 timer. Femten procent er 60-90, og det går kun op hvis du beslutter hvad der ikke bliver til noget.

| Post | Timer |
|---|---|
| Kernelæsning, filtrerede kilder | 12 |
| F1 — API-kontrakt håndhævet i CI | 22 |
| F2 — BFF mod Entra ID, målt mod et angreb | 22 |
| F3 — opsætning af deployet frontend | 10 |
| F3 løbende drift, 1,5 t/md i 10 md | 15 |
| Repo-audit, 1 t × 6 | 6 |
| **I alt** | **87** |

87 af de 90 timer er dermed bundet: **performance-budget, ACR-arbejde og distribueret tracing kan ikke betales herfra.** De hører hjemme i performance-, compliance- og observability-sporet. Skrider F1 eller F2, er driften på F3 den eneste post du må skære i; alt andet fjerner et artefakt. Det er den allokering en arkitekt laver: ikke hvad der er værdifuldt, men hvad der er værdifuldt nok til at fortrænge noget andet.

## Frontend rådner af manglende grænser, ikke af dårlig kode

Alle fem er organisatoriske problemer med teknisk symptom. Derfor er de arkitektens.

| Rådnemekanisme | Symptom udefra | Håndhæves ét sted |
|---|---|---|
| Server-state i en client-state-container | Manuelle loading/error-flag, stale-data-bugs, en "Opdater"-knap | Et query-cache-lag |
| Komponentvækst uden lag eller ejerskab | Komponenter med 25 props; største fil 10x medianen | Lagdeling og mappeejerskab |
| Ingen design-system-governance | Mikrobeslutninger pr. ticket der aldrig konvergerer | Komponentlaget |
| Intet bundle-budget | Størrelsen vokser monotont; ingens ticket hedder "gør den mindre" | CI-gate der fejler builden |
| Ingen versionsdisciplin i drift | Klienter cacher sig fast; hvid skærm efter deploy | Cache-headers og versionsstempel |

En refresh-knap i et B2B-UI er ikke en feature, men en indrømmelse af at cachen er brudt. Diagnosespørgsmålet er: **hvor mange kilder til sandhed har dette datum?** Mere end én er råd. Svaret i 2026 er kedeligt: server-state i et query-cache-lag (TanStack Query 5.102.8, eller RTK Query hvis Redux allerede er der), client-state i noget lille (Zustand 5.0.15 eller `useState`).

To versionsfakta der er argumenter og ikke trivia: React 19.3.0 er nyeste stabile, og der findes ingen React 20 — næsten to år uden major, så framework-panik er ikke længere en reel arkitekturrisiko. React Router kørte derimod v6 → v7 → v8 på kort tid. En router med årlig major **er** en migrationsskat, og at prissætte den er arkitektarbejde.

## De tre nej'er du skal skrive ned

Et nej uden betingelse gør dig til bremseklods. Et nej med betingelsen gør dig til rådgiver.

| Mønster | Hvorfor nej her | Betingelsen der vender svaret |
|---|---|---|
| RSC / Next.js App Router | Bag login er SEO-effekten nul. Next.js betyder en Node-runtime ved siden af .NET: et andet deployment-target, en anden sikkerhedsflade, en anden on-call-kompetence i et hus med syv årsværk | En offentlig, indholdstung del bliver forretningskritisk, og nogen kan tage vagten for Node |
| Micro-frontends | Løser ét problem: at selvstændige teams ikke kan deploye uafhængigt. Under 4-5 teams overstiger prisen gevinsten — versionsdrift på delte afhængigheder, delt auth, ejerskab over routing | Målt PR-kø-tid viser at 5+ teams blokerer hinanden. Undtagelse: strangler-fig-migration |
| Global store til server-data | Flere kilder til sandhed pr. datum; stale-bugs bliver et vedvarende supportmønster | Data der reelt er client-state: kladder, wizard-tilstand |

Teknologien bag micro-frontends er fin og vedligeholdt (`@module-federation/enhanced` 2.9.0); beslutningen er det sjældent.

## Kontrakten mellem .NET og React

Den mest undervurderede grænse i stakken og den eneste frontend-kompetence der overføres 1:1 til distribueret systemarkitektur. Håndskrevne TypeScript-interfaces der spejler C#-DTO'er er gæld der ikke fremgår af nogen metric før den brækker i produktion.

.NET 10 genererer OpenAPI 3.1 native (`Microsoft.AspNetCore.OpenApi` 10.0.12). TS-klienten genereres i CI: `NSwag.MSBuild` 14.7.1 hvis backend skal eje generatoren, hvilket er den rigtige ejerskabsplacering i et .NET-tungt hus, eller `@hey-api/openapi-ts`, som stadig er pre-1.0 — nævn den leverandørrisiko selv når du anbefaler værktøjet.

Forbeholdet der adskiller dig fra en der har læst et blogindlæg: **generering løser kun syntaktisk kompatibilitet.** Et felt der beholder sin type men skifter betydning, eller en ny enum-værdi klienten ikke håndterer, er usynligt for ethvert diff-værktøj.

Og sig ikke at Swashbuckle er dødt. Det er fjernet fra webapi-templaten i .NET 9, men biblioteket lever og understøtter .NET 10 og OpenAPI 3.1.

## Auth: tokens ud af browseren

RFC 10017 rangerer mønstrene normativt: **BFF** (tokens kun server-side, browseren får en HttpOnly-cookie) > **token-mediating backend** > **browser-based OAuth client**. Autoriteten gør forskellen på "jeg synes" og "standarden rangerer sådan, vi valgte nummer to, prisen er X, vi tager det op igen når Y". At argumentere gennem en ekstern autoritet frem for gennem anciennitet du ikke har, er den mest asymmetrisk værdifulde færdighed her.

En BFF løser tre ting og kun tre: browseren ser aldrig et access token; N kald bliver til ét; frontend får en datamodel formet efter skærmen. Gør ingen af dem ondt, er en BFF bare ekstra drift. Reglen i ADR'en: **den må aggregere, transformere og autentificere. Den må ikke beslutte.**

- **Autorisation i frontend er aldrig sikkerhed, det er UX.** Duplikér ikke reglerne to steder: lad serveren returnere de tilladte handlinger sammen med ressourcen, så UI'et renderer ud fra data.
- **Tenant-valg er den mest sandsynlige reelle sårbarhed.** Kommer tenant-id fra et URL-segment eller en header klienten styrer, har du horizontal privilege escalation. Hvor en leverandør betjener flere købere, er "leverandør A kunne se leverandør B's auditsvar" ikke en bug, men en sag der koster kunder.

## Performance: dine egne tal, ikke Googles

Core Web Vitals (LCP under 2,5 s, INP under 200 ms, CLS under 0,1 ved 75.-percentilen) måles i CrUX, som kun indeholder offentligt tilgængelige sider. En app bag login er ikke i CrUX, har ingen SEO-effekt, og LCP betyder næsten intet der. Lånte metrikker er det modsatte af arkitektur.

INP-*konceptet* betyder til gengæld alt. Udled budgetterne fra brugerkendsgerninger: tid pr. tastetryk i en leverandørtabel med 5.000 rækker, tid til et auditskema med 200 felter er interaktivt på 4x throttlet CPU. Tilføj den metrik næsten ingen underviser i: **hukommelsesvækst over en 8-timers session uden reload.** En læk en forbrugerside aldrig opdager, dræber en app der aldrig genindlæses.

Koblingen der får en performance-ticket prioriteret uden mandat: eksterne leverandørbrugere er utrænede og sidder på hvad som helst, så performance konverterer direkte til afbrudt onboarding. Tal om leverandører der ikke bliver færdige, ikke om Lighthouse-scorer.

## Tilgængelighed er en salgsblokering før den er en lovblokering

Trelagsmodellen du skal kunne tegne: **EAA** (direktivet, håndhæveligt siden 28. juni 2025, transponeret i alle 27 lande) → **EN 301 549** (harmoniseret standard, v4.1.1 fra ETSI 2. sept 2026) → **WCAG 2.2 AA**. Danmarks implementeringslov og citeringen i EU-Tidende er ikke bekræftet (uverificeret) — nævn ingen dansk lovtitel du ikke har slået op.

En B2B-leverandørportal er sjældent direkte omfattet af EAA. Men offentlige kunder **skal** indkøbe efter EN 301 549, og store private kunder beder om en ACR uanset jura. Argumentér indkøb og tabt omsætning, ikke paragraffer.

Den højeste løftestang for et hus af denne størrelse: **ejer vi tilgængelighedslaget eller lejer vi det?** Prissæt i vedligeholdelsestimer over tre år, ikke implementeringstimer. Arkitekter regner i år, udviklere i sprints.

| Option | Hvad du påtager dig | Realistisk for syv årsværk |
|---|---|---|
| Egne UI-primitiver | WCAG 2.2 AA implementeret og vedligeholdt selv, uden specialist, for evigt | Nej |
| Headless primitives (fx Radix, React Aria) | Eje styling og komposition, leje tilgængelighedslaget | Ja, mest sandsynligt rigtige |
| Fuldt system (fx Fluent UI, MUI) | Leje begge dele, tage leverandørens designretning | Ja, hvis designfrihed ikke er et produktargument |

## Ressourcer

| Ressource | Prioritet | Tid | Springes over |
|---|---|---|---|
| RFC 10017, OAuth 2.0 for Browser-Based Applications — https://www.rfc-editor.org/info/rfc10017/ | Kerne | 2-3 t | Appendiks og protokolflows; citér ingen sektionsnumre du ikke har set |
| Backends for Frontends — https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends | Kerne | 45 min | Resten af Azure Architecture Center |
| OpenAPI i ASP.NET Core — https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/overview | Kerne | 3-4 t | Native AOT, transformers |
| TanStack Query, caching-modellen — https://tanstack.com/query/latest | Kerne | 2-3 t | Hele API-referencen |
| Fowler/Jackson: Micro Frontends — https://martinfowler.com/articles/micro-frontends.html | Kerne | 1,5 t inkl. nej-ADR | Alt andet på emnet |
| Nygard-ADR og skabeloner — https://adr.github.io/ | Kerne | 1 t | ADR-værktøjer; markdown i repoet er nok |
| WCAG 2.2 Quick Reference, filtreret til AA — https://www.w3.org/WAI/WCAG22/quickref/ | Kerne | 2 t, så opslag | Level AAA |
| `size-limit` — https://github.com/ai/size-limit | Kerne | 2 t | Konkurrerende bundle-værktøjer |
| NSwag — https://github.com/RicoSuter/NSwag | Kerne | I F1 | Kiota, openapi-generator |
| Deque om EN 301 549 — https://www.deque.com/accessibility-compliance/en-301-549/ | Støtte | 1 t | Selve normteksten |
| Lighthouse CI — https://github.com/GoogleChrome/lighthouse-ci | Senere | 1-2 t | Seneste release juni 2025, stadig 0.x: byg ikke governance ovenpå |

Spring over uden undtagelse: Mezzaliras micro-frontend-bog, RSC/Next.js som dybdespor, og enhver tilgængeligheds- eller "frontend architecture"-certificering — ingen af dem har troværdighed hos folk der ansætter arkitekter, og dine certificeringsslots hører til andre emner. Enkelte URL'er kunne ikke hentes ved research (uverificeret).

## Spikes med fysisk output

**F1 — API-kontrakten håndhævet i CI (obligatorisk, 22 t).** Byg en .NET 10 minimal-API med 3-4 endpoints for et forsimplet certifikatflow: opret leverandør, upload certifikat med udløbsdato, hent leverandørliste med status. Generér OpenAPI 3.1 som build-artefakt og TS-klienten i CI, og byg en Azure DevOps-gate der **fejler builden** ved et breaking change mod main: fjernet felt, ændret type, strammet nullability, fjernet enum-værdi. Gaten skal kunne overrules med en ADR-reference i commit-beskeden, for governance uden dokumenteret nødudgang bliver omgået i det skjulte. Frontend og backend må ikke tvinges til at deploye sammen, og du må ikke håndskrive én TS-type der spejler en C#-DTO.
*Output:* ADR med "hvad vi giver afkald på"; C4 container-diagram og et sekvensdiagram over deploy-rækkefølge; **måling:** plant 10 ændringer, 6 breaking og 4 ikke, og tæl korrekt klassificering samt falske positiver og negativer; retrospektiv med navngivne brud gaten ikke kan fange. Ram de tre klassiske fælder med vilje: enums serialiseret som int, nullable reference types der får skemaet til at lyve om `required`, og `DateTime` vs. `DateTimeOffset` — et certifikats udløbsdato er en juridisk kendsgerning.

**F2 — Tokens ud af browseren, målt mod et angreb (obligatorisk, 22 t).** Byg begge varianter; sammenligningsgrundlaget er pointen. A: React SPA med MSAL i browseren. B: samme SPA bag en .NET BFF med authorization code flow og PKCE mod Entra ID, tokens server-side, kun en HttpOnly + Secure + SameSite-cookie ud. Krav: CSRF-forsvar i B, silent renew der ikke smider brugeren ud midt i en 20-minutters auditformular, og defineret opførsel når refresh token udløber. Byg gør-det-selv-varianten med YARP, cookie-auth og Microsoft.Identity.Web; så kan du bagefter argumentere for hvorfor man alligevel bør købe. `Duende.BFF` findes, men licensvilkårene er ikke verificeret (uverificeret).
*Output:* ADR med RFC 10017 som normativ reference og et prisafsnit (ekstra netværkshop, sessionsstate ved udskalering, endnu en ting på vagtplanen); sekvensdiagrammer for login, silent renew **og** logout, for det er dér fejlene bor; **måling:** injicér samme simulerede XSS-payload i begge varianter og dokumentér at A lykkes og B fejler. Tag Entra ID group claims med: mange grupper sprænger token-størrelsen mod header-grænser.

**F3 — Den deployede frontend der ikke kan rulles tilbage (driftskandidat, 10 t + 1,5 t/md).** Deploy F1 og F2 til Azure og driv det året ud. Krav: ingen hvid skærm for en bruger der har appen åben under deploy (håndtér chunk-load-fejl fra assets der ikke længere findes); backend skal kunne rulles én version tilbage uden at en indlæst ældre frontend brækker; immutable hashede assets og ucachet `index.html`, hvor du kan forklare hver header; synligt versionsstempel, så supporten kan starte med "hvilken build kører du".
*Output:* ADR om cache-, versionerings- og rollback-strategi; deployment-diagram med cache-lag og TTL'er; **måling:** 5 deploys med en browser stående åben, tæl hvide skærme før afbødning, implementér, tæl igen; hændelseslog over 3+ måneder. En deployet SPA er det sværeste at rulle tilbage i stakken, fordi klienten cacher og du ikke bestemmer hvornår brugeren genindlæser.

**Månedlig øvelse — 60-minutters repo-audit (6 t i alt).** Ét ukendt open source React-repo, fem arkitekturrisici med kodereference, skrevet **før** du åbner repoets issues. Sammenlign så med issues og commit-historik: fik du ret.

## På jobbet, uden at bede om mandat

Fire ting du må gøre uden tilladelse, og som producerer data i stedet for meninger: **skyggeaudit** af kodebasen (kortlæg hvor server-state ligger — i en store, i et query-lag, eller begge dele, og begge dele *er* diagnosen); **kategorisér 12 måneders frontend-bugs** i kontraktbrud, state, permissions, performance og cache; **kortlæg hvilke skærme leverandører ser versus købere**, for behandles de to ens, har du fundet et reelt arkitekturproblem; og skriv **to linjer arkitektur plus bundle-tallet i hver PR**. Efter 20 tickets har du en kurve, og en kurve er et argument. Skal du spørge om lov, så bed om et eksperiment med slutdato, ikke om mandat.

## Faldgruber

1. **At blive frontend-specialist i stedet for arkitekt.** Den farligste, fordi den føles som fremskridt hele vejen.
2. **At forveksle nye biblioteker med arkitektur.** Framework-jagt er undgåelsesadfærd forklædt som læring.
3. **At bygge et design system som spike.** Design systems fejler organisatorisk, og du har ingen organisation at fejle i. Kompetencen her er beslutning, ikke byggeri.
4. **At bruge to måneder på RSC** i stedet for to timer på at afvise det, eller at nævne micro-frontends for at lyde avanceret.
5. **At citere Core Web Vitals for en app bag login.**
6. **At tro at frontend-permission-checks er sikkerhed.** Håndhæver backend ikke det samme, findes kontrollen ikke.
7. **ADR'er uden tal.** En ADR uden måling er en mening med overskrift, gennemskuet på ti sekunder.
8. **At lade en spike vokse til et produkt.** Når spørgsmålet er besvaret og målt, stopper spiken — også når den er "næsten færdig".
9. **At vente på mandat.** Mandat uddeles ikke; det bekræftes bagudrettet til folk der allerede har lavet arbejdet.
10. **At påstå ting der var sande for to år siden.** Den der ikke tjekker før han udtaler sig, er farligere end den der intet ved.

## Sådan ved du at du kan det

Kompetenceporten i måned 9-10 kræver mindst 3 af de 4 første punkter.

- [ ] **Repo-testen bestået:** i et ukendt React-repo producerer du på 60 minutter fem arkitekturrisici med kodereference, og en erfaren tredjepart er enig i mindst tre.
- [ ] **Fire ADR'er om frontend-grænser eksisterer,** hver med (a) ét tal du selv har målt, (b) et "hvad vi giver afkald på"-afsnit, (c) en ekstern reference. Mangler ét af tre, tæller ADR'en ikke.
- [ ] **En pipeline du har bygget fejler en build,** og en anden end dig har måttet forholde sig til det. En gate ingen andre har mødt, er en demo.
- [ ] **En frontend du har deployet har kørt i 3+ måneder,** med mindst 2 håndterede cache- eller kompatibilitetshændelser og et retrospektiv der navngiver fejlmønsteret.
- [ ] Du kan **tegne kontrakten mellem frontend og backend uden noter**, inklusive hvor et breaking change opdages — og er svaret "det gør det ikke", siger du det uden at pynte.
- [ ] Du kan **gengive RFC 10017's mønsterrangering fra hukommelsen**, sige hvilket mønster I bruger, og hvad det koster.
- [ ] Du har **skriftligt afvist mindst ét populært mønster** med en organisatorisk begrundelse, og navngivet betingelsen der ville vende svaret til ja.
- [ ] Du kan **svare på et tilgængelighedsspørgsmål fra et indkøbsspørgeskema uden at slå op**, og du har **et performance-budgettal du selv har udledt** med brugerkendsgerningen bag det.
- [ ] **En kollega har spurgt dig om en frontend-arkitekturbeslutning uden at du bad om det.** Det eneste ægte mandatsignal. Alt andet er støj.

Falder du under tre ud af fire, fejler planen ikke. Så siger du højt: frontend-arkitektur er mit svageste område, og her er hvad jeg har gjort ved det. Det er et respektabelt svar. At påstå en styrke du ikke har, er ikke.
