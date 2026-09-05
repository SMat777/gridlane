# Design- og frontend-værktøjsstak

Research udført 2026-09-05. Formål: værktøjer til at bygge websites, features,
landingpages, showcases og prototyper i Gridlane-stacken — og ende med reelle,
salgsbare produkter.

Gridlanes stack, som anbefalingerne er valgt op mod:
Next.js 16 · React 19 · Tailwind v4 · shadcn v4 · Base UI · lucide-react ·
@xyflow/react · Supabase · zustand · vitest · pnpm monorepo.

**Licensprincip gennem hele dokumentet:** alt der anbefales som standard må
sendes med i et produkt der sælges til kunder, uden attributionskrav.
Undtagelser er markeret eksplicit.

---

## 0. Gratis og allerede på din konto (start her)

Verificeret direkte mod kontoens plugin-katalog. Tre plugins i marketplace
`knowledge-work-plugins` er tilgængelige men **slået fra**:

| Plugin | Indhold | Hvorfor det betyder noget |
|---|---|---|
| **Design** | `design:design-critique`, `design:design-system`, `design:accessibility-review`, `design:design-handoff`, `design:ux-copy`, `design:research-synthesis`, `design:user-research` | `design-critique` er et "ser det her premium ud?"-gennemsyn. Nul omkostning, nul dependency. |
| **Figma** | 14 skills: `figma-design-to-code`, `figma-code-connect`, `figma-implement-motion`, `figma-shaders`, `figma-generate-library` m.fl. + Figma MCP-server | Hele design-til-kode-banen, hvis du har Figma-seat. |
| **Modern Web Guidance** | `modern-web-guidance`, `chrome-extensions` | Holder agenten opdateret på nuværende web-best-practices. |

Slå dem til med `/plugin`. Det er den billigste kvalitetsforbedring i hele
dokumentet.

---

## 1. MCP-servere

### 1.1 Visuel verifikation — den vigtigste feedback-loop

Uden det her retter agenten CSS i blinde.

**Chrome DevTools MCP er default'en.** Google, officiel, Apache-2.0,
npm 1.8.0 (2026-08-25). Den taler CDP, så ud over screenshots kan den give
**computed CSS for en konkret selector**, console-fejl med source-mapped
stacktraces, network-waterfalls og performance-traces. Man diagnosticerer med
computed CSS og *bekræfter* med screenshot — ikke omvendt.

**Playwright MCP** er den holdbare halvdel: cross-browser, og `scale: "device"`
giver 4x pixels på et Retina-display, hvilket er forskellen på om modellen kan
læse en 12px fejltekst. Bliver senere din E2E-rig.

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

Sikkerhed: giv Chrome DevTools MCP en **ren Chrome-profil**, ikke din daglige.
Serveren eksponerer hvad browseren kan se for modellen.

### 1.2 Komponentkilde

**shadcn MCP** — højeste signal-støj-forhold for denne stack. Agenten installerer
rigtige komponenter fra shadcn-registry plus tredjeparts- og private registries
i stedet for at hallucinere JSX. npm `shadcn@4.21.0` (2026-09-04), MIT.

```bash
# verificér underkommandoen først:
npx shadcn@latest mcp --help
claude mcp add shadcn -- npx -y shadcn@latest mcp
```

### 1.3 Design-fil ind

| Server | Vurdering |
|---|---|
| **Figma MCP (officiel remote)** — `https://mcp.figma.com/mcp` | Kræver **Dev- eller Full-seat på betalt plan**. Starter-planen er begrænset til **6 tool-kald pr. måned** = demo, ikke brugbart. Giver auto-layout, varianter, variabler, Code Connect. |
| **Framelink `figma-developer-mcp`** — 15.8k*, MIT, npm 0.13.2 (2026-06-18) | **Den gratis vej.** Personal access token, virker på gratis Figma. Lavere fidelity: ingen Code Connect, ingen live selection. |
| **Penpot MCP (officiel)** — npm `@penpot/mcp` 2.15.4 (2026-07-08) | Eneste troværdige gratis, selv-hostbare, **read-write** design-fil-MCP. DTCG-tokens. Remote multi-user-mode er stadig undervejs. |

```bash
# gratis vej:
claude mcp add framelink -- npx -y figma-developer-mcp --figma-api-key=DIN_PAT --stdio
```

### 1.4 Deploy og backend

```bash
claude mcp add vercel --transport http https://mcp.vercel.com          # OAuth
claude mcp add netlify -- npx -y @netlify/mcp                          # npm 1.15.1
claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest \
  --read-only --project-ref=DIT_PROJECT_REF
```

