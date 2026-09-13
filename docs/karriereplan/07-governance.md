# 07. Governance: at styre uden at kvæle

> Du sidder i et hus på ni mennesker, der opbevarer andre virksomheders bevismateriale: auditrapporter, ISO-certifikater, CSR-erklæringer. Governance er ikke en stabsfunktion hos jer — det er produktet.
> Der er samtidig ingen at spørge om lov og ingen til at stoppe dig: hver regel du indfører, indfører du reelt selv.
> Det gør emnet til dit hurtigste at blive stærk i, og dit letteste at ødelægge noget i.

## Fem ord der lyder ens

Samtaler om governance går i stå, fordi folk taler om fem discipliner uden at sige hvilken. At udpege hvilken du taler om, i den sætning du siger den, løfter dig over de fleste seniorudviklere.

| Betydning | Konkret indhold | Dit? |
|---|---|---|
| Corporate/IT governance | COBIT, bestyrelse, intern revision, tilsyn | Nej — kun som oversættelse |
| Cloud-/platformgovernance | Management groups, Azure Policy, RBAC, PIM, tagging, budgetter | Ja — kernen |
| Engineering governance | Branch policies, environments, approvals, required templates, supply chain | Ja — kan ændres i næste ticket |
| Arkitekturgovernance | ADR'er, principper, fitness functions, tech radar | Ja — kræver nul mandat |
| Data governance | Klassificering, retention, sletning, isolation | Ja — LeanLinkings forretning sat på formel |

## Guardrail eller gatekeeper

En gatekeeper er et menneske, der skal sige ja: omkostningen skalerer med antal beslutninger, ventetiden med kalendere. En guardrail er en automatiseret begrænsning, der gør det forkerte svært og det rigtige til default: omkostningen betales én gang. Jobbet er at konvertere gatekeeping til guardrails.

Den målbare test er forskellen mellem tid-til-compliant-miljø og tid-til-non-compliant-miljø. Er den compliante vej langsommere, træner du folk i at rute uden om — et designproblem, ikke et kulturproblem. Tving dig selv til to sætninger for hver idé: hvordan gør det her den rigtige vej **hurtigere**, og hvad koster det den forkerte vej? Kan du ikke besvare den første, har du designet en skat.

Architecture Review Boards fejler strukturelt: en synkron, batchet kø foran en proces med høj ankomstrate, hvor ventetiden går mod uendelig, når udnyttelsen nærmer sig kapaciteten. Hos jer er det problem irrelevant, og det skal du bruge bevidst: i ni mennesker findes ingen kø, ingen sponsor at opdyrke, ingen magtanalyse og intet board at reformere. Du får mandat ved at spørge stifteren direkte og får svaret samme eftermiddag. Til gengæld stopper ingen dig, hvis du indfører noget dumt.

## Progressiv håndhævelse: manøvren der giver mandat

Foreslå aldrig Deny først. Rækkefølgen er: **audit → mål → vis tal → modify/deployIfNotExists på det mekaniske → deny kun på det lille sæt, der ikke kan forhandles.** Azure Policy har `enforcementMode: DoNotEnforce`, og GitHub rulesets har en evaluate-tilstand præcis til det (rulesets-detaljer uverificeret).

Mønsteret lyder: "jeg kørte det i audit i tre uger; der er 43 afvigelser, 38 af dem i én resource group, her er modify-policyen der retter dem — skal vi håndhæve for nye ressourcer?" Det forvandler en juniors mening til en beslutning, og virker identisk på policy, branch-regler, licenser og teknisk gæld.

Én hård advarsel, og det eneste sted hvor du kan komme i alvorlige problemer i stedet for at fremme dig selv: kør aldrig scanningsværktøjer mod LeanLinkings produktionstenant uden skriftlig aftale. Bed om Reader på ét abonnement, og vis outputtet først. Får du nej, kører du mod dit eget dev-tenant.

## Artefakter du kan producere

Governance-arbejde er næsten altid ejerløst: ingen ejer tagging-strategien, licenspolitikken eller listen over hvilke beslutninger der kræver en ADR. Du behøver ikke mandat til at samle op, hvad ingen holder i.

| Artefakt | Indhold | Tid |
|---|---|---|
| ADR-serie | `docs/adr/`, MADR bare-minimal, `NNNN-kebab-titel.md` | 30-45 min pr. stk. |
| ADR-trigger og `TECH-CHOICES.md` | Hvilke beslutninger kræver en ADR; Default / Tilladt med en ADR / Start ikke nyt med dette | 3 t |
| Licenspolitik, én side | Permissive tilladt, LGPL betinget, AGPL og SSPL afvist for SaaS | 2 t |
| Incident-log | Dato, hvad gik i stykker, hvordan opdaget, tid til udbedring | 10 min/uge |

