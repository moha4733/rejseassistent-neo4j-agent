# Opsætning og genskabelse

## Forudsætninger

Den afleverede løsning er afprøvet på en MacBook Air M1, 8 GB RAM, med Docker Desktop, n8n 2.45.7, Neo4j Desktop 2026.09.0 (Enterprise/Cypher 25), Ollama 0.40.0 og Python 3. Python-scripts bruger kun standardbiblioteket.

Neo4j-querysyntaksen `SEARCH ... VECTOR INDEX` kræver en kompatibel nyere Neo4j-version. En ældre Neo4j 5-installation kan ikke forventes at køre disse forespørgsler uændret. Brug en tom projektdatabase; scripts sletter ikke en eksisterende database. Snapshot-gendannelse er afgrænset til Spanien.

## 1. Start tjenesterne

Opret og start en database `rejseassistent` i Neo4j Desktop. HTTP Query API v2 skal kunne nås på `http://localhost:7474/db/rejseassistent/query/v2`. Notér din egen bruger/adgangskode.

Installer Ollama fra den officielle distribution og kør:

```sh
ollama pull nomic-embed-text
ollama serve
```

Hvis Ollama allerede kører som app, skal du ikke starte en ekstra server. `ollama show nomic-embed-text` kontrollerer installationen. Modellen skal være den samme ved dokument- og spørgsmåls-embeddings; et modelskift kræver nye dokumentvektorer og eventuelt et nyt indeks.

Start n8n med den medfølgende [compose.yml](../compose.yml):

```sh
docker compose up -d
```

Åbn `http://localhost:5678` og opret den lokale n8n-bruger. Denne compose-fil indeholder kun n8n; Neo4j og Ollama kører på værtsmaskinen. Fra n8n-containeren bruges `host.docker.internal:7474` og `host.docker.internal:11434`. Fra Python på værten bruges `localhost`. På andre platforme skal adresser og de to tjenesters lytteadresser tilpasses. Eksponér ikke tjenesterne offentligt.

## 2. Genskab den afleverede database deterministisk

I repoets rod, sæt dine egne miljøvariabler. Indtast adgangskoden lokalt; commit aldrig `.env` eller credentials.

```sh
export NEO4J_URL=http://localhost:7474
export NEO4J_DATABASE=rejseassistent
export NEO4J_USER=neo4j
read -s NEO4J_PASSWORD
export NEO4J_PASSWORD
python3 scripts/restore_snapshot.py
```

`read -s`-eksemplet er til Mac/zsh/bash. Scriptet opretter fire unikke constraints, indlæser dokumenter, chunks med de faktiske 768-dimensionelle vektorer og ambassadegrafen, opretter cosine-indekset og venter på `ONLINE`. Kør det kun mod den ønskede projektdatabase. Det kan genkøres uden dubletter. Snapshot indeholder offentlig kildetekst og er ikke en ny indsamling.

Kontrollér:

```sh
python3 scripts/validate_project.py --live
python3 scripts/check_retrieval.py --country Spanien --question 'Jeg har mistet mit pas. Hvad skal jeg gøre?'
python3 scripts/check_retrieval.py --country Japan --question 'Jeg har mistet mit pas. Hvad skal jeg gøre?'
```

Forvent 3 Document, 20 Chunk, 1 Country og 1 Embassy, 25 relationer, fire unikke constraints og online `chunk_embedding`. Spanien-pastesten skal indeholde begge pas-chunks; Japan skal have `found=false`. Scriptet er en retrievaltest, ikke et kunstigt agentsvar.

## 3. Importér de tre n8n-workflows

Importér hver JSON-fil i [workflows](../workflows/) via n8n-menuen **Import from File**. De tre filer er renset for secrets og eksporteret med `active=false` og uden pin-data.

Opret én **Basic Auth** credential med dine Neo4j-loginoplysninger. Vælg den i Neo4j HTTP-noden i hvert workflow. `REPLACE_WITH_YOUR_CREDENTIAL_ID` er en markør, ikke en fungerende credential. Kontrollér database-URL, hvis din database hedder noget andet.

