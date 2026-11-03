# Arkitektur og datamodel

## Arbejdsdeling

Agenten er samtale- og beslutningslaget: den afklarer land, vælger værktøj og formulerer et svar. n8n-workflows udfører de kontrollerede databaseforespørgsler. Neo4j opbevarer både relationer og tekstvektorer. Gemini genererer svar eksternt; Ollama beregner embeddings lokalt. Brugerens testspørgsmål og hentede tekster sendes derfor til Gemini. Testene indeholder ingen pasnumre eller andre følsomme identitetsoplysninger.

## Noder, relationer og egenskaber

| Node | Antal | Nøgle og egenskaber |
|---|---:|---|
| `Country` | 1 | `id=ES`, `name=Spanien` |
| `Embassy` | 1 | `id=dk-madrid`, `name`, `address`, `city`, `source_url`, `retrieved_at` |
| `Document` | 3 | unik `id`, `title`, `country`, `topic`, `publisher`, `source_url`, `retrieved_at` |
| `Chunk` | 20 | unik `id`, `chunk_index`, `text`, `embedding`, `embedding_model`, `embedding_dimensions` |

| Relation | Retning | Antal | Formål |
|---|---|---:|---|
| `ABOUT_COUNTRY` | Document → Country | 3 | Dokumentets geografiske tilknytning |
| `HAS_CHUNK` | Document → Chunk | 20 | Kildetilhørsforhold og rækkefølge |
| `DOCUMENTS` | Document → Embassy | 1 | Kilden til ambassadeoplysningerne |
| `LOCATED_IN` | Embassy → Country | 1 | Grafopslag efter land |

Der er ingen relationsegenskaber. `retrieved_at` er indsamlingstid, ikke sidens opdateringsdato. Kildedokumentets metadata gentages i retrievalresultatet, så modellen kan se land og kilde for hver chunk. `score` kan være null for et naboafsnit, der blev hentet gennem grafrelationen.

## Dataimport

Workflowets rækkefølge er: manuel trigger → Kildeliste → HTTP GET → HTML → tekstnormalisering → Edit Fields → chunking → embedding → samling → Neo4j → kontrol.

- Tre eksplicit valgte offentlige sider; metadata og stabile ID'er er defineret i Kildeliste.
- HTML udtrækker `h1` og `body`; script/style/nav/header/footer/noscript udelades. Whitespace normaliseres, og indledende støj før titlen fjernes.
- Chunkstørrelse 800 tegn, overlap 150 tegn, ordgrænser og `chunk_index`. Overlap kan fortsat dele sætninger; naboopslag afhjælper dette.
- Embeddingmodel `nomic-embed-text`, `search_document: ` på dokumenter og `search_query: ` på spørgsmål. 768 dimensioner, cosine-indeks.
- Ambassadens navn, ID og by er en kontrolleret normalisering for denne case. Adressen udtrækkes med et eksplicit regex fra kontaktsiden. Importen fejler, hvis adressens kendte format ikke findes. Denne parser skal ændres ved andre landes sideformater; den er ikke en universel ambassadeparser.
- `MERGE` og unikke ID'er forhindrer dubletter. Ved kortere nye dokumenter fjernes gamle chunks med indeks uden for det nye antal. Der er ikke fuld historik eller automatisk oprydning af helt fjernede kilder.

## Grafopslag

[graph-retrieval.cypher](../neo4j/graph-retrieval.cypher) følger `Document-[:DOCUMENTS]->Embassy-[:LOCATED_IN]->Country`, sammenligner land uden forskel på store/små bogstaver og returnerer adresse med kilde. Brugertekst sendes som en parameter, ikke som genereret Cypher. Et tomt resultat giver `found=false`; det betyder ikke, at en ambassade ikke eksisterer.

## Vektorsøgning med emneprioritering og naboer

[vector-retrieval.cypher](../neo4j/vector-retrieval.cypher) henter de 20 bedste vektorkandidater, filtrerer på dokumentets land og udvælger tre seeds. Hvis spørgsmålet indeholder `pas` samt et udtryk for mistet/stjålet/bortkommet, gives dokumenter med `topic=mistet_pas` et tillæg på 0,25 i udvælgelsen. Det er en transparent, håndskrevet regel til denne case. Den opfinder ikke svar og bruger ikke faste chunk-ID'er.

Hvert seed udvides til naboer med indeksafstand højst én i samme dokument. Dubletter samles, og kildenumre tildeles efter den endelige rækkefølge. Dermed kan et pasafsnit hente fortsættelsen om ansøgningsskemaet. Resultatet indeholder `score`, `selection_score`, `retrieved_via`, `source_url`, land og indsamlingsdato. En udvælgelsesscore over 1 skyldes emnetillægget og er **ikke** en sandsynlighed eller sikkerhedsvurdering.

Landefilteret er hårdt: Japan må ikke modtage Spanien-chunks. Kandidatgrænsen gælder før landefilteret; ved et stort datasæt kan andre lande stadig skubbe relevante kandidater ud. En større løsning bør bruge mere effektiv geografisk afgrænsning og evaluere recall pr. land. Der er heller ingen kalibreret relevanstærskel: `found=true` betyder, at der findes kandidater, ikke at de besvarer spørgsmålet.

## Afgrænsning

Ingen vægttræning, særskilte skills, ekstra agenter eller human approval-workflows er anvendt. Web search og cross-session memory er slået fra; almindelig sessionshukommelse er slået til. Knowledge-tabben bruges ikke. Valget gør de to Neo4j-værktøjer synlige og efterprøvelige.
