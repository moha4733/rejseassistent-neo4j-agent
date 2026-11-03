# Tre eksempelspørgsmål og resultater

Kørt den 3. november 2026 i **n8n Agents** med **Gemini 3.1 Flash Lite**, de to workflowværktøjer og den gemte Spanien-database. Hvert af de tre spørgsmål blev startet i en ny session. Resultaterne nedenfor er faktiske agentsvar og værktøjsresultater, ikke håndskrevne idealsvar. Kildeteksterne er indsamlede snapshots; dette er en evaluering af prototypen, ikke aktuel rejserådgivning.

| Case | Spørgsmål | Opslag | Vurdering |
|---|---|---|---|
| [1. Ambassadeadresse](01-address.md) | Hvad er adressen på Danmarks ambassade i Spanien? | Grafopslag, ét resultat | Bestået for overensstemmelse med den gemte adresse og kilde |
| [2. Mistet pas](02-passport.md) | Jeg har mistet mit pas i Spanien. Hvad skal jeg gøre? | Vektor + emneprioritering + nabochunks, fem afsnit | Delvist bestået; svar overfortolker bl.a. gebyrhenvisning og skemaets aflevering |
| [3. Japan uden data](03-japan.md) | Jeg har mistet mit pas i Japan. Hvad skal jeg gøre? | Tekstsøgning og grafopslag, begge uden resultat | Landefilter bestået; ingen Spanien-oplysninger brugt |

Hver case indeholder input til værktøjerne, hentede oplysninger, det fulde faktiske svar og en kort kritisk vurdering. [JSON-traces](raw/) indeholder de fulde returnerede tekster og kilde-URL’er. Sporene er renset til relevante hændelser; credentials, interne providersignaturer og private samtaler er udeladt.

## Dokumenteret fejl og udviklingsforløb

[Fejl før retrievalrettelsen](04-retrieval-failure-before-fix.md) viser samme passpørgsmål med syv generelle afsnit og et utilstrækkeligt svar. Den er medtaget, så begrundelsen for emneprioriteringen kan efterprøves. Case 2 viser, at bedre kilder forbedrede svaret, men ikke fjernede alle fejl.

Andre tekniske problemer under udviklingen:

- Værktøjskald blev sendt med `{}`, fordi agenten ikke læste det implicitte inputskema. Triggerne fik et eksplicit JSON-example-skema og agentstyrede inputfelter. Den aktuelle adressetest viser `country=Spanien`; Japantesten viser `country=Japan`.
- En Gemini-model svarede med “high demand”, og en tidligere kørsel fejlede ved DNS-opslag. Det er driftsfejl, som skal skelnes fra et legitimt tomt søgeresultat.
- De lokale Qwen/Llama-forsøg havde problemer med instruktionsefterlevelse, gentagelser og kildebrug. De er udviklingsobservationer, ikke en systematisk sammenligning med den endelige model.

## Begrænsninger i evalueringen

Tre cases er en demonstration, ikke et statistisk benchmark. De tester grafopslag, et konkret tekstbehov og afvisning af et land uden data. Vi har ikke målt generel præcision/recall på mange spørgsmål, robusthed mod alle prompt-injektioner eller opdateringsforsinkelse. Modellen kan stadig fortolke et link som et krav. `found=true` og en høj score bekræfter ikke svarets korrekthed. Derfor er løsningen tydeligt mærket som en uofficiel studieprototype.
