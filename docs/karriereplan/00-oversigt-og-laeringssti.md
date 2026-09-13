# 00. Oversigt og læringssti

> Tolv moduler, syv cases, 490-600 timer, ét mål: en kompetence med observerbare kendetegn, ikke et visitkort. Planen er bygget til én person i én situation — en softwareingeniør i et 9-mandsfirma der opbevarer andre virksomheders bevismateriale, uden arkitektstige, uden review board, og med 10-15 timer om ugen ved siden af et fuldtidsjob. Alt i planen er afledt af den situation. Intet i planen er generisk karriereudviklingsrådgivning.

## Planens formål og filosofi

Planen bygger én tese: i et mikrofirma uden titel, uden ladder og uden ekstern bedømmer er den eneste gangbare vej til Solution Architect at producere artefakter med målte tal, som en fremmed kan verificere — og at gøre det konsistent nok til, at andre begynder at behandle dig som arkitekt, før nogen har givet dig titlen. Internt bygger du evidens: scope, driftsansvar, domæneviden, ting der kan bevises for en fremmed. Titlen indløses et andet sted, senere. At blande de to sammen er den mest sandsynlige enkeltfejl i planen. Hvert modul leverer derfor fysiske artefakter med datoer og tal — aldrig læsning alene, aldrig fornemmelser, aldrig "jeg føler mig klar". Kompetenceportene er binære og kræver enten andres adfærd eller reproduserbare målinger som bevis.

## Afhængighedskort

Modulerne er ikke sekventielle. De fleste kører parallelt, men med hårde rækkefølgekrav på de steder hvor et modul forudsætter artefakter eller tal fra et andet.

```
                    ┌─────────────────┐
                    │  01 Rollen       │  ← Læses i uge 1, definerer målet
                    │  (ramme)         │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  02 Teknisk     │  ← FUNDAMENT. Måleapparatet FØRST.
                    │  fundament      │     Alt andet bygger på dette.
                    └──┬──┬──┬──┬────┘
                       │  │  │  │
          ┌────────────┘  │  │  └──────────────────┐
          │               │  │                     │
  ┌───────▼───────┐ ┌─────▼──▼──────┐    ┌────────▼────────┐
  │ 03 Azure-     │ │ 04 System-    │    │ 06 Observa-     │
  │ arkitektur    │ │ design og     │    │ bility          │
  │               │ │ integration   │    │                 │
  └───┬───┬───────┘ └───────┬───────┘    └────────┬────────┘
      │   │                 │                     │
      │   │    ┌────────────┘                     │
      │   │    │                                  │
  ┌───▼───▼────▼──┐                               │
  │ 07 Governance │◄──────────────────────────────┘
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │ 08 Compliance │
  │ og risiko     │
  └───────────────┘

  ┌───────────────┐
  │ 05 Frontend-  │◄── 02 (kontrakten mod backend)
  │ arkitektur    │    Hårdt loft: 15% af øvetiden
  └───────────────┘

  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
  │ 09 Domæne-    │  │ 11 Kommuni-   │  │ 10 Produkt og │
  │ ekspertise    │  │ kation og     │  │ leverance     │
  │ SRM           │  │ indflydelse   │  │               │
  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
          │                  │                  │
          └──────────┬───────┘──────────────────┘
                     │
            ┌────────▼────────┐
            │  12 Mandat i et │  ← CAPSTONE. Samler alt.
            │  lille firma    │     Fuldtidsforhandling.
            └─────────────────┘
```

**Hårde rækkefølgekrav:**

| Krav | Begrundelse |
|---|---|
| 02 før alt andet | Uden måleapparat er ethvert argument en mening. En junior med meninger taber altid |
| 02 før 03 | Azure-kostmodellen kræver egne tal, ikke blogcitater |
| 02 før 04 | Idempotens og leveringssemantik kræver at du kan måle prisen på dit idempotenslag |
| 02 før 06 | Observability er måleapparatet forfremmet, ikke et separat emne |
| 03 og 04 før 07 | Governance-policies kræver at du ved hvad du håndhæver |
| 07 før 08 | Compliance-by-design bygger på guardrails, ikke gatekeeping |
| 09, 10, 11 parallelt fra måned 1 | Forretning og kommunikation venter ikke på teknisk modenhed |
| 01 i uge 1 | Definitionen af målet skal stå fast før noget andet begynder |