**Supabase MCP kan eksekvere SQL og køre migrations.** Start altid med
`--read-only` og en pinned `--project-ref`.

### 1.5 Tilgængelighed

```bash
claude mcp add a11y-scan -- npx -y mcp-accessibility-scanner   # npm 3.3.2 (2026-08-30)
```

Friskere end alternativet `a11y-mcp` (1.0.6, 2026-03-22). Begge kører axe-core.

### 1.6 Hul i økosystemet

**Der findes ingen troværdig Tailwind- eller style-dictionary token-MCP.**
`@tailwindcss/mcp` eksisterer ikke på npm. Nærmeste alternativer er Penpots
DTCG-eksport eller `designlang` (se 3.4).

---

## 2. Komponentregistries — licens er hele historien

Ved shadcn-stil registries kopieres kildekoden ind i dit repo. **Licensen på den
kopierede kode er det der styrer dit solgte produkt** — ikke bibliotekets egen.

| Registry | Licens | Må sælges videre? |
|---|---|---|
| **shadcn/ui** (123k*) | MIT | Ja, ubegrænset |
| **Magic UI** (22.2k*) | MIT | Ja, ubegrænset |
| **Motion Primitives** (6.2k*) | MIT | Ja, ubegrænset |
| **Kokonut UI** (2.1k*) | MIT | Ja, ubegrænset |
| **daisyUI** (42.3k*) | MIT | Ja — men class-lag, ikke ejet kildekode |
| **HeroUI v3** (30.6k*) | MIT | Ja. v3 er en rewrite på React Aria + Tailwind v4; brud fra v2 |
| **Radix Themes** (8.7k*) | MIT | Ja — men npm-bibliotek, ikke kopieret kode, og distinkt udseende |
| **tweakcn** (10.3k*) | Apache-2.0 | Ja. Visuel shadcn-temaeditor -> CSS-variabler |
| **React Bits** (46.8k*) | **MIT + Commons Clause** | Ja til website/app/SaaS. **Nej** til at sælge en template bygget på den — licensen forbyder salg/videredistribution af selve komponenterne, alene eller bundlet |
| **Origin UI** | **Splittet: repo-default AGPL-3.0**, kun `apps/ui/` og `apps/origin/` er MIT | Kun MIT-delene. Kopiér enkeltkomponenter, aldrig hele repoet |
| **21st.dev** (5.4k*) | Platform rapporteret MIT, **men licens er pr. komponentforfatter** | Tjek pr. komponent |
| **Aceternity UI** | **Uverificeret** — domænet var blokeret under research | Antag intet. Få licensen skriftligt før videresalg |
| **Tailwind Plus** | Proprietær, ~$299 engang | Ja til skræddersyede kundesites. **Nej** til en template du sælger til flere kunder |

### shadcn CLI v4 — registry-mekanikken

```bash
npx shadcn@latest add @registry/component          # namespaced
npx shadcn@latest add https://x.com/r/thing.json   # direkte URL
npx shadcn@latest add button --dry-run --diff --view
npx shadcn@latest init --preset <kode>             # helt designsystem fra én kode
npx shadcn@latest init -t next --monorepo
npx shadcn@latest info                             # dumper projektkontekst til agenten
npx shadcn@latest docs combobox
```

Nyt i v4: `registry:base` (helt designsystem som ét payload), `registry:font`,
`include` (komposition af registries), `shadcn registry validate`.

---

## 3. CLI-værktøjer

### 3.1 Animation

| Værktøj | Licens | Noter |
|---|---|---|
| **Motion** `motion@13.2.0` (33.5k*) | MIT | Framer-motions efterfølger. **Default.** |
| **Lenis** `lenis@1.3.26` (15.7k*) | MIT | Smooth scroll |
| **GSAP 3.15** (28.3k*) | **Custom "no-charge"**, ikke OSI | Gratis kommercielt inkl. SplitText/MorphSVG/ScrollSmoother efter Webflow-opkøbet. **Restriktion:** må ikke bruges til at bygge et konkurrerende visuelt animationsværktøj. Sidste push 2026-04-13. Eneste ikke-open-source afhængighed her — læs `gsap.com/standard-license` selv |
| **Rive** runtime | MIT | Runtime gratis for altid. **Editorens gratis tier kan ikke eksportere `.riv`** — $9/seat/md er den reelle gate |
| **Lottie** | MIT | Foretræk `@lottiefiles/dotlottie-react` til nyt arbejde. Animationsfilerne har egne licenser |
| **three.js / R3F** | MIT | Kun når 3D *er* produktet — stort tidsforbrug |

### 3.2 Visuel QA — hvad giver agenten en reel loop?

