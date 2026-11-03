# 02-passport: faktisk agenttest

**Spørgsmål:** Jeg har mistet mit pas i Spanien. Hvad skal jeg gøre?

Model: `google/gemini-3.1-flash-lite`. Agent execution: `pyR95gntYPqjQm4X`. Start: `2026-11-03 16:00:21.594` (UTC i n8n-loggen). Status: `success`. Testet i en ny session; teksten nedenfor er ikke rettet efterfølgende.

## Værktøjskald og hentede oplysninger

### Værktøj – søg rejseinformation

Workflow execution: `177`.

Input:

```json

{
  "country": "Spanien",
  "question": "mistet pas hvad skal jeg gøre"
}

```

Resultat: `found=true`, antal `5`.

| Kilde | Chunk | Titel/emne | Udvælgelsesscore |
|---|---|---|---:|
| 1 | `es-mistet-pas-0` | Bortkommet eller stjålet pas | 1.0783958 |
| 2 | `es-mistet-pas-1` | Bortkommet eller stjålet pas | 1.0783958 |
| 3 | `es-rejsevejledning-12` | Spanien | 0.8398821 |
| 4 | `es-rejsevejledning-13` | Spanien | 0.8398821 |
| 5 | `es-rejsevejledning-14` | Spanien | 0.8398821 |

Kilde-URL’er i resultatet:

- https://um.dk/spanien/rejse-og-ophold/pas-og-konsulaere-ydelser/pas/bortkommet-eller-stjaalet-pas

- https://um.dk/rejse-og-ophold/rejse-til-udlandet/rejsevejledninger/spanien

De to pasafsnit indeholder bl.a. politirapport før henvendelse om provisorisk pas, den lokale telefonmulighed i Madrid med afhentning, to pasfotos og fortsættelsen om pasansøgningsskemaet. Alle fulde kildetekster, scores og metadata findes i JSON-tracen nedenfor.

Værktøjets besked: Søgningen har fundet tekstbidder. De er ikke nødvendigvis alle relevante. Brug kun oplysninger, der besvarer spørgsmålet og gælder det valgte land. Henvis med [Kilde N] ud fra source_number og medtag den tilhørende source_url. Hvis teksterne ikke besvarer spørgsmålet, sig det tydeligt. retrieved_at er indsamlingsdatoen, ikke kildens opdateringsdato.

## Agentens faktiske svar

> Hvis du har mistet dit pas i Spanien, kan du få udstedt et provisorisk pas til hjemrejse hos den danske ambassade eller et af de danske konsulater.
>
> Følg disse trin:
>
> 1. **Anmeld tabet**: Kontakt en lokal politistation for at anmelde tabet og få en politirapport ("Denuncia Policial"). I Madrid kan anmeldelsen i visse tilfælde foretages telefonisk på (+34) 90 210 2112, hvorefter rapporten skal afhentes på en politistation.
> 2. **Forbered dokumentation**: Du skal bruge to fotos i passtørrelse (3,5 x 4,5 cm) og udfylde et pasansøgningsskema (kan downloades via linket herunder).
> 3. **Besøg ambassaden/konsulatet**: Medbring politirapport, fotos og det udfyldte skema til ambassaden i Madrid eller et af de danske konsulater i Spanien.
> 4. **Gebyr**: Vær opmærksom på, at der skal betales gebyr for udstedelsen af det provisoriske pas.
>
> Kilde: [https://um.dk/spanien/rejse-og-ophold/pas-og-konsulaere-ydelser/pas/bortkommet-eller-stjaalet-pas](https://um.dk/spanien/rejse-og-ophold/pas-og-konsulaere-ydelser/pas/bortkommet-eller-stjaalet-pas)
>
> Dette er uofficiel vejledning. Kontrollér oplysningerne i den officielle kilde.

## Kort vurdering

**Vurdering: delvist bestået; resterende faglig begrænsning/fejl.** Søgningen fandt nu begge pasafsnit, og svaret medtog politianmeldelse, politirapport, fotos, ansøgningsskema og provisorisk pas. Telefonmuligheden blev knyttet til Madrid med efterfølgende afhentning og blev ikke et selvstændigt obligatorisk trin.

Der er fortsat problemer: Kilden siger, at telefonisk anmeldelse i Madrid kan ske på engelsk; svaret udelader sproget og tilføjer den uklare betingelse “i visse tilfælde”. Svaret siger, at skemaet kan downloades “via linket herunder”, men linket er til oversigtssiden om mistet pas, ikke det konkrete download. Det formulerer også medbringelse af det udfyldte skema som et dokumentkrav, selv om det viste afsnit kun udtrykkeligt siger, at skemaet skal udfyldes. Gebyrtrinnet fortolker et link til gebyrsatser som et ubetinget betalingskrav; ingen sats eller betalingsprocedure blev hentet. Det er derfor ikke tilstrækkeligt at erklære svaret korrekt, selv om de vigtigste trin er med.

Resultatet er bevaret uændret. Prompten og bedre retrieval reducerer fejl, men garanterer ikke kildefasthed. En næste forbedring er en kontrol af hver faktuel påstand mod kildeafsnittet og en mere præcis kildehenvisning pr. trin. Den kontrol er ikke implementeret her.

[Fuld trace med alle returnerede kildetekster](raw/02-passport.json)