Aflever i organisationens format: Azure DevOps Wiki publicerer direkte fra en repo-mappe, så markdown i git gratis bliver en læsbar side. Og sig aldrig ordet governance internt — det gør udviklere defensive og ledelse mistænksom. Sig i stedet "det her gør næste sikkerhedsspørgeskema til en time i stedet for tre dage".

## Spikes med fysisk output

Governance er dit **andet** fokusområde: en tredjedel af de 10-15 timer, altså 3-5 timer om ugen i måned 1-6. Fire til fem spikes, ikke elleve.

### G1 — Tag- og region-guardrail som policy-as-code (måned 1-2, ~1 uge dedikeret)

Fire obligatoriske tags (`owner`, `costCenter`, `env`, `dataClassification`), ressourcer kun i westeurope og northeurope, tags arves fra resource group hvor de mangler. Ingen eksisterende ressource må gå i stykker, og Deny håndhæves ikke, før der foreligger tal.

Byg et lille management group-hierarki i et eget abonnement. Fire definitioner: audit på manglende tag, modify der arver tag fra resource group, deny på ikke-tilladte lokationer (slå det indbyggede definitions-ID op i `Azure/azure-policy` frem for at gætte), audit på ressource helt uden tags. Bundl dem i én initiative med parametre, assign med `DoNotEnforce`, deploy femten bevidst non-compliante ressourcer, notér compliance-procenten, kør en remediation task, mål igen. Skift til sidst kun region-policyen til Enforce.

**Output:** repo med `infra/policy/` i Bicep; ADR-0001 "Vi håndhæver fire tags, ikke ni" med afviste alternativer; Mermaid-diagram over hierarkiet med assignment-scopes; `measurements.md` med compliance før og efter, antal remedierede ressourcer og målt varighed på remediation task; retrospektiv. `dataClassification` er valgt med vilje: det binder infrastruktur til dokumentklassifikation og er det eneste af de fire, en kunde spørger til.

### G5 — ADR-serie om lejerisolation i dokumentlageret (måned 3-4, 1 uge, parallelt)

Teknisk let, dømmekraftsmæssigt svær — den rigtige vej rundt for en, der kan kode. Hvordan isolerer man lejere i et lager for leverandørbevismateriale? Fire optioner: delt container med sti-præfiks og ABAC-betingelser, container pr. lejer, storage account pr. lejer, eller storage account pr. lejer-niveau med kundeadministrerede nøgler til enterprise-kunder. Beslutningen skal adressere sletning af en hel lejer, datalokalisering for en tysk kunde, omkostning pr. lejer og Azures grænse for storage accounts pr. abonnement (slå den op, gæt ikke). Én side pr. ADR, maks fem, mindst to registrerer et **fravalg** med navngivne afviste alternativer.

**Output:** `docs/adr/` med index, et C4 container-diagram over den valgte model, og en registrering af den indhentede rådgivning plus hvad den ændrede. Måling: minutter pr. ADR (mål: under 45).

