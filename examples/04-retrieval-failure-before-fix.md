# 04-retrieval-failure-before-fix: faktisk agenttest

**Spørgsmål:** Jeg har mistet mit pas i Spanien. Hvad skal jeg gøre?

Model: `google/gemini-3.1-flash-lite`. Agent execution: `mK0Ofi3eN2zBVxjR`. Start: `2026-11-03 15:49:01.214` (UTC i n8n-loggen). Status: `success`. Testet i en ny session; teksten nedenfor er ikke rettet efterfølgende.

## Værktøjskald og hentede oplysninger

### Værktøj – søg rejseinformation

Workflow execution: `176`.

Input:

```json

{
  "country": "Spanien",
  "question": "hvad skal jeg gøre hvis jeg har mistet mit pas?"
}

```

Resultat: `found=true`, antal `7`.

| Kilde | Chunk | Titel/emne | Udvælgelsesscore |
|---|---|---|---:|
| 1 | `es-rejsevejledning-12` | Spanien | 0.8374357 |
| 2 | `es-rejsevejledning-13` | Spanien | 0.8374357 |
| 3 | `es-rejsevejledning-14` | Spanien | 0.8374357 |
| 4 | `es-rejsevejledning-4` | Spanien | 0.8357134 |
| 5 | `es-rejsevejledning-5` | Spanien | 0.8357134 |
| 6 | `es-rejsevejledning-6` | Spanien | 0.8357134 |
| 7 | `es-rejsevejledning-7` | Spanien | 0.83246267 |

Kilde-URL’er i resultatet:

- https://um.dk/rejse-og-ophold/rejse-til-udlandet/rejsevejledninger/spanien

Værktøjets besked: Søgningen har fundet tekstbidder. De er ikke nødvendigvis alle relevante. Brug kun oplysninger, der besvarer spørgsmålet og gælder det valgte land. Henvis med [Kilde N] ud fra source_number og medtag den tilhørende source_url. Hvis teksterne ikke besvarer spørgsmålet, sig det tydeligt. retrieved_at er indsamlingsdatoen, ikke kildens opdateringsdato.

## Agentens faktiske svar

> Hvis du har mistet dit pas i Spanien, bør du kontakte den danske ambassade eller et dansk konsulat for at få hjælp [Kilde 3].
>
> Du kan finde kontaktoplysninger til den danske ambassade og de danske konsulater i Spanien via deres hjemmeside [http://spanien.um.dk/](http://spanien.um.dk/) eller i Udenrigsministeriets "Rejseklar"-app. Du kan også altid kontakte Udenrigsministeriets Globale Vagtcenter, som har åbent hele døgnet [Kilde 3].
>
> Dette er uofficiel vejledning. Kontrollér oplysningerne i den officielle kilde.

## Kort vurdering

**Vurdering: fejl før retrievalrettelsen.** De tre bedste vektorseeds kom fra generel rejsevejledning. Efter naboopslag modtog modellen syv chunks, men ingen fra det særlige pasdokument. Den gav derfor en generel kontaktanbefaling i stedet for de understøttede pastrin og citerede kun `[Kilde 3]` uden den krævede source_url. Høj vektorlighed var ikke det samme som relevans for den konkrete opgave.

Rettelsen udvidede kandidatfeltet fra 3 til 20, gav pasdokumentet et åbent dokumenteret emnetillæg på 0,25 ved mistet-pas-spørgsmål og beholdt nabochunks. Der er ingen hardcodede pas-chunk-ID'er i den endelige søgning. Case 2 viser forbedringen og de fejl, der stadig er tilbage. Det er ikke en kontrolleret modelsammenligning eller en garanti for andre spørgsmål.

[Fuld trace med alle returnerede kildetekster](raw/04-retrieval-failure-before-fix.json)