| Værktøj | Licens | Agent-loop |
|---|---|---|
| **Playwright** `@playwright/test@1.63.0` (95.6k*) | Apache-2.0 | **Bedst.** Lokalt, screenshots går direkte ind i Read-værktøjet som billeder. Indbygget `toHaveScreenshot()` pixel-diff uden nogen service |
| **axe-core** `4.13.0` | MPL-2.0 | Struktureret violation-JSON. **MPL-2.0 som uændret dev-dependency pålægger dit produkt intet** |
| **unlighthouse** `0.18.0` | MIT | Crawler hele sitet i én kommando. Undervurderet til "audit før aflevering" |
| **Lighthouse CI** `@lhci/cli@0.15.1` | Apache-2.0 | JSON + assertions der fejler builden |
| **Argos** `@argos-ci/cli@6.9.2` | MIT | Gratis 5.000 screenshots/md. Eneste open-source hostede diffing |
| **pa11y** `10.0.0` | LGPL-3.0-only | Fungerer, men axe-core dækker samme grund med renere licens |

Playwright + axe-core + unlighthouse dækker ~95% uden løbende omkostning.

### 3.3 Assets

| Værktøj | Licens | Noter |
|---|---|---|
| **sharp** `0.35.4` (32.6k*) | Apache-2.0 | ~25x hurtigere end squoosh |
| **svgo** `4.1.0` (22.7k*) | MIT | |
| **lucide-react** `1.41.0` | ISC | Allerede i stacken |
| **@tabler/icons-react** `3.46.0` | MIT | 6.100+ ikoner |
| **@iconify/react** `6.0.2` | MIT **kun for frameworket** | **Største licensfælde ved videresalg:** hvert af ~300k ikoner har sin egen licens — nogle CC-BY (attribution), nogle ikke-kommercielle. Bliv på Lucide/Tabler, så undgår du spørgsmålet |
| **Fontsource** | Pr. font, typisk OFL-1.1 | OFL tillader indlejring i kommercielle produkter; du må ikke sælge selve fonten |
| **satori / @vercel/og** | MPL-2.0 | Uændret dependency = intet krav til din kode. Det er Next.js' `ImageResponse` |
| **subfont** `7.2.3` / **glyphhanger** | MIT | Reelle besparelser. OFL tillader subsetting |

### 3.4 Design-tokens

**Tailwind v4 `@theme`** er det rigtige svar for denne stack — CSS-variabel-nativ,
og både tweakcn og shadcn-presets sigter mod den. `style-dictionary` (Apache-2.0)
er overkill medmindre du leverer til flere platforme. **Panda CSS og Park UI er
gode, men forkerte her** — at forlade Tailwind koster hele
shadcn/tweakcn/Magic UI-økosystemet uden gevinst.

**`designlang`** (MIT, `Manavarya09/design-extract`) trækker et komplet
designsystem ud af et hvilket som helst live website — tokens, Tailwind-config,
Figma-variabler, motion-specs, a11y-rapport. Ingen API-nøgle:

```bash
npx designlang https://stripe.com
npx designlang grade <url>
npx designlang fidelity <url> --clone <lokal-url>
```

---

## 4. Claude Code plugins og skills

| Item | Install | Licens |
|---|---|---|
| **`frontend-design`** (Anthropic officiel) | `/plugin install frontend-design@claude-plugins-official` | Anthropic |
| **`webapp-testing`** (anthropics/skills, 174k*) | `/plugin marketplace add anthropics/skills` | Apache-2.0 |
| **`shadcn/skills`** | `npx skills add shadcn/ui` | MIT |
| **`ui-ux-pro-max-skill`** (125k*) | `/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` + `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill` | MIT |
| **`taste-skill`** (84k*) | via marketplace | Uverificeret |
| **`wshobson/agents`** `ui-design` (39.4k*) | `/plugin marketplace add wshobson/agents` | Uverificeret |

`webapp-testing` er præcis den loop du vil have: `scripts/with_server.py`
starter dev-serveren, venter på readiness, tager screenshots, inspicerer DOM,
lukker ned.

**Sikkerhed:** plugins eksekverer vilkårlig kode med dine rettigheder. Anthropic
vetter ikke tredjeparts-marketplaces. Foretræk `claude-plugins-official` og
`claude-plugins-community` (SHA-pinned) frem for rå `owner/repo`-marketplaces.
Tredjeparts "bedste plugins"-lister får ofte install-kommandoerne forkert.

---

## 5. Anbefalet minimal stak