Den hårde konflikt, du skal kunne ræsonnere højt om, og som er et direkte arkitektsignal i jeres branche: immutabelt revisionsbevis versus ret til sletning. En auditrapport må ikke kunne ændres; en navngiven person i den har sletteret. Løsningen er normalt at adskille persondata fra beviset eller at dokumentere et retsgrundlag, der går forud. Kunderne er selv under leverandørkædekrav (NIS2, CSRD, CSDDD — datoer og dansk implementering uverificeret efter 2025's udskydelser; brug kravene som kontekst uden at citere datoer).

### G9 — Fitness functions: principper omsat til tests (måned 5, 1 uge, parallelt)

Konvertér fem principper til checks, der fejler et build: én lagdelingsregel, én afhængighedsregel, én infrastrukturregel, én runtime-regel, én dataregel. Hver check bevises ved, at du **indfører** en overtrædelse og ser den fejle. Lagdeling med NetArchTest eller ArchUnitNET; infrastruktur med PSRule for Azure eller Checkov på Bicep-koden; runtime med en pipeline-assertion på p95-latenstid; data med en test, der fejler hvis et `restricted`-klassificeret feltnavn optræder i en log-payload — domæneægte og indførbar på arbejdet i næste ticket uden at spørge nogen.

**Output:** testprojektet, ADR "Principper vi ikke kan automatisere — og hvad vi gør i stedet", og målingen: hvor mange af de fem du **ikke** kunne automatisere. Det tal er hele fundet. Testen på om et princip er operativt: kan du navngive en beslutning, det ville få dig til at afvise?

### Hvis der er luft (vælg én, måned 6-8)

**G4:** gør det umuligt at deploye til prod uden at udvide en required template, du kontrollerer, som genererer SBOM, kører IaC-scanning og kræver godkendelse fra en gruppe, deployeren ikke er i — hvor den compliante vej måles som hurtigere end den naive, og du skriftligt redegør for dit forsøg på at omgå din egen kontrol. **G11:** ti rigtige kontroller mappet til Azure-konfiguration og eksporterbart bevis; "vi har en politik om det" tæller ikke. Den gør dig hurtigst nyttig for salgsprocessen — den korteste vej til mandat hos jer.

## Modspil udefra

Ingen hos LeanLinking kan fortælle dig, om din isolationsmodel er dum. Governance-fejl er stille: en dårlig regel producerer ingen stacktrace, kun folk der ruter uden om, og det opdager du først om et år.

- **Simuleret advice process på G5.** Send serien til to-tre parter: en dygtig kollega, nogen fra et dansk arkitekturfællesskab, og en sprogmodel instrueret i at spille en skeptisk sikkerhedsansvarlig, der skal godkende før produktion. Registrér rådet — registreringen er artefaktet, ikke enigheden.
- **Kundesikkerhedsspørgeskemaet** er gratis, hård, ekstern feedback. Tilbyd salg eller CTO'en at hjælpe med det næste; kunden fortæller dig præcist, hvor dine svar ikke holder, og ingen slås om opgaven.
- **Publicér mindst én ADR-serie eller kontrol-mapping offentligt** og inviter kritik; skriv den, så en fremmed kan finde fejlen. Læs samtidig tre rigtige beslutningsprocesser, mindst én afvist: `rust-lang/rfcs` og `oxidecomputer/rfd`.

## TOGAF, ITIL, COBIT, ArchiMate

De er ordbøger til at tale med folk, der styrer budgetter — ikke metoder til at bygge gode systemer. I Danmark bruges de i offentlig sektor, bank, pension, energi og hos konsulenthusene der sælger derind; i SaaS-produktvirksomheder på jeres størrelse stort set aldrig (uverificeret mod data). Rammeværkerne er billige at tilføje senere; ingeniørdybden udløber, hvis du ikke bygger den nu.

| Rammeværk | Hvad det reelt er | Dosis | Dom |
|---|---|---|---|
| TOGAF (10. udg., uverificeret) | EA-metode med ADM-cyklus og en stor bunke leverancer; certificeringen er en ordforrådseksamen | 3 t: ADM-faserne som tænkecheckliste, principper med rationale | Spring den over — den træner en leverance-først-vane, produktteams læser som bureaukrati |
| ITIL 4 (skema uverificeret) | Service value system med 34 praksisser | 4-6 t: incident vs. problem vs. change, change enablement | Ingen eksamen. Pointen der vinder et rum: ITIL 4 understøtter forhåndsgodkendte standard changes, så "ITIL kræver et CAB" er forkert på ITIL's egne præmisser |
| COBIT (2019, uverificeret) | Målkaskade, 40 objectives — revisorers sprog | 2 t på hvad en revisor accepterer som bevis | Ren oversættelse: "funktionsadskillelse i deployment" = "dette environment kræver godkendelse fra en gruppe, deployeren ikke er i, her er audit-loggen" |

En eftermiddag hver til to ting mere: at **læse** ArchiMate uden at tegne i det (C4 og Mermaid renderes, hvor I allerede arbejder), og SAFe-ordforrådet — enabler epics, architectural runway, PI planning — som mange danske arkitektopslag reelt beskriver uden at nævne SAFe. Nul certificeringer i alt dette i måned 1-9.

## Certificeringer: to, kirurgisk valgt

Verificeret ved søgning 10. september 2026; efterprøv selv på Microsoft Learn før du booker.

| Eksamen | Status | Timer | Dom |
|---|---|---|---|
| **AZ-305** | Aktiv; engelsk version opdateret 17. april 2026 | 50-70 | **Ankeret.** Governance, identitet, data og kontinuitet som designdisciplin, ikke administration |
| **SC-300** | Aktiv; kursusrepo opdateret august 2026 | 35-45 | **Nummer to.** Entra ID, betinget adgang, PIM, access reviews — den dybe halvdel af cloud governance |
| AZ-500 | **Udfases 31. august 2026**, afløst af SC-500 uden konverteringssti | — | Tag den ikke; vejledninger der anbefaler den er forældede |
| AZ-400 | Aktiv; labs flyttet til `MicrosoftLearning/mslearn-devops` | 40-50 | Senere. Overlapper G4 — mere signalering end læring |

AZ-204 blev pensioneret 31. juli 2026 og afløst af det AI-drejede AI-200, så enhver plan der siger "tag AZ-204" er forældet. AZ-104 er ikke et selvstændigt mål — men *titlen* Solutions Architect Expert kræver angiveligt Azure Administrator Associate ovenpå AZ-305 (uverificeret).

## Ressourcer

| Ressource | Prioritet | Tid | Spring over |
|---|---|---|---|
| Azure Landing Zones techdocs (`aka.ms/alz/techdocs`, citeret fra Enterprise-Scale-repoet) | Kerne | 4 t | Hybridnetværk og ExpressRoute: halvdelen af materialet, nul relevans for SaaS |
| `Azure/bicep-registry-modules` (AVM) og `Azure/Azure-Landing-Zones-Library` | Kerne | 5 t | Contribution-dokumentationen; læs én arketype til bunds, ikke hele biblioteket |
| `Azure/azure-policy`, `Azure/Community-Policy`, EPAC-repoets layout | Støtte | 4 t | EPAC-installationen. Community-definitioner er utestede: læsestof, ikke kopikilde |
| MADR (`adr/madr`, v4.0.0) | Kerne | 1 t | Full-skabelonen: ni sektioner får folk til at lade være |
| AzGovViz (`JulianHayward/Azure-MG-Sub-Governance-Reporting`, v6.7.3) | Kerne | 3 t + 1 t/uge | Intet — men kør den aldrig mod produktionstenanten |
| Cloud Adoption Framework (Govern + Manage) og Well-Architected (Security, Cost, Operational Excellence) | Kerne | 12-14 t | Plan/Ready/Migrate og workload-guider. Læs WAF's trade-off-afsnit |
| *Facilitating Software Architecture* (Harmel-Law) og *Building Evolutionary Architectures* (Ford m.fl.), udgaver uverificeret | Kerne | 7 t | Alt undtagen advice process-, ADR- og fitness function-kapitlerne |
| `npryce/adr-tools`, `log4brains`, Purview-opsætning | Spring over | 0 | Døde værktøjer (sidste commits marts 2020 og december 2024) |

## Faldgruber

- **At forveksle governance med at lære værktøjer.** Azure Policy-syntaks er en eftermiddag. At vide hvilke fire regler der er værd at håndhæve, er årevis. Og foreslår du Deny først, er du "ham med policyerne" i to år.
- **For mange obligatoriske tags.** Fire er meget, otte er nul. Kan du ikke navngive rapporten der **læser** `owner`, skal tagget væk.
- **Governance-gæld.** Hver regel uden ejer og udløbsdato er permanent. En policy med to hundrede exemptions er ikke en policy, men en løgn med revisionsspor.
- **At tro ADR'er er dokumentation.** De er beslutningshistorik skrevet på beslutningstidspunktet og afløst frem for redigeret; værdien ligger i de afviste alternativer.
- **Teknisk gæld målt som debt ratio.** Ingen handler på et abstrakt gældstal. Alle handler på en dato og et beløb: "denne runtime mister support på dato D, og kundernes sikkerhedsspørgeskemaer kræver understøttede runtimes."
- **At tro SBOM-generering er supply chain-sikkerhed.** Uden forespørgselsstien — hvilke releases i produktion indeholder pakke X under version Y — er det en fil, ingen åbner.

## Sådan ved du at du kan det

Kriterier til kompetenceporten i måned 9-10. Ingen kan besvares med "jeg har læst om det".

- Du tegner et management group-hierarki med abonnementsopdeling på under fem minutter uden noter og forsvarer hver grænse — herunder hvorfor der **ikke** assignes på Tenant Root Group.
- Du har et repo med mindst otte ADR'er: tre dokumenterer et fravalg, og mindst én er **afløst** af en senere ADR frem for redigeret.
- Mindst én policy-initiative ligger i version control, er deployet til et rigtigt tenant og har en dokumenteret audit → modify → deny-progression med tal før og efter.
- Mindst ét guardrail er kommet ind i LeanLinkings faktiske pipeline eller repo — branch policy, required template, central pakkelåsning eller en fitness function-test. Ikke foreslået: indført og i brug.
- Du forklarer uden tøven control plane versus data plane: Owner på en storage account giver ikke blob-læseadgang uden en data-rolle.
- Du har bidraget til mindst ét rigtigt kundesikkerhedsspørgeskema og kan navngive de tre spørgsmål, virksomheden havde sværest ved at besvare.
- Nogen har spurgt **dig** om råd eller om lov i stedet for omvendt.
- Hver regel du har indført, også dine egne, har navngiven ejer og udløbsdato — og du kan navngive én, du **fjernede** igen, fordi den ikke betalte sig.
- Du kan forklare en revisor eller kunde, hvordan et krav opfyldes i Azure, og hvordan beviset eksporteres, uden at bruge ordet politik.
- AZ-305 er bestået, eller der er en booket eksamensdato inden for otte uger.

Fejler du tre eller flere i måned 9-10, er kompetencen ikke der endnu, og titlen skal ikke rejses. Det er pointen med at skrive listen nu, hvor svarene endnu er ukendte.
