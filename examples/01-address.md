# 01-address: faktisk agenttest

**Spørgsmål:** Hvad er adressen på Danmarks ambassade i Spanien?

Model: `google/gemini-3.1-flash-lite`. Agent execution: `6ZZwumdL5NrBNED1`. Start: `2026-11-03 16:04:32.734` (UTC i n8n-loggen). Status: `success`. Testet i en ny session; teksten nedenfor er ikke rettet efterfølgende.

## Værktøjskald og hentede oplysninger

### Værktøj – find ambassade

Workflow execution: `180`.

Input:

```json

{
  "country": "Spanien"
}

```

Resultat: `found=true`, antal `1`.

```json

[
  {
    "embassy": "Danmarks ambassade i Spanien",
    "address": "Calle Serrano 26, 7. 28001 Madrid",
    "city": "Madrid",
    "country": "Spanien",
    "source_url": "https://um.dk/spanien/om-os/kontakt-og-ekspedionstid/",
    "retrieved_at": "2026-11-03T15:50:57.332Z"
  }
]

```

Værktøjets besked: Ambassadeoplysninger fundet i den gemte graf. Brug source_url som kilde. retrieved_at er indsamlingsdatoen.

## Agentens faktiske svar

> Adressen på Danmarks ambassade i Spanien er Calle Serrano 26, 7. 28001 Madrid.
>
> Kilde: https://um.dk/spanien/om-os/kontakt-og-ekspedionstid/

## Kort vurdering

**Vurdering: bestået i denne test.** Agenten valgte grafværktøjet, sendte `country=Spanien` og returnerede præcis den gemte adresse og kontaktsidens URL. Svaret var kort og blandede ikke den spanske ambassade i Danmark sammen med Danmarks ambassade i Spanien. Adressens aktualitet er kun så god som den indsamlede kilde; testen verificerer overensstemmelse med databasen, ikke en uafhængig aktuel adressekontrol.

[Fuld trace med alle returnerede kildetekster](raw/01-address.json)