```bash
# --- 0. Claude Code-laget (kør inde i Claude Code) ---
#   /plugin                       -> slå Design, Figma, Modern Web Guidance til
#   /plugin install frontend-design@claude-plugins-official
#   /plugin marketplace add anthropics/skills     -> installér webapp-testing
#   npx skills add shadcn/ui

# --- 1. MCP: se, byg, ship ---
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
claude mcp add playwright -- npx -y @playwright/mcp@latest
claude mcp add shadcn -- npx -y shadcn@latest mcp     # verificér med --help først
claude mcp add vercel --transport http https://mcp.vercel.com
claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest \
  --read-only --project-ref=DIT_PROJECT_REF

# --- 2. Byg UI hurtigt ---
pnpm dlx shadcn@latest add @magicui/hero-video-dialog @motion-primitives/text-effect

# --- 3. Få det til at se premium ud ---
pnpm add motion lenis
#   tema: byg på tweakcn.com -> indsæt CSS-variabler i globals.css @theme

# --- 4. Verificér visuelt ---
pnpm add -D @playwright/test @axe-core/playwright
pnpm exec playwright install --with-deps chromium
pnpm dlx unlighthouse --site http://localhost:3000

# --- 5. Optimér assets ---
pnpm add -D sharp svgo
pnpm add @fontsource-variable/inter
```

Licenser i blokken: MIT, Apache-2.0, ISC, MPL-2.0 som uændrede dependencies,
OFL-1.1. **Intet blokerer videresalg. Intet kræver attribution i det du sender
med produktet.**

Hver MCP-server bruger kontekst på tool-definitioner i *hver* tur. Tilføj kun
servere ud over den her liste når en konkret opgave kræver det. Læg
projektrelevante servere i en committet `.mcp.json` i monorepo-roden; personlige
i user scope.

---

## 6. Skip — og hvorfor

**Findes ikke:** Lovable, Subframe, Relume, tldraw, Excalidraw og Framer har
**ingen MCP-servere**. De optræder kun som fyld i "best design MCP"-lister.

**Døde:** `puppeteer-mcp-server` og `@modelcontextprotocol/server-puppeteer`
(16-18 mdr. uden release) · `mcp-lighthouse` (mar 2025) · `figma-mcp`,
`mcp-figma` · `@squoosh/cli` (droppet af Google) · `token-transformer`
(~3 år) · `shadcn-ui/next-template` (arkiveret) · `shadcn-ui/taxonomy`
(19k*, men Next.js 13 — høje stjerner er ikke det samme som aktuelt).

**Forkert prisniveau for et solo-studie:** Percy (~$599/md) · Chromatic
(~$179/md, Storybook-formet) · Applitools · Deque axe DevTools (axe-core
gratis bruger samme motor) · Browserbase/Stagehand (betalt cloud-browser-infra;
tilføjer omkostning og latency uden gevinst over Chrome DevTools MCP lokalt).

**Risikabelt:** **Mobbin MCP** er uofficiel og autentificerer ved at replaye
**din session-cookie** mod Mobbins private interne API. Sandsynligt ToS-brud og
ét deploy fra at gå i stykker. Hører ikke hjemme i kommercielt arbejde.

**21st.dev Magic MCP gratis tier** er ~5 generationer/md — det er en prøve, ikke
et tier. Enten budgettér $20/md eller lad være.

---

## 7. Ikke verificeret — tjek selv før du bruger penge

Begge research-agenters sessioner havde blokeret udgående adgang til flere
leverandørdomæner. Alle npm-versioner og -datoer ovenfor er hårdt verificeret
mod npm-registret; følgende er ikke:

1. **GSAPs faktiske licenstekst** (`gsap.com` blokeret). Gratis-kommercielt er
   bekræftet via npm-metadata, Webflows annoncering og ScanCode LicenseDB.
   Konkurrent-restriktionen er kun fra søgeresultater. GitHub rapporterer
   **ingen SPDX-licens** for repoet.
2. **Tailwind Plus' licens og pris** (~$299/$979 og "må ikke bruges til en
   template der sælges til flere kunder"). Den dyreste beslutning her —
   verificér på `tailwindcss.com/plus/license`.
3. **Aceternity UI** — nul kildeverificeret licensinformation. Antag ikke MIT.
4. **21st.dev pr. komponent-licens.**
5. **Park UI, Blazity/next-enterprise, ixartz/SaaS-Boilerplate, Bigspring,
   wshobson/agents** — LICENSE-filer ikke hentet. Bigspring er det klassiske
   "gratis tema, attribution påkrævet"-mønster.
6. **Install-kommandoerne til shadcn MCP, Storybook MCP og Webflow** — kør
   `--help` før du skriver dem ind i `.mcp.json`.