- `01-data-ingestion.json`: manuel trigger. Kan genindsamle de tre sider, normalisere, beregne embeddings og oprette hele grafen. Kør først `python3 scripts/setup_database.py`, hvis du starter uden snapshot. Klik **Execute workflow**. Slutnoden skal vise `status=success` og antallet af importerede chunks. Nye websider kan give et andet chunkantal end snapshottet. Det er forventet.
- `02-graph-retrieval.json`: triggeren **When Executed by Another Workflow**, input `country` som String. Test med `{"country":"Spanien"}` og Japan. Spanien skal give ét ambassaderesultat.
- `03-vector-retrieval.json`: samme trigger, input `country` og `question`, begge String. Test med de to lande. Begge workflows skal **publiceres**, før en publiceret agent kan kalde dem.

**Vigtigt inputproblem fra udviklingen:** Triggeren bruger eksplicit **Define using JSON example**. Gem og publicér triggerens inputskema. Hvis agentens Advanced → Workflow inputs siger “no defined inputs”, genvælg workflowet efter publicering. Et tomt `{}` som tool input er en konfigurationsfejl, ikke et bevis på manglende kilder.

## 4. Genskab agenten i n8n Agents

Opret en agent i **Overview → Agents**. Dette er Agents-builderen, ikke blot AI Agent-noden i et workflow.

1. Navn: `Rejseassistent – Spanien`. Vælg Google Gemini med din egen API-key i en n8n credential. Vælg **Gemini 3.1 Flash Lite** (`google/gemini-3.1-flash-lite`) som i testene, hvis tilgængelig for din konto. En anden model kræver nye testresultater; modeltilgængelighed og kvoter kan ændre sig.
2. Kopiér [instructions.txt](../agent/instructions.txt) til Instructions.
3. Under Capabilities → Add workflow tilknyttes de to importerede værktøjer. Kopiér de fulde beskrivelser fra [tool-1-description.txt](../agent/tool-1-description.txt) og [tool-2-description.txt](../agent/tool-2-description.txt).
4. Under Advanced → Workflow inputs: vælg **Defined by the agent** for `country`; på søgeværktøjet også `question`. Kopiér inputbeskrivelserne fra tekstfilerne. Indtast ikke permanent “Spanien” som input.
5. Return all node outputs: Off. Require approval: Off (værktøjerne foretager læseopslag). Web search: Off. Cross-session memory: Off. n8n Chat: On. Ingen særskilte skills eller Knowledge-tab.
6. Test agenten og publicér den. Hvis importerede workflow-ID'er ændres, vælg de nye workflows i UI. `configuration.json` er en læsbar specifikation, ikke en automatisk agentimport.

## 5. Gentag de tre agenttests

Start en **ny session for hvert spørgsmål**, så tidligere landeoplysninger ikke påvirker resultatet:

- `Hvad er adressen på Danmarks ambassade i Spanien?`
- `Jeg har mistet mit pas i Spanien. Hvad skal jeg gøre?`
- `Jeg har mistet mit pas i Japan. Hvad skal jeg gøre?`

Udvid tool calls og kontrollér input, land, kilde og output. Gem det faktiske agentsvar, også hvis det er forkert. Sammenlign med [afleveringens vurderinger](../examples/RESULTS.md). Et andet svar er muligt selv med samme opsætning.

Ved “high demand”, kvotefejl eller DNS-fejl skal der vises en teknisk fejl, ikke opfindes et fagligt svar. Kontrollér først den konkrete fejlede node og tool input. Den endelige Agents-konfiguration sætter ikke temperatur eller tokenbudget eksplicit; providerens standarder anvendes. De tidligere Ollama-parametre er ikke Gemini-agentens indstillinger. Vores tidligere fejl i disse kategorier beskrives i evalueringen.