**Bløde afhængigheder:** 05 kan starte når 02's API-spike (spike 7) er færdig. 10 fodres af 09's domæneviden. 12 trækker på alt og kører hele året, men intensiveres i måned 8-12.

## Fire læringsspor

Planen er ikke tolv moduler i rækkefølge. Den er fire parallelle spor der kører hele året med varierende intensitet. Ingen uge bør kun indeholde ét spor — det producerer enten en tekniker uden forretningsforståelse eller en rådgiver uden dybde.

### Spor 1: Teknisk dybde (modul 02, 03, 04, 05, 06)

Kernen. Her ligger de fleste timer i måned 1-7, og det er her troværdigheden bygges. Sporet starter med måleapparatet i uge 1 og ender med kodebase-arkæologi i måned 9. Artefakterne er spikes med ADR, diagram, mindst ét tal og retrospektiv.

| Måned | Tyngde | Hvad der sker |
|---|---|---|
| 1-3 | 70% af tiden | Spike 1-4 i modul 02, fase 1 i modul 03 |
| 4-6 | 55% af tiden | Spike 5-8 i modul 02, fase 2 i modul 03, spike A i modul 04 |
| 7-9 | 40% af tiden | Spike 9-12 i modul 02, fase 3 i modul 03, modul 05 spikes |
| 10-12 | 25% af tiden | Drift, fase 4 i modul 03, fri spike drevet af kompetenceporten |

**Faldtesten:** falder den tekniske andel ikke til 25% i måned 10-12, har positioneringen ikke fået plads. Dybdesporet føles aldrig færdigt, så det skæres på kalenderen, ikke på fornemmelse.

### Spor 2: Governance og compliance (modul 07, 08)

