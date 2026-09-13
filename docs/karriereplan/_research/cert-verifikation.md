# Verifikationslog - certificeringer, 10. sep 2026

## Metode
learn.microsoft.com, scrum.org, developer.hashicorp.com, aka.ms, wikipedia BLOKERET af egress-proxy.
WebSearch-budget opbrugt (200/200) af tidligere agent i samme session.
Verifikation gennemfoert via GitHub (MicrosoftLearning-org), som vedligeholder officielle lab-repos pr. eksamenskode.
Arkiveringsstatus + sidste commit-dato = live/doed-signal for kursusindhold.

## VERIFICERET 10. sep 2026
- AZ-305 lab-repo: AKTIV, opdateret 2026-09-10, ikke arkiveret -> AZ-305 lever
- AZ-104 lab-repo: AKTIV, opdateret 2026-09-10 -> AZ-104 lever
- SC-100 lab-repo: AKTIV, opdateret 2026-09-09 -> SC-100 lever
- SC-300 lab-repo: AKTIV, opdateret 2026-09-10 + nyt mslearn-sec-identity (marts 2026) -> lever
- AZ-900 lab-repo: AKTIV (nyt repo marts 2025) -> lever
- AZ-204 gammelt repo: ARKIVERET. Efterfoelger mslearn-azure-developer ARKIVERET 2026-09-01,
  banner: "This repository has been archived. The course and self-paced content it supported have been retired."
  -> bekraefter AZ-204-pensionering
- AZ-400 gammelt repo arkiveret jan 2026, men KUN flytning: labs -> mslearn-devops (AKTIV, opd. 2026-09-08)
  -> AZ-400 LEVER. Arkivering var repo-flytning, ikke eksamenspensionering.
- AI-102 repo arkiveret dec 2023 = reorganisering til mslearn-ai-* repos, ikke pensionering
- AI-900 repo arkiveret = reorg til mslearn-ai-fundamentals (AKTIV)

## VIGTIGSTE FUND - korrigerer briefets praemis om AI-200
mslearn-azure-ai (oprettet 2025-10-21, AKTIV, opd. 2026-09-08)
_config.yml title: "Develop AI Cloud Solutions on Microsoft Azure"
instructions/ indeholder:
  app-sec-config, azure-container-apps, azure-database-postgresql,
  azure-kubernetes-service, azure-managed-redis, container-hosting,
  cosmosdb, instrument-observe, integrate-services
=> Pensum er OVERVEJENDE KLASSISK CLOUD-NATIVE UDVIKLING (containere, Cosmos DB,
   PostgreSQL, Redis, Key Vault/managed identity, observability, service integration).
   IKKE primaert RAG/vector-databaser. "AI" er indpakning; maalte faerdigheder er
   AZ-204-arvtager. Briefets formulering "AI-drejet, ikke en generel udviklereksamen"
   holder ikke mod lab-pensum.

## NYE KODER OPDAGET
- AZ-1012/1013/1014 "Govern/Manage/Secure AI-Ready Infrastructure" (okt 2025)
- AI-300 (via mslearn-mlops.ja-jp beskrivelse "WWL-Lab-AI-300")
- DP-800 (via mslearn-sql-developer beskrivelse)

## IKKE VERIFICERBART I DENNE SESSION
AZ-305 forudsaetningsregel, priser, pensumvaegte, PSM I-pris, Terraform-version,
studenterrabatter. Alt saadant er markeret verificeret=false i output.