Din differentiering. Kombinationen "kan bygge systemet OG kan læse det regulatoriske krav" er tynd i Danmark. Sporet kører med lav, jævn intensitet fra måned 1 (læs DPA'en, start ADR-log) og intensiveres i måned 3-6 (governance-spikes, tenant-isolation, threat model).

| Måned | Tyngde | Hvad der sker |
|---|---|---|
| 1-2 | 10% af tiden | DPA-læsning, ADR-bootstrap, regionspolicy (G1) |
| 3-6 | 20% af tiden | Tenant-isolation (flagskib), OWASP, threat model, ISO 27001 SoA-start |
| 7-9 | 15% af tiden | GDPR-sletning spike, audit-trail, SoA færdig |
| 10-12 | 10% af tiden | Vedligeholdelse, opdatering af svarbibliotek |

**Den absolutte regel fra modul 08:** hvert compliance-artefakt leveres sammen med kørende kode og en måling. Aldrig et dokument uden en deployment. Compliance uden engineering er en GRC-analytiker; engineering uden compliance er en senior udvikler; værdien ligger udelukkende i OG'et.

### Spor 3: Forretning og positionering (modul 09, 10, 11, 12)

Det spor der afgør om dybden konverterer til noget. Starter fra dag 1 med domænelæsning, beslutningslog og supportkø-gennemlæsning. Intensiveres fra måned 6, når den tekniske basis er på plads.

| Måned | Tyngde | Hvad der sker |
|---|---|---|
| 1-3 | 15% af tiden | Domæne-90-dagesplan (modul 09), beslutningslog, mandags-skriveblok startet (modul 11), fem ting uden tilladelse (modul 12) |
| 4-6 | 20% af tiden | Overtag ét kedeligt ansvarsområde (modul 12), regulatorisk roadmap (modul 10), discovery-log, kunderekognoscering |
| 7-9 | 30% af tiden | Hotspot-analyse med prisskilt (modul 10), Shape Up-pitches, design docs eksternt reviewet (modul 11), fuldtidsforhandling forberedt (modul 12) |
| 10-12 | 40% af tiden | Fuldtidsforhandling (modul 12), enhedsøkonomi pr. tenant, læringsloft-checkpoint, mundtlige tests (modul 11) |

**Faldtesten:** nul uopfordrede henvendelser om dit design ved måned 9 betyder, at dybden ikke er blevet synlig. Over 50% selvformulerede tickets ved måned 12 er det binære bevis på at mandatet er taget.

### Spor 4: Drift og praksis (tværgående)

Ikke et modul, men en vane der binder alt sammen. Spike 1 fra modul 02 deployes til Azure og driftes resten af året. Uden dette spor er de andre tre øvelser uden konsekvens.

Krav der kører hele året:
- **Driftsansvar:** en service med defineret SLO, alarmering, pipeline med rollback brugt mindst én gang
- **Skemaændringer:** mindst to expand-migrate-contract mod levende data
- **API-kompatibilitet:** mindst to ændringer uden at brække en consumer
- **Hændelser:** mindst én rigtig hændelse med skreven postmortem med gennemførte handlinger
- **Prædiktionslog:** estimér før du måler, og fejlmarginen skal falde over seks måneder
- **ADR-kadence:** mindst 15 over året, heraf mindst 5 bagudfyldte domænebeslutninger
- **Skrivepraksis:** mandags-skriveblok (modul 11), ca. 4 timer/uge

Tidsbudget: ca. 2 timer/uge dedikeret til drift, plus den tid der naturligt falder i de andre spor. I alt ca. 90 timer over året.

## 12-måneders kalender

Budgettet er 10-15 timer/uge, ca. 550-600 timer over 48 arbejdsuger. Tabellen viser hovedaktiviteter — de detaljerede spike-beskrivelser, tidsangivelser og afleveringskrav står i de enkelte moduler.

### Måned 1: Fundament og rekognoscering

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 1-2 | **02:** Spike 1 — måleapparat (20-24 t) | Læs DPA, start ADR-log | **01:** 30 opslag kodet. **12:** Fem ting uden tilladelse. **09:** Læs firmaets site | 12-14 |
| 3-4 | **02:** Spike 2 — async-fejlmønstre (12 t) | — | **11:** Mandags-skriveblok startet. **09:** Begrebsdivergens-tabel | 12-14 |

Læsning: supportpolitik, diagnostics-docs, Cleary, Programmer's Brain Del 1.

### Måned 2: Måling og domæne

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 5-6 | **02:** Spike 3 — allokering og GC (22 t). Start driftssporet | **07:** G1 — tag- og region-guardrail | **09:** Peppol BIS 3, systemarkitektur tegnet. **12:** Supportkø-gennemlæsning | 12-14 |
| 7-8 | **02:** Spike 3 færdig. **03:** Fase 1 — budgetkontrol, WAF | G1 færdig | **09:** Supportkø kategoriseret. ADPList-samtaler | 12-14 |

Læsning: Use The Index Luke, DATAS-posten, Kokosa målrettet.

### Måned 3: SQL-dybde og isolation

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 9-10 | **02:** Spike 4 — SQL uden ORM (24 t) | **08:** Start tenant-isolation flagskib (25-30 t) | **09:** Ariba API, cXML. **10:** Regulatorisk roadmap påbegyndt | 13-15 |
| 11-12 | Spike 4 færdig. **03:** Fase 1 færdig | Tenant-isolation fortsat. **07:** G5 — ADR om lejerisolation | **11:** Første diagram blindtestet. **12:** Overtag ét ansvarsområde | 13-15 |

Læsning: Use The Index Luke færdig, DDIA Storage and Retrieval, eShop som læseøvelse. **Ekstern sparring booket inden udgangen af denne måned** — sker det ikke, er det planens første og alvorligste afvigelse.

### Måned 4: EF Core, transaktioner, AZ-104

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 13-14 | **02:** Spike 5 — EF Core-diff (12 t). Spike 6 start — isolation (24 t) | Tenant-isolation flagskib afleveret | **10:** Reference class og throughput-forecast (10-12 t) | 13-15 |
| 15-16 | Spike 6 fortsat. **AZ-104 eksamensperiode** (md. 4-5) | **08:** OWASP-læsning, GDPR art. 28 | **09:** Lyt med på kundeopkald. **12:** Dag 30-90-leverancer | 13-15 |

Læsning: DDIA Transactions (to gange), Kendra Little, Toub-posten. **C01 kan køres fra nu.**

### Måned 5: API-kontrakter og observability

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 17-18 | **02:** Spike 6 færdig. Spike 7 — API-kontrakt (22 t) | **07:** G2-G3 — engineering governance, SBOM | **10:** Hotspot-analyse påbegyndt. Discovery-log | 12-14 |
| 19-20 | Spike 7 færdig. **05:** F1 — API-kontrakt i CI (22 t) | — | **11:** Første design doc eksternt reviewet. **C07 kan køres** | 12-14 |

Læsning: DDIA Encoding and Evolution, RFC 9457, versionerings-posten. **Code review-bytte etableret i denne måned.**

### Måned 6: Idempotens og compliance-dybde

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 21-22 | **02:** Spike 8 — idempotens og outbox (24 t) | **08:** Threat model-spike. ISO 27001 SoA-start | **10:** Regulatorisk roadmap færdig og præsenteret | 13-15 |
| 23-24 | Spike 8 færdig. **06:** Intensivering — SLI-design, byte-budget | **07:** G4 — licenspolitik | **09:** Spike 1 — certifikatgyldighed. **Læringsloft-checkpoint modul 12** | 13-15 |

Læsning: DDIA Replication, idempotency-draftet. **01: Rollerekognoscering gentages (2 t). C02, C04, C06 kan køres fra nu.**

### Måned 7: Multi-tenancy og platform

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 25-26 | **02:** Spike 9 — multi-tenancy (26 t). **03:** Fase 3 — governance, landing zone | **08:** GDPR-sletning spike | **10:** Hotspot-analyse afleveret med prisskilt. Første Shape Up-pitch | 13-15 |
| 27-28 | Spike 9 færdig. **05:** F2 — BFF mod Entra ID (22 t) | SoA fortsat | **11:** Narrativ/seks-sider format øvet. **C03, C05 kan køres** | 13-15 |

Læsning: DDIA Sharding, Azure tenancy models, **Fundamentals 2e begynder.**

### Måned 8: Teststrategi og Khononov

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 29-30 | **02:** Spike 10 — teststrategi (12 t). Spike 11 — caching (12 t) | **08:** Audit-trail spike. SoA færdig | **09:** Spike 2. **10:** Shape Up-pitch 2. **11:** Faciliteret session | 11-13 |
| 31-32 | **03:** Fase 3 — netværksisolation, threat model, datastore-bake-off | — | **12:** Fuldtidsforhandling forberedt — tal samlet | 11-13 |

Læsning: Fundamentals 2e, Khononov strategisk halvdel.

### Måned 9: Kompetenceport og AZ-305

| Uge | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| 33-34 | **02:** Spike 12 — kodebase-arkæologi (20 t) | Spørgeskema-maskinen opdateret (modul 12) | **10:** ADR-log: 15 ADR'er, heraf 5 bagudfyldte. Shape Up-pitch 3 | 11-13 |
| 35-36 | **Kompetenceport modul 02** (md. 9-10). **AZ-305 eksamensperiode** | — | **11:** Mundtlig test. **12:** Enhedsøkonomi pr. tenant | 11-13 |

Læsning: Fundamentals 2e færdig, The Hard Parts udvalgte kapitler. **01: Rollerekognoscering gentages (2 t). Kompetenceportene i modul 01, 02, 10, 11 evalueres.**

### Måned 10-12: Kalibrering, forhandling og overgang

| Fokus | Teknisk dybde | Governance/compliance | Forretning/positionering | Timer |
|---|---|---|---|---|
| Md. 10 | **03:** Fase 4 — WAF-review 3, reduktionsøvelse. Fri spike drevet af port | Svarbibliotek vedligeholdt | **12:** Fuldtidsforhandling gennemført. Shape Up-pitch 4 | 8-10 |
| Md. 11 | Drift fortsat. Eventuel valgfri spike | — | **10:** Forecast efterprøvet. **11:** Præsentation ved ANUG/GOTO | 8-10 |
| Md. 12 | Drift. Anti-rollen-test fra modul 01 | — | **12:** Endelig evaluering mod alle kompetenceporte | 8-10 |

Læsning: The Hard Parts, DDIA data privacy og regulering.

### Timeregnskab, samlet

| Post | Timer |
|---|---|
| Modul 02 spikes | ~240 |
| Modul 02 drift | ~90 |
| Modul 03 spikes og cert-forberedelse | ~100 |
| Modul 04 spikes | ~50 |
| Modul 05 spikes (hårdt loft) | ~87 |
| Modul 06 spikes | ~40 |
| Modul 07 spikes | ~30 |
| Modul 08 spikes | ~60 |
| Modul 09 (primært arbejdstid) | ~50 |
| Modul 10 spikes | ~50 |
| Modul 11 skrivepraksis | ~50 |
| Modul 12 spikes og forhandling | ~55 |
| Læsning på tværs | ~120 |
| ADR-skrivning og retroer | ~40 |
| **I alt** | **~1.062** |

Heraf ligger 400-450 timer i arbejdstiden (domæne, drift, ADR'er, supportkø, kundeopkald, skrivepraksis). De private 10-15 timer/uge dækker de resterende ~600 timer over 48 uger — ca. 12,5 timer/uge i gennemsnit. Buffer er bygget ind: de første seks måneder ligger højere (12-15 t/uge), de sidste seks lavere (8-10 t/uge). Bruger du 14+ timer hver uge fra måned 1, brænder du ud i måned 5.

## Case study-kortlægning

Cases er ikke eksamener — de er timeboxede trade-off-øvelser der tvinger dig til at producere artefakter under tidspres med ufuldstændig information. Hver case har en optimal periode; kør den for tidligt, og du producerer gætværk; for sent, og den er for nem.

| Case | Titel | Primært modul | Sekundære moduler | Timebox | Optimal periode | Kompetencer testet |
|---|---|---|---|---|---|---|
| C01 | Tenant-isolation under tidspres | 01 Rollen | 03, 08, 04 | 8 t | Md. 4-7 | Trade-off-analyse, kostmodel, ADR, kundekommunikation |
| C02 | Månedsafslutningen der tager 40 sekunder | 02 Teknisk fundament | 06, 10 | 6 t | Md. 5-7 | Diagnostik, SQL, måleplan, prisskilt, kalibrering |
| C03 | Azure-regningen tredoblet | 03 Azure-arkitektur | 06, 10, 07 | 6 t | Md. 6-9 | Kostarkitektur, enhedsøkonomi, guardrails, stifterkommunikation |
| C04 | Idempotent ERP-indlæsning | 04 Systemdesign | 09, 02 | 8 t | Md. 5-8 | Idempotens, feltafbildning, leveringssemantik, domæneforståelse |
| C05 | Tilgængelighed som salgsblokering | 05 Frontend | 10, 11 | 6 t | Md. 6-9 | Afgrænsning, nej med betingelse, kundedokumentation |
| C06 | Observability fra nul | 06 Observability | 02, 03, 08 | 8 t | Md. 5-8 | SLI-design, byte-budget, datapolitik, compliance |
| C07 | Guardrail uden mandat | 07 Governance | 12, 11, 03 | 5 t | Md. 4-8 | Policy-as-code, progressiv håndhævelse, intern kommunikation |

**Brug:** kør mindst fem af de syv. Kør C01 og C02 to gange — én gang i den optimale periode og én gang i måned 10-12 med samme rubrik — og sammenlign scorerne. Det er den eneste objektive progressionsmåling du har. Ingen case er løst ved at slå ting op; de er løst ved at træffe valg under usikkerhed og skrive fravalget ned.

## Progressionscheckliste

Milepæle trukket fra de enkelte modulers kompetenceporte. Listen er binær: ja eller nej, med artefakt eller observation som bevis. "Jeg føler mig klar" er standard hos kompetente folk; "jeg føler mig klar" hos inkompetente. Porten afgøres på tællelige ting.

### Måned 3

| # | Kriterium | Kilde | Bevis |
|---|---|---|---|
| 1 | Måleapparatet (spike 1) er deployet og har kørt i mindst én måned | 02 | Oppetidsrapport |
| 2 | Niveau 1-selvvurderingen i modul 02 er bestået på alle seks spørgsmål | 02 | Skriftlig vurdering med dato |
| 3 | 30 danske arkitektopslag er kodet i et regneark med gap-analyse | 01 | Regnearket |
| 4 | Systemkortet (C4 context + container) ligger i repoet | 12 | Filen, reviewet af mindst én kollega |
| 5 | Ekstern sparring er booket og har kørt mindst én session | 12 | Dato og navn |
| 6 | Mindst 5 bagudfyldte ADR'er for eksisterende beslutninger | 07, 11 | Filerne i repoet |
| 7 | Beslutningslog er startet med mindst 20 poster | 12 | Loggen |
| 8 | Domænets syv områder kan tegnes på en tavle uden noter | 09 | Demonstreres |

### Måned 6

| # | Kriterium | Kilde | Bevis |
|---|---|---|---|
| 9 | Niveau 2-selvvurderingen i modul 02 er bestået | 02 | Skriftlig vurdering |
| 10 | AZ-104 bestået | 03 | Certifikat |
| 11 | Tenant-isolation flagskib-spike afleveret med bugmatrix og ADR | 08 | Artefaktsæt |
| 12 | Regulatorisk roadmap præsenteret til stifteren | 10 | Dokumentet og en dato |
| 13 | Mindst 30 poster i kalibreringsloggen med interval og faktisk tid | 10 | Loggen |
| 14 | Over 30% af tickets selvformulerede | 12 | Optælling |
| 15 | Rørt mindst 5 af 7 systemområder i produktion | 12 | Liste med datoer |
| 16 | Discovery-log med 30+ poster, rolle registreret | 10 | Loggen |
| 17 | Code review-bytte kører med mindst én ekstern person | 02 | Datoer |
| 18 | Læringsloft-checkpoint gennemført skriftligt med seks svar | 12 | Dokumentet |
| 19 | Prædiktionsloggens fejlmargin er dokumenteret over mindst tre måneder | 02 | Loggen |
| 20 | Restore-test gennemført med målt RTO og RPO | 12 | Rapport med tidsstempler |

### Måned 9

| # | Kriterium | Kilde | Bevis |
|---|---|---|---|
| 21 | Kompetenceporten i modul 02: ja til mindst 11 af 14 | 02 | Artefakter og observationer |
| 22 | AZ-305 bestået | 03 | Certifikat |
| 23 | Mindst 15 ADR'er, heraf 3 "superseded" med begrundelse | 11 | Filerne |
| 24 | Mindst 8 komplette spike-artefaktsæt, gennemgåeligt koldt | 02 | Repoet |
| 25 | Tre hændelser ejet fra alarm til færdig postmortem | 12 | Postmortems |
| 26 | To designoplæg gennemgået uden for firmaet med dokumenterede ændringer | 10 | Feedbacken |
| 27 | Ét valg ændret eller forkastet pga. et dokument du skrev | 10 | Dokument, beslutning, dato |
| 28 | Fitness functions i CI der har fejlet mindst ét build | 10 | CI-log |
| 29 | Svarbibliotek med 60-100 standardsvar i repoet | 12 | Filen |
| 30 | Hotspot-analyse med prisskilt fremlagt og besluttet (ja eller nej) | 10 | Dokumentet og beslutningen |

### Måned 12

| # | Kriterium | Kilde | Bevis |
|---|---|---|---|
| 31 | 45-minutters-testen fra modul 01: ukendt problem, otte kravsspørgsmål, kontekstdiagram, to fravalg, fem NFR'er med tal, tre risici — foran en fremmed | 01 | Optagelse vurderet af en udenforstående |
| 32 | Præmisændringstesten: du itererer i stedet for at forsvare | 01 | Observerbart på optagelse |
| 33 | Anti-rollen-testen: deployet til produktion inden for seks måneder, driftsansvar inden for tolv | 01 | Datoer |
| 34 | Over 50% selvformulerede tickets | 12 | Optælling |
| 35 | Mindst to områder overdraget til navngivne kolleger med runbook | 12 | Runbooks og perioden |
| 36 | Mindst tre uopfordrede henvendelser om dit design | 01 | Kan dateres |
| 37 | Tre ting du var sikker på og tog fejl om, med målingen | 02 | Retroerne |
| 38 | Fuldtidskontrakt med anciennitet, ansvarsområde, uddannelsesbudget, genforhandlingsdato | 12 | Kontrakten |
| 39 | Fem fejlmønstre du selv har ramt i produktion, navngivet | 01 | Postmortems |
| 40 | Du kan på fem minutter forklare rollens tre virksomhedstyper med konkrete opslag | 01 | Demonstreres |

**Samlet:** 40 kriterier. Ingen af dem afgøres af din fornemmelse. Mindst to praktiserende arkitekter uden for LeanLinking skal have gennemgået et af dine designs skriftligt, før noget af det tæller.

## Sådan bruges planen

### Start her

1. Læs modul 01 i sin helhed. Hele dokumentet, samme dag. Det definerer hvad du sigter mod og hvad du ikke sigter mod.
2. Læs modul 12's afsnit "Uge 1: fem ting du kan gøre uden at spørge om lov". Gør alle fem inden fredag.
3. Begynd spike 1 i modul 02. Måleapparatet er fundament under alt andet.
4. Start mandags-skriveblokken fra modul 11 i uge 2. Én time, fast, på samme tidspunkt.
5. Begynd domæne-90-dagesplanen fra modul 09 parallelt — den kører primært i arbejdstiden.

### Rækkefølge når du er i tvivl

Følg de fire spor, ikke modulnumrene. I enhver given uge bør du røre mindst to spor. Modul 02 har den mest detaljerede uge-for-uge-progression — brug den som rygrad og fletter de andre spor ind.

### Når du er gået i stå

Tre spørgsmål, i denne rækkefølge:

1. **Har du et artefakt med et tal fra de sidste to uger?** Nej: problemet er at du læser i stedet for at producere. Gå tilbage til den spike du sidst arbejdede på og aflever noget halvfærdigt med ét målt tal. Halvfærdigt med tal slår færdigt uden.
2. **Har du fået feedback fra et menneske i de sidste fire uger?** Nej: du øver dig i et vakuum, og du kan have øvet forkert i fire uger uden at vide det. Send et artefakt til din eksterne sparringspartner, din code review-buddy eller en ADPList-mentor. Feedback er ikke valgfrit — det er den eneste kalibrering du har.
3. **Er din kalibreringslog opdateret?** Nej: du ved ikke om du bliver bedre. Gå tilbage til den seneste spike, skriv hvad du troede ville ske, og sammenlign med hvad der skete.

### Når du vil springe forud

Spring kun forud inden for et spor, aldrig på tværs. Du kan springe spike 10 og 11 i modul 02 over, hvis spike 9 og porten viste at du allerede kan det. Du kan ikke springe modul 02's spikes over og gå direkte til modul 03 — uden egne tal er alt i Azure-sporet blogcitater.

Undtagelsen: modul 12's fuldtidsforhandling skal ligge to til tre måneder før du er færdig, ikke efter. Timer den forkert, er den dyreste post i planen tabt.

### Hvad du gør med denne fil

Åbn den første mandag i hver måned. Tjek progressionschecklisten. Opdatér din egen status med dato og artefakt-reference. Hvis et kriterium er grønt uden et artefakt, er det ikke grønt — det er en fornemmelse.

Planen er ikke et pensum. Den er en rækkefølge af artefakter du producerer, og en liste af kriterier du måler dig selv på. Alt mellem artefakterne er din egen vej derhen.
